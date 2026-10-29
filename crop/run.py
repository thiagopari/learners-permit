"""Commission the leaf-diagnosis skill for each crop on real labelled photos, then show what the licence allows.

    python crop/run.py            (needs NEBIUS_API_KEY in .env, and data/plantvillage from the manifest)

Writes docs/results/crop-<date>/: every prediction (predictions.jsonl), the licences (licences.json) and a summary.
"""
import json
import os
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from crop import leaf  # noqa: E402
from permit import envfile  # noqa: E402
from permit.licences import Licences  # noqa: E402

SKILL = "diagnose_leaf"


def commission(licences, crop, record, client=None, data=leaf.DATA):
    rb = leaf.runner(crop, record, client=client, data=data)
    t0 = time.time()
    skill, scope, source = f"{SKILL}:{crop}", {"crop": [crop]}, f"plantvillage-fewshot:{leaf.MODEL}"
    # One crop per licence: the crop is the scope, and the sweep's key, so crops never share trials.
    try:
        lic = licences.commission(skill, [leaf.MODEL], rb, batch=10, scope=scope, source=source, resume=False)
    except leaf.OutOfPhotos:  # the gate couldn't decide on the photos we have: report that, unlicensed
        prog = licences.sweeps[licences.sweep_key(skill, [leaf.MODEL], "supervised", scope, source)]
        s, f = prog["successes"][leaf.MODEL], prog["failures"][leaf.MODEL]
        from permit.gate import prob_rate_at_least
        lic = {"status": "undecided (ran out of labelled photos)", "successes": s, "trials": s + f,
               "p": round(prob_rate_at_least(s, f, 0.8), 4), "scope": scope}
    if lic.get("decision") == "inconclusive":  # the licence store files it as "refused"; say exactly what happened
        lic = {**lic, "status": f"not licensed (undecided after {lic['trials']} photos)"}
    lic["minutes"] = round((time.time() - t0) / 60, 1)
    return lic


def main(out=None, client=None, data=leaf.DATA):
    envfile.load()
    out = pathlib.Path(out or ROOT / "docs" / "results" / f"crop-{time.strftime('%Y-%m-%d')}")
    out.mkdir(parents=True, exist_ok=True)
    licences = Licences(str(out / "licences.json"))
    preds = open(out / "predictions.jsonl", "w")

    def record(row):
        preds.write(json.dumps(row) + "\n"); preds.flush()

    summary = {"model": leaf.MODEL, "few_shot": "one verified reference leaf per diagnosis", "crops": {}}
    for crop in leaf.CROPS:
        lic = commission(licences, crop, record, client=client, data=data)
        summary["crops"][crop] = {k: lic[k] for k in ("status", "successes", "trials", "p", "scope", "minutes")}
        print(f"{crop}: {lic['status'].upper()} on {lic['successes']}/{lic['trials']} labelled photos, "
              f"P(accuracy >= 80%) = {lic['p']}  ({lic['minutes']} min)", flush=True)
    # The scope, checked the way the control plane checks it: a licence covers only the crop it was earned on.
    summary["scope_checks"] = {f"{held} licence covers {asked}": licences.covers(f"{SKILL}:{held}", {"crop": asked})
                               for held in leaf.CROPS for asked in leaf.CROPS}
    json.dump(summary, open(out / "summary.json", "w"), indent=1)
    print(json.dumps(summary["scope_checks"], indent=1))
    return summary


if __name__ == "__main__":
    main()
