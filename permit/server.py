"""Learner's Permit control plane: the single path from any request to the robot.

  POST /orders     {"text"}                           a person's order -> Nemotron plan -> each call runs as the AI
  POST /agent/run  {"skill","args","approval"}        retry one AI command for you, e.g. with a supervisor's approval
  POST /run        {"skill","args"}                   a person commands directly, under their own role
                   (both also take "repeat": n episodes under one decision, so a sim shift doesn't boot Isaac n times)
  POST /approvals  {"skill","args","for","repeat"}    supervisor: single-use token bound to that exact command + person
  POST /commission {"skill","arms","tier","scope"}    supervisor: run the gate, then issue or refuse a licence
                                                     (409 if a crash interrupted that sweep: resend with "resume")
  POST /perturb    {"skill","arm","rate"}             supervisor, mock runner only: change a true success rate (demo)
  POST /sensors    {"human_in_zone"}                  supervisor: stand-in for the cell's presence sensor
  GET  /  /licences  /audit                           console and state

Callers send "Authorization: Bearer <session token>", and the role comes from that session. The LLM never supplies
identity, approvals or context: execute() fills context from the clock, sensors, sessions and the licence store.
"""
import hashlib
import json
import os
import secrets
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from permit import authz, datasheet, licences, planner, runners

ROOT = os.path.dirname(os.path.abspath(__file__))
SESSIONS = json.loads(os.environ.get("PERMIT_SESSIONS", '{"demo-sue": "sue", "demo-olga": "olga", "demo-max": "max"}'))
DEFAULT_SPEED = 40  # commissioning runs at this speed, so a default licence covers exactly this speed


def command_hash(skill, args, repeat, requester):
    cmd = {"skill": skill, "args": args, "repeat": repeat, "for": requester}
    return hashlib.sha256(json.dumps(cmd, sort_keys=True).encode()).hexdigest()[:16]


class Permit:
    def __init__(self, data_dir=os.path.join(ROOT, "data"), runner="mock", plan=None, check_part=None,
                 clock=time.localtime, mock_delay=0.0, lock_timeout=5.0):
        self.skills = json.load(open(os.path.join(ROOT, "skills.json")))
        self.licences = licences.Licences(os.path.join(data_dir, "licences.json"))
        self.audit_path = os.path.join(data_dir, "audit.jsonl")
        self.rates = {k: dict(v["mock_rates"]) for k, v in self.skills.items()}
        self.runner, self.mock_delay = runner, mock_delay
        self.batch = 20 if runner == "robolab" else 4  # each RoboLab call boots Isaac Sim: amortize over 20 episodes
        self.plan, self.check_part, self.clock = plan or planner.offline_plan, check_part, clock
        self.sensors = {"human_in_zone": False}
        self.approvals = {}
        self.lock, self.lock_timeout = threading.RLock(), lock_timeout  # one cell, one command at a time

    def run_batch(self, skill):
        if self.runner == "mock":
            return runners.mock(self.rates[skill], self.mock_delay)
        return runners.robolab(self.skills[skill]["robolab_task"], self.skills[skill]["arms"])

    def log(self, **entry):
        entry = {"t": time.strftime("%H:%M:%S"), **entry}
        os.makedirs(os.path.dirname(self.audit_path), exist_ok=True)
        with open(self.audit_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
        return entry

    def context(self, skill, args, requester=None, approver=None):
        s, speed = self.skills[skill], args.get("speed_pct", DEFAULT_SPEED)
        ctx = {"object_class": s["object_class"], "bin": s["bin"], "speed_pct": speed, "hour": self.clock().tm_hour,
               "human_in_zone": bool(self.sensors["human_in_zone"]),
               "skill_licensed": self.licences.covers(skill, {"speed_pct": speed})}
        if authz.PEOPLE.get(requester):
            ctx["requester_role"] = authz.PEOPLE[requester]
        if approver:
            ctx["approver"] = {"__entity": {"type": "User", "id": approver}}
        return ctx

    def execute(self, user, skill, args, approval=None, requester=None, repeat=1):
        """The choke point. user is authz.AGENT for AI commands (requester = the person it acts for), otherwise the
        session's person. A busy cell denies instead of queueing, so a timed-out caller never executes later."""
        if not self.lock.acquire(timeout=self.lock_timeout):
            return self.log(actor=user, requester=requester, skill=skill, decision="deny", reasons=["cell busy"])
        try:
            return self._execute(user, skill, args, approval, requester, repeat)
        finally:
            self.lock.release()

    def _execute(self, user, skill, args, approval, requester, repeat):
        deny = dict(actor=user, requester=requester, skill=skill, decision="deny")
        if skill not in self.skills:
            return self.log(**deny, reasons=["unknown skill"])
        args = {k: v for k, v in args.items() if k in planner.ARGS}
        speed = args.get("speed_pct", DEFAULT_SPEED)
        if type(speed) is not int or not 5 <= speed <= 100 or type(repeat) is not int or not 1 <= repeat <= 100:
            return self.log(**deny, args=args, reasons=["invalid speed_pct or repeat"])
        approver = self.redeem(approval, skill, args, repeat, requester) if approval else None
        ctx = self.context(skill, args, requester, approver)
        ok = authz.decide(user, "pick_place", "cell1", ctx)
        reasons = [] if ok else self.why(user, ctx)
        sheet = None
        if ok and args.get("part_number") and self.check_part:
            sheet = self.check_part(args["part_number"], self.skills[skill]["max_mass_kg"])
            if sheet["verdict"] == "block":  # web evidence can only narrow
                ok = False
                reasons.append(f"datasheet: {sheet['mass_kg']} kg > {sheet['limit_kg']} kg limit ({sheet['source']})")
        result = None
        if ok:
            policy = (self.licences.data.get(skill) or {}).get("policy") or next(iter(self.skills[skill]["arms"]))
            try:
                outcomes = self.run_batch(skill)({policy: repeat})[policy]
            except Exception as e:  # a crashed run is logged and counts against the skill
                outcomes, result = [0], f"error: {e}"
            for o in outcomes:  # sim batches only; a real cell would stop at the first revocation
                self.licences.record_live(skill, bool(o))
            if result is None:
                result = ("success" if outcomes[0] else "failure") if repeat == 1 else f"{sum(outcomes)}/{repeat} succeeded"
        entry = self.log(actor=user, requester=requester, skill=skill, args=args, repeat=repeat, approver=approver,
                         decision="allow" if ok else "deny", reasons=reasons, context=ctx, datasheet=sheet,
                         result=result, licence=(self.licences.data.get(skill) or {}).get("status", "none"))
        if not ok and user == authz.AGENT:
            entry["escalate"] = {"skill": skill, "args": args, "repeat": repeat, "for": requester,
                                 "command_hash": command_hash(skill, args, repeat, requester)}
        return entry

    def why(self, user, ctx):
        if user != authz.AGENT:
            return ["outside your role's permissions"]
        checks = [(ctx.get("requester_role") not in ("operator", "supervisor"), "requester's role can't ask the AI"),
                  (not ctx["skill_licensed"], "skill not licensed for this request"),
                  (ctx["speed_pct"] > 50, "speed above the AI envelope (50%)"),
                  (not 6 <= ctx["hour"] < 22, "outside the AI's hours (06-22)"),
                  (ctx["human_in_zone"] and ctx["speed_pct"] > 25, "person in the cell: 25% max")]
        return [msg for bad, msg in checks if bad] or ["outside the AI's envelope"]

    def approve(self, user, skill, args, requester, repeat=1):
        if authz.PEOPLE.get(user) != "supervisor":
            raise PermissionError("only a supervisor can approve")
        if requester not in authz.PEOPLE:
            raise PermissionError("an approval must name the person it is for")
        args = {k: v for k, v in args.items() if k in planner.ARGS}
        token, h = secrets.token_urlsafe(12), command_hash(skill, args, repeat, requester)
        self.approvals[token] = {"hash": h, "by": user, "expires": time.time() + 600}
        self.log(actor=user, action="approve", skill=skill, args=args, repeat=repeat, requester=requester, command_hash=h)
        return token

    def redeem(self, token, skill, args, repeat, requester):
        a = self.approvals.pop(token, None)  # single use: a mismatched attempt burns it too
        if a and a["hash"] == command_hash(skill, args, repeat, requester) and time.time() < a["expires"]:
            return a["by"]
        return None

    def sweep(self, skill, arms=None, tier="supervised", scope=None):
        """The defaults a commission uses, and that sweep's interrupted progress, if any."""
        arms = arms or list(self.skills[skill]["arms"])
        scope = scope or {"speed_pct": [DEFAULT_SPEED]}
        return arms, scope, self.licences.sweeps.get(self.licences.sweep_key(skill, arms, tier, scope, self.runner))

    def commission(self, user, skill, arms=None, tier="supervised", scope=None, resume=None):
        if authz.PEOPLE.get(user) != "supervisor":
            raise PermissionError("only a supervisor can commission")
        if not self.lock.acquire(timeout=self.lock_timeout):
            raise RuntimeError("cell busy")
        try:
            arms, scope, _ = self.sweep(skill, arms, tier, scope)
            lic = self.licences.commission(skill, arms, self.run_batch(skill), tier=tier, batch=self.batch,
                                           scope=scope, source=self.runner, resume=resume)
            self.log(actor=user, action="commission", skill=skill, arms=arms, tier=tier, status=lic["status"],
                     counts=f"{lic['successes']}/{lic['trials']}", p=lic["p"])
            return lic
        except Exception as e:
            self.log(actor=user, action="commission", skill=skill, status="error", reasons=[str(e)])
            raise
        finally:
            self.lock.release()

    def order(self, user, text):
        calls = self.plan(text, self.skills)
        self.log(actor=user, action="order", text=text, plan=calls)
        return [self.execute(authz.AGENT, c["skill"], c["args"], requester=user) for c in calls]


def serve(permit, port):
    console = os.path.join(ROOT, "..", "console", "index.html")

    class Handler(BaseHTTPRequestHandler):
        def reply(self, code, body, ctype="application/json"):
            data = body if isinstance(body, bytes) else json.dumps(body).encode()
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/":
                return self.reply(200, open(console, "rb").read(), "text/html")
            if self.path == "/licences":
                return self.reply(200, permit.licences.data)
            if self.path == "/audit":
                lines = open(permit.audit_path).read().splitlines()[-60:] if os.path.exists(permit.audit_path) else []
                return self.reply(200, [json.loads(line) for line in lines])
            self.reply(404, {"error": "not found"})

        def do_POST(self):
            user = SESSIONS.get(self.headers.get("Authorization", "").removeprefix("Bearer ").strip())
            if not user:
                return self.reply(401, {"error": "send Authorization: Bearer <session token>"})
            supervisor = authz.PEOPLE.get(user) == "supervisor"
            try:
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
                repeat = body.get("repeat", 1)
                if self.path == "/orders":
                    return self.reply(200, permit.order(user, body["text"]))
                if self.path == "/run":
                    return self.reply(200, permit.execute(user, body["skill"], body.get("args", {}), repeat=repeat))
                if self.path == "/agent/run":
                    return self.reply(200, permit.execute(authz.AGENT, body["skill"], body.get("args", {}),
                                                          approval=body.get("approval"), requester=user, repeat=repeat))
                if self.path == "/approvals":
                    token = permit.approve(user, body["skill"], body.get("args", {}), body["for"], repeat)
                    return self.reply(200, {"approval": token})
                if self.path == "/commission":
                    if not supervisor:
                        raise PermissionError("only a supervisor can commission")
                    tier, resume = body.get("tier", "supervised"), body.get("resume")
                    if resume is not None and not isinstance(resume, bool):
                        raise ValueError("resume must be true or false")
                    _, _, interrupted = permit.sweep(body["skill"], body.get("arms"), tier, body.get("scope"))
                    if interrupted and resume is None:
                        return self.reply(409, {"error": f"a sweep of {body['skill']} was interrupted after "
                                                f"{len(interrupted['log'])} batches; resend with \"resume\": true "
                                                "to continue it, or false to start over"})
                    threading.Thread(target=permit.commission, daemon=True,
                                     args=(user, body["skill"], body.get("arms"), tier, body.get("scope"),
                                           resume)).start()
                    return self.reply(202, {"commissioning": body["skill"], "watch": "/licences and /audit"})
                if self.path == "/perturb" and supervisor and permit.runner == "mock":
                    permit.rates[body["skill"]][body["arm"]] = float(body["rate"])
                    return self.reply(200, permit.rates[body["skill"]])
                if self.path == "/sensors" and supervisor:
                    permit.sensors["human_in_zone"] = bool(body["human_in_zone"])
                    return self.reply(200, permit.sensors)
            except PermissionError as e:
                return self.reply(403, {"error": str(e)})
            except (KeyError, ValueError) as e:
                return self.reply(400, {"error": f"bad request: {e}"})
            except Exception as e:  # e.g. the planner's API is down
                return self.reply(502, {"error": str(e)})
            self.reply(404, {"error": "not found or not allowed"})

        def log_message(self, *args):
            pass

    print(f"console: http://127.0.0.1:{port}/")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--runner", choices=["mock", "robolab"], default="mock")
    ap.add_argument("--port", type=int, default=8099)
    a = ap.parse_args()
    llm, web = bool(os.environ.get("NEBIUS_API_KEY")), bool(os.environ.get("TAVILY_API_KEY"))
    print(f"planner: {'Nemotron on Token Factory' if llm else 'offline stand-in (set NEBIUS_API_KEY)'} | "
          f"datasheets: {'Tavily' if web else 'off (set TAVILY_API_KEY)'} | runner: {a.runner}")
    serve(Permit(runner=a.runner, plan=planner.plan if llm else None, check_part=datasheet.check if web else None,
                 mock_delay=0.3 if a.runner == "mock" else 0.0, lock_timeout=5.0 if a.runner == "mock" else 30.0), a.port)
