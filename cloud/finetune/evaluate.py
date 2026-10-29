"""Commission the fine-tuned red-dishes policy through the gate, and measure zero-shot on the very same scenes.

    ROBOLAB_DIR=~/RoboLab .venv/bin/python cloud/finetune/evaluate.py CHECKPOINT_NAME [OUT_DIR]

Needs two GR00T servers on the VM: the zero-shot nvidia/GR00T-N1.7-DROID on 127.0.0.1:5600 and the fine-tuned
checkpoint on 127.0.0.1:5601. Both are evaluated on RoboLab seeds 2001, 2002, ... (one seed per launch of 20 episodes),
which no training episode used (training used seeds 1001-1003). The fine-tuned arm is commissioned through the same
gate as everything else; the zero-shot arm then runs the same number of launches on the same seeds, so the two
numbers describe the same scenes.
"""
import json
import os
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from permit import runners  # noqa: E402
from permit.gate import prob_rate_at_least  # noqa: E402
from permit.licences import Licences  # noqa: E402

TASK, FIRST_SEED, BATCH = "RedDishesInBinTask", 2001, 20


def main(checkpoint, out):
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    log = open(out / "evaluate.jsonl", "a")

    def say(**row):
        row = {"t": time.strftime("%H:%M:%S"), **row}
        print(json.dumps(row), flush=True); log.write(json.dumps(row) + "\n"); log.flush()

    lic_store = Licences(str(out / "licences.json"))
    ft = runners.robolab(TASK, {"n17_droid_ft": 5601}, timeout=3600, seed=FIRST_SEED)
    t0 = time.time()
    lic = lic_store.commission("red_dishes_in_bin", ["n17_droid_ft"], ft, batch=BATCH, scope={"speed_pct": [40]},
                               source=f"robolab:finetuned:{checkpoint}:seeds-from-{FIRST_SEED}", resume=False)
    launches = lic["trials"] // BATCH
    say(step="fine-tuned, through the gate", checkpoint=checkpoint, status=lic["status"], decision=lic["decision"],
        successes=lic["successes"], trials=lic["trials"], p=lic["p"], launches=launches,
        seeds=list(range(FIRST_SEED, FIRST_SEED + launches)), minutes=round((time.time() - t0) / 60, 1), log=lic["log"])
    zs = runners.robolab(TASK, {"n17_droid": 5600}, timeout=3600, seed=FIRST_SEED)
    outcomes, t0 = [], time.time()
    for _ in range(launches):  # the same seeds, the same number of episodes
        outcomes += zs({"n17_droid": BATCH})["n17_droid"]
        s = sum(outcomes)
        say(step="zero-shot, same seeds", successes=s, trials=len(outcomes),
            p=round(prob_rate_at_least(s, len(outcomes) - s, 0.8), 4))
    s = sum(outcomes)
    say(step="summary", finetuned=f"{lic['successes']}/{lic['trials']}", finetuned_status=lic["status"],
        zero_shot=f"{s}/{len(outcomes)}", zero_shot_p=round(prob_rate_at_least(s, len(outcomes) - s, 0.8), 4),
        seeds=list(range(FIRST_SEED, FIRST_SEED + launches)), minutes=round((time.time() - t0) / 60, 1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser("~/finetune/eval"))
