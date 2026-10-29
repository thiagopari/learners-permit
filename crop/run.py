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


def commission(licences, crop, record, client=None, data=leaf.DATA, predict=None, model_id=leaf.MODEL):
    rb = leaf.runner(crop, record, client=client, data=data, predict=predict, workers=1 if predict else 8)
    t0 = time.time()
    kind = "trained" if predict else "fewshot"
    skill, scope, source = f"{SKILL}:{crop}", {"crop": [crop]}, f"plantvillage-{kind}:{model_id}"
    # One crop per licence: the crop is the scope, and the sweep's key, so crops never share trials.
    try:
        lic = licences.commission(skill, [model_id], rb, batch=10, scope=scope, source=source, resume=False)
    except leaf.OutOfPhotos:  # the gate couldn't decide on the photos we have: report that, unlicensed
        prog = licences.sweeps[licences.sweep_key(skill, [model_id], "supervised", scope, source)]
        s, f = prog["successes"][model_id], prog["failures"][model_id]
        from permit.gate import prob_rate_at_least
        lic = {"status": "undecided (ran out of labelled photos)", "successes": s, "trials": s + f,
               "p": round(prob_rate_at_least(s, f, 0.8), 4), "scope": scope}
    if lic.get("decision") == "inconclusive":  # the licence store files it as "refused"; say exactly what happened
        lic = {**lic, "status": f"not licensed (undecided after {lic['trials']} photos)"}
    lic["minutes"] = round((time.time() - t0) / 60, 1)
    return lic


def main(out=None, client=None, data=leaf.DATA, predict=None, model_id=leaf.MODEL, meta=None):
    envfile.load()
    kind = "trained" if predict else "fewshot"
    default = f"crop-{time.strftime('%Y-%m-%d')}" + ("-trained" if predict else "")
    out = pathlib.Path(out or ROOT / "docs" / "results" / default)
    out.mkdir(parents=True, exist_ok=True)
    licences = Licences(str(out / "licences.json"))
    preds = open(out / "predictions.jsonl", "w")

    def record(row):
        preds.write(json.dumps(row) + "\n"); preds.flush()

    summary = {"model": model_id, "kind": kind, "crops": {}}
    if kind == "fewshot":
        summary["few_shot"] = "one verified reference leaf per diagnosis"
    if meta:
        summary["training"] = meta
    for crop in leaf.CROPS:
        lic = commission(licences, crop, record, client=client, data=data, predict=predict, model_id=model_id)
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
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--trained", help="a model.pt from crop/train.py, instead of the few-shot vision model")
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.trained:
        import hashlib
        sha = hashlib.sha256(pathlib.Path(a.trained).read_bytes()).hexdigest()
        meta_path = pathlib.Path(a.trained).with_name("training_meta.json")
        meta = json.load(open(meta_path)) if meta_path.exists() else None
        # The model's hash is its identity: a retrained model is a different arm and must earn its own licence.
        main(out=a.out, predict=leaf.trained(a.trained), model_id=f"resnet18-plantvillage:{sha[:12]}", meta=meta)
    else:
        main(out=a.out)
