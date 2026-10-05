"""The first GPU session's numbers, unattended, through the same runner the gate uses. Rows append to
~/lp-measurements.jsonl; quote them (with ~/lp-versions.txt) in docs/PLAN.md instead of NVIDIA's.

  default scene  40 episodes each of the two must-ship tasks (NVIDIA's README: 38/40 and 15/40)
  perturbed      20 episodes of bananas with a randomized background, 2 seeds: the revoke beat. At 50% or below,
                 drift revokes the licence in about 9 live runs; at 60%, about 19 and only 83% of the time. If it
                 stays higher, the beat needs a stronger perturbation (RoboLab's lighting variation, ported to GR00T).

On the VM, with the GR00T server starting or up on 127.0.0.1:5555 (docs/LINUX_HANDOFF.md, Step 4):
    ROBOLAB_DIR=~/RoboLab .venv/bin/python cloud/measure.py
"""
import json
import os
import socket
import time

from permit import runners

PLAN = [("BananasInBinThreeTotalTask", 40, None), ("RedDishesInBinTask", 40, None),
        ("BananasInBinThreeTotalTask", 20, 1), ("BananasInBinThreeTotalTask", 20, 2)]
OUT = os.path.expanduser("~/lp-measurements.jsonl")


def wait_for_server(port=5555, minutes=15):
    for _ in range(minutes * 12):
        try:
            socket.create_connection(("127.0.0.1", port), timeout=2).close()
            return
        except OSError:
            time.sleep(5)
    raise SystemExit(f"no GR00T server on 127.0.0.1:{port} after {minutes} minutes")


def main():
    wait_for_server()
    for task, n, seed in PLAN:
        extra = [] if seed is None else ["--randomize-background", "--background-seed", str(seed)]
        t0, row = time.time(), {"task": task, "episodes": n, "background_seed": seed}
        try:
            outcomes = runners.robolab(task, {"a": 5555}, timeout=7200, extra_args=extra)({"a": n})["a"]
            row["successes"] = sum(outcomes)
        except RuntimeError as e:  # one failed condition shouldn't cost the rest of the session
            row["error"] = str(e)[-300:]
        row["minutes"] = round((time.time() - t0) / 60, 1)
        print(json.dumps(row), flush=True)
        with open(OUT, "a") as f:
            f.write(json.dumps(row) + "\n")


if __name__ == "__main__":
    main()
