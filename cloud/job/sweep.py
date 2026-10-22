"""One commissioning sweep inside a Nebius Serverless Job, through the same licence code the control plane uses.

Configured by environment variables (cloud/job.sh run sets them):
  LP_SKILL            skill from permit/skills.json (required)
  LP_ARMS             comma-separated arms to compare (default: all of the skill's arms)
  LP_TIER             supervised | unattended (default supervised)
  LP_SPEEDS           the licence's scope: commanded speeds tested, comma-separated (default 40)
  LP_BACKGROUND_SEED  run in a randomized RoboLab background (the revoke beat's perturbed scene)
  LP_RUNNER           robolab (default) | mock (coin flips at skills.json's rates: test the job without a GPU)
  LP_STATE            where licences.json, sweeps.json and summary.json persist: the bucket's run folder (required)
  LP_USD_PER_HOUR     the job's GPU price, for cost per 1,000 episodes (default 1.80, RTX PRO 6000 on demand)

The checkpoint is written on local disk, then copied to LP_STATE after every batch: renames on a mounted bucket may not
be atomic, and a crash mid-copy must never leave a truncated checkpoint as the only one. A restarted job resumes the
sweep only if the skill, arms, tier, scope, scene and image commit all match (see Licences.sweep_key).

Importing a finished licence into the control plane on the laptop:
    python cloud/job/sweep.py import results/<run_id>/licences.json [permit/data]
"""
import json
import os
import shutil
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from permit import runners  # noqa: E402
from permit.licences import Licences  # noqa: E402

FILES = ("licences.json", "sweeps.json")


def copy_files(src, dst):
    for name in FILES:
        if os.path.exists(os.path.join(src, name)):
            shutil.copyfile(os.path.join(src, name), os.path.join(dst, name + ".part"))
            os.replace(os.path.join(dst, name + ".part"), os.path.join(dst, name))


def config(env):
    skills = json.load(open(os.path.join(ROOT, "permit", "skills.json")))
    skill = env["LP_SKILL"]
    if skill not in skills:
        raise SystemExit(f"unknown skill {skill!r}; known: {', '.join(skills)}")
    spec = skills[skill]
    arms = [a for a in env.get("LP_ARMS", "").split(",") if a] or list(spec["arms"])
    unknown = [a for a in arms if a not in spec["arms"]]
    if unknown:
        raise SystemExit(f"{skill} has no arm {unknown}; known: {', '.join(spec['arms'])}")
    seed = env.get("LP_BACKGROUND_SEED") or None
    return {"skill": skill, "spec": spec, "arms": arms, "tier": env.get("LP_TIER", "supervised"),
            "speeds": [int(s) for s in env.get("LP_SPEEDS", "40").split(",")], "seed": seed,
            "runner": env.get("LP_RUNNER", "robolab"), "state": env["LP_STATE"],
            "usd_per_hour": float(env.get("LP_USD_PER_HOUR", "1.80")), "commit": env.get("LP_COMMIT", "unknown")}


def main(env=os.environ, run_batch=None):
    c = config(env)
    work = tempfile.mkdtemp(prefix="lp-sweep-")
    os.makedirs(c["state"], exist_ok=True)
    copy_files(c["state"], work)  # a restarted job picks up its last checkpoint
    licences = Licences(os.path.join(work, "licences.json"))
    extra = ["--randomize-background", "--background-seed", str(c["seed"])] if c["seed"] else []
    if run_batch is None:
        if c["runner"] == "mock":
            run_batch = runners.mock(c["spec"]["mock_rates"])
        else:
            run_batch = runners.robolab(c["spec"]["robolab_task"], c["spec"]["arms"], extra_args=extra)
    # The image's commit is part of the source, so a sweep never resumes into different code or a different scene.
    source = f"{c['runner']}:job:{c['commit']}" + (f":background_seed={c['seed']}" if c["seed"] else "")
    t0, ran = time.time(), []

    def checkpoint(entry):
        copy_files(work, c["state"])
        ran.append(sum(len(v) for v in entry["ran"].values()))
        print(entry["line"], flush=True)

    lic = licences.commission(c["skill"], c["arms"], run_batch, tier=c["tier"], scope={"speed_pct": c["speeds"]},
                              batch=20 if c["runner"] == "robolab" else 4, on_batch=checkpoint, source=source,
                              resume=True)
    copy_files(work, c["state"])
    seconds = time.time() - t0
    summary = {"skill": c["skill"], "status": lic["status"], "decision": lic["decision"], "tier": lic["tier"],
               "policy": lic["policy"], "successes": lic["successes"], "trials": lic["trials"], "p": lic["p"],
               "scope": lic["scope"], "source": source, "resumed": lic["resumed"], "minutes": round(seconds / 60, 1)}
    summary.update(cost(sum(ran), seconds, c["usd_per_hour"]))
    with open(os.path.join(c["state"], "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps(summary), flush=True)
    return summary


def cost(episodes, seconds, usd_per_hour):
    """Cost per 1,000 episodes for this attempt: its episodes and its sweep time (after weights and server start-up,
    which a longer sweep amortizes). A resumed attempt counts only the batches it ran itself."""
    usd = seconds / 3600 * usd_per_hour
    return {"episodes_this_attempt": episodes, "usd_this_attempt": round(usd, 2),
            "usd_per_1000_episodes": round(usd / episodes * 1000, 2) if episodes else None}


def import_licence(src, data_dir=os.path.join(ROOT, "permit", "data")):
    """Merge a job's licences into the control plane's store; the job's verdicts replace older ones for those skills."""
    store = Licences(os.path.join(data_dir, "licences.json"))
    new = json.load(open(src))
    store.data.update(new)
    store.save()
    return sorted(new)


if __name__ == "__main__":
    if sys.argv[1:2] == ["import"]:
        print("imported:", ", ".join(import_licence(*sys.argv[2:4])))
    else:
        main()
