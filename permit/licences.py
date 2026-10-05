"""Licences: the AI may command a skill only after evaluation proves it, only within the scope that was
tested, and only until live results slip. The proof is Hyperion's commissioning gate (cell/bandit.py), unchanged.
"""
import json
import os
import time

from cell.bandit import CONF, commission, p_at_least

# tier -> (success-rate threshold, trial cap). 99% needs ~298 straight successes, hence the bigger cap.
# Cap 40 licensed a true-90% policy only ~56% of the time; cap 100 does it ~92% (see docs/PLAN.md).
TIERS = {"supervised": (0.80, 100), "unattended": (0.99, 400)}
LIVE_WINDOW, LIVE_MIN = 20, 8  # revoke only on >= 8 live runs: one early miss must not kill a 92% skill


class Licences:
    def __init__(self, path):
        self.path = path
        self.data = json.load(open(path)) if os.path.exists(path) else {}

    def save(self):
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=1)

    def commission(self, skill, arms, run_batch, tier="supervised", scope=None, on_batch=None):
        thr, cap = TIERS[tier]
        res = commission(list(arms), run_batch, thr=thr, max_trials=cap, on_batch=on_batch)
        s, f = res["successes"], res["failures"]
        best = res.get("policy") or max(arms, key=lambda a: p_at_least(s[a], f[a], thr))
        lic = {"status": "licensed" if res["decision"] == "pass" else "refused", "decision": res["decision"],
               "tier": tier, "thr": thr, "policy": best, "successes": s[best], "trials": s[best] + f[best],
               "p": round(p_at_least(s[best], f[best], thr), 4), "scope": scope or {},
               "issued": time.strftime("%Y-%m-%d %H:%M:%S"), "live": [], "log": [e["line"] for e in res["log"]]}
        self.data[skill] = lic
        self.save()
        return lic

    def covers(self, skill, args):
        """Licensed, and every scoped key (e.g. colour) in the request is one that was tested."""
        lic = self.data.get(skill)
        if not lic or lic["status"] != "licensed":
            return False
        return all(args.get(k) in (v if isinstance(v, list) else [v]) for k, v in lic["scope"].items())

    def record_live(self, skill, ok):
        """Live results can only narrow: once the recent window gives P(rate >= thr) <= 1 - CONF, revoke."""
        lic = self.data.get(skill)
        if not lic or lic["status"] != "licensed":
            return lic
        lic["live"] = (lic["live"] + [int(ok)])[-LIVE_WINDOW:]
        s, n = sum(lic["live"]), len(lic["live"])
        if n >= LIVE_MIN and p_at_least(s, n - s, lic["thr"]) <= 1 - CONF:
            lic.update(status="revoked", reason=f"live results slipped: {s}/{n} successes in the last {n} runs")
        self.save()
        return lic
