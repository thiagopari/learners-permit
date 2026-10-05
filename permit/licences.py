"""Licences: the AI may command a skill only after evaluation proves it, only within the scope that was
tested, and only until live results slip. The proof is Hyperion's commissioning gate (cell/bandit.py).
"""
import json
import os
import time

from cell.bandit import CONF, commission, p_at_least

# thr: success rate to license at. cap: trial cap (cap 40 licensed a true-90% policy only ~56% of the time; 100
# does ~92%). min_trials: no early fail before this many (the 99% prior starts below 1 - CONF).
# revoke_below: revoke once the live window is confident the rate is below this. Simulated over 200 live runs
# (window 20, min 8): 0.70 never revoked a 92% skill (2% for an 85% one), and 0.95 revoked a 99.5% skill 0.5% of
# the time; both caught a broken skill in 8 runs. Revoking at the licensing bar itself wrongly revoked 3% and 63%.
TIERS = {"supervised": {"thr": 0.80, "cap": 100, "min_trials": 0, "revoke_below": 0.70},
         "unattended": {"thr": 0.99, "cap": 400, "min_trials": 20, "revoke_below": 0.95}}
LIVE_WINDOW, LIVE_MIN = 20, 8


def _load(path):
    return json.load(open(path)) if os.path.exists(path) else {}


def _save(path, data):
    """Write, then rename: a crash or a spot preemption mid-write leaves the old file, never a truncated one."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path + ".tmp", "w") as f:
        json.dump(data, f, indent=1)
        f.flush()
        os.fsync(f.fileno())
    os.replace(path + ".tmp", path)


class Licences:
    def __init__(self, path):
        self.path = path
        self.data = _load(path)
        # Sweeps a crash interrupted, checkpointed after every batch. Each RoboLab batch is 10-20 GPU minutes.
        self.sweeps_path = os.path.join(os.path.dirname(path), "sweeps.json")
        self.sweeps = _load(self.sweeps_path)

    def save(self):
        _save(self.path, self.data)

    @staticmethod
    def sweep_key(skill, arms, tier, scope, source):
        """A resume is only valid for the same skill, arms, tier, scope and runner (never mock trials into a real sweep)."""
        return json.dumps([skill, sorted(arms), tier, scope or {}, source], sort_keys=True)

    def commission(self, skill, arms, run_batch, tier="supervised", scope=None, batch=4, on_batch=None,
                   source="mock", resume=None):
        """resume: None refuses if this sweep was interrupted, True continues it, False discards it. Resuming is a
        person's call: if an arm's checkpoint changed since the crash, continuing would mix two policies' trials."""
        t = TIERS[tier]
        key = self.sweep_key(skill, arms, tier, scope, source)
        prog = self.sweeps.get(key)
        if prog and resume is None:
            raise ValueError(f"{skill}: a sweep was interrupted after {len(prog['log'])} batches; "
                             "pass resume=true to continue it or resume=false to start over")
        if prog and resume is False:  # drop it now, so a crash in the first new batch can't bring it back
            self.sweeps.pop(key)
            _save(self.sweeps_path, self.sweeps)
            prog = None
        if not prog:
            prog = {"successes": dict.fromkeys(arms, 0), "failures": dict.fromkeys(arms, 0), "log": [], "resumed": 0}
        start = prog if prog["log"] else None
        if start:
            prog["resumed"] += 1

        def checkpoint(entry):
            for arm, outcomes in entry["ran"].items():
                prog["successes"][arm] += sum(outcomes)
                prog["failures"][arm] += len(outcomes) - sum(outcomes)
            prog["log"].append(entry)
            self.sweeps[key] = prog
            _save(self.sweeps_path, self.sweeps)
            if on_batch:
                on_batch(entry)
        res = commission(list(arms), run_batch, thr=t["thr"], batch=batch, max_trials=t["cap"],
                         min_trials=t["min_trials"], on_batch=checkpoint, start=start)
        if self.sweeps.pop(key, None) is not None:
            _save(self.sweeps_path, self.sweeps)
        s, f = res["successes"], res["failures"]
        best = res.get("policy") or max(arms, key=lambda a: p_at_least(s[a], f[a], t["thr"]))
        lic = {"status": "licensed" if res["decision"] == "pass" else "refused", "decision": res["decision"],
               "tier": tier, "thr": t["thr"], "revoke_below": t["revoke_below"], "policy": best,
               "successes": s[best], "trials": s[best] + f[best], "p": round(p_at_least(s[best], f[best], t["thr"]), 4),
               "scope": scope or {}, "issued": time.strftime("%Y-%m-%d %H:%M:%S"), "live": [],
               "log": [e["line"] for e in res["log"]], "resumed": prog["resumed"]}
        self.data[skill] = lic
        self.save()
        return lic

    def covers(self, skill, conditions):
        """Licensed, and every scoped condition of the request (e.g. speed) is one that was tested."""
        lic = self.data.get(skill)
        if not lic or lic["status"] != "licensed":
            return False
        return all(conditions.get(k) in (v if isinstance(v, list) else [v]) for k, v in lic["scope"].items())

    def record_live(self, skill, ok):
        """Live results can only narrow: revoke once the recent window is confident the rate is below revoke_below."""
        lic = self.data.get(skill)
        if not lic or lic["status"] != "licensed":
            return lic
        lic["live"] = (lic["live"] + [int(ok)])[-LIVE_WINDOW:]
        s, n = sum(lic["live"]), len(lic["live"])
        if n >= LIVE_MIN and p_at_least(s, n - s, lic["revoke_below"]) <= 1 - CONF:
            lic.update(status="revoked", reason=f"live results slipped: {s}/{n} successes in the last {n} runs")
        self.save()
        return lic
