"""Learner's Permit control plane: the single path from any request to the robot.

  POST /orders     {"text"}                       a person's order -> Nemotron plan -> each call runs as the AI agent
  POST /agent/run  {"skill","args","approval"}    retry one AI command, e.g. with a supervisor's approval token
  POST /run        {"skill","args"}               a person commands directly, under their own role
  POST /approvals  {"skill","args"}               supervisor: single-use token bound to that exact command
  POST /commission {"skill","arms","tier"}        supervisor: run the gate, then issue or refuse a licence
  POST /perturb    {"skill","arm","rate"}         supervisor, mock runner only: change a true success rate (demo)
  POST /sensors    {"human_in_zone"}              supervisor: stand-in for the cell's presence sensor
  GET  /  /licences  /audit                       console and state

Callers send "Authorization: Bearer <session token>", and the role comes from that session. The LLM never supplies
identity, approvals or context: execute() fills context from the clock, sensors and the licence store.
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


def command_hash(skill, args):
    return hashlib.sha256(json.dumps({"skill": skill, "args": args}, sort_keys=True).encode()).hexdigest()[:16]


class Permit:
    def __init__(self, data_dir=os.path.join(ROOT, "data"), runner="mock", plan=None, check_part=None,
                 clock=time.localtime, mock_delay=0.0):
        self.skills = json.load(open(os.path.join(ROOT, "skills.json")))
        self.licences = licences.Licences(os.path.join(data_dir, "licences.json"))
        self.audit_path = os.path.join(data_dir, "audit.jsonl")
        self.rates = {k: dict(v["mock_rates"]) for k, v in self.skills.items()}
        self.runner, self.mock_delay = runner, mock_delay
        self.plan, self.check_part, self.clock = plan or planner.offline_plan, check_part, clock
        self.sensors = {"human_in_zone": False}
        self.approvals = {}
        self.lock = threading.RLock()

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

    def context(self, skill, args, approver=None):
        s = self.skills[skill]
        ctx = {"object_class": s["object_class"], "bin": s["bin"], "speed_pct": int(args.get("speed_pct", 40)),
               "hour": self.clock().tm_hour, "human_in_zone": bool(self.sensors["human_in_zone"]),
               "skill_licensed": self.licences.covers(skill, args)}
        if approver:
            ctx["approver"] = {"__entity": {"type": "User", "id": approver}}
        return ctx

    def execute(self, user, skill, args, approval=None, requester=None):
        """The choke point. user is authz.AGENT for AI commands, otherwise the session's person."""
        with self.lock:
            if skill not in self.skills:
                return self.log(actor=user, requester=requester, skill=skill, decision="deny", reasons=["unknown skill"])
            args = {k: v for k, v in args.items() if k in planner.ARGS}
            approver = self.redeem(approval, skill, args) if approval else None
            ctx = self.context(skill, args, approver)
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
                result = "success" if self.run_batch(skill)({policy: 1})[policy][0] else "failure"
                self.licences.record_live(skill, result == "success")
            entry = self.log(actor=user, requester=requester, skill=skill, args=args, approver=approver,
                             decision="allow" if ok else "deny", reasons=reasons, context=ctx, datasheet=sheet,
                             result=result, licence=(self.licences.data.get(skill) or {}).get("status", "none"))
            if not ok and user == authz.AGENT:
                entry["escalate"] = {"skill": skill, "args": args, "command_hash": command_hash(skill, args)}
            return entry

    def why(self, user, ctx):
        if user != authz.AGENT:
            return ["outside your role's permissions"]
        checks = [(not ctx["skill_licensed"], "skill not licensed for this request"),
                  (ctx["speed_pct"] > 50, "speed above the AI envelope (50%)"),
                  (not 6 <= ctx["hour"] < 22, "outside the AI's hours (06-22)"),
                  (ctx["human_in_zone"] and ctx["speed_pct"] > 25, "person in the cell: 25% max")]
        return [msg for bad, msg in checks if bad] or ["outside the AI's envelope"]

    def approve(self, user, skill, args):
        if authz.PEOPLE.get(user) != "supervisor":
            raise PermissionError("only a supervisor can approve")
        args = {k: v for k, v in args.items() if k in planner.ARGS}
        token = secrets.token_urlsafe(12)
        self.approvals[token] = {"hash": command_hash(skill, args), "by": user, "expires": time.time() + 600}
        self.log(actor=user, action="approve", skill=skill, args=args, command_hash=command_hash(skill, args))
        return token

    def redeem(self, token, skill, args):
        a = self.approvals.pop(token, None)  # single use: a mismatched attempt burns it too
        if a and a["hash"] == command_hash(skill, args) and time.time() < a["expires"]:
            return a["by"]
        return None

    def commission(self, user, skill, arms=None, tier="supervised"):
        if authz.PEOPLE.get(user) != "supervisor":
            raise PermissionError("only a supervisor can commission")
        with self.lock:
            arms = arms or list(self.skills[skill]["arms"])
            lic = self.licences.commission(skill, arms, self.run_batch(skill), tier=tier)
            self.log(actor=user, action="commission", skill=skill, arms=arms, tier=tier, status=lic["status"],
                     counts=f"{lic['successes']}/{lic['trials']}", p=lic["p"])
            return lic

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
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            supervisor = authz.PEOPLE.get(user) == "supervisor"
            try:
                if self.path == "/orders":
                    return self.reply(200, permit.order(user, body["text"]))
                if self.path == "/run":
                    return self.reply(200, permit.execute(user, body["skill"], body.get("args", {})))
                if self.path == "/agent/run":
                    return self.reply(200, permit.execute(authz.AGENT, body["skill"], body.get("args", {}),
                                                          approval=body.get("approval"), requester=user))
                if self.path == "/approvals":
                    return self.reply(200, {"approval": permit.approve(user, body["skill"], body.get("args", {}))})
                if self.path == "/commission":
                    if not supervisor:
                        raise PermissionError("only a supervisor can commission")
                    threading.Thread(target=permit.commission, daemon=True,
                                     args=(user, body["skill"], body.get("arms"), body.get("tier", "supervised"))).start()
                    return self.reply(202, {"commissioning": body["skill"]})
                if self.path == "/perturb" and supervisor and permit.runner == "mock":
                    permit.rates[body["skill"]][body["arm"]] = float(body["rate"])
                    return self.reply(200, permit.rates[body["skill"]])
                if self.path == "/sensors" and supervisor:
                    permit.sensors["human_in_zone"] = bool(body["human_in_zone"])
                    return self.reply(200, permit.sensors)
            except PermissionError as e:
                return self.reply(403, {"error": str(e)})
            except KeyError as e:
                return self.reply(400, {"error": f"missing field {e}"})
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
                 mock_delay=0.3 if a.runner == "mock" else 0.0), a.port)
