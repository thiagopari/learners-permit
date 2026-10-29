"""Keep the successful episodes of one recorded RoboLab launch, in the shape GR00T's DROID fine-tuning needs.

    python extract.py RUN_DIR OUT_DIR       (RoboLab's venv: h5py, cv2, numpy; ffmpeg on PATH)

RUN_DIR is a RoboLab output folder from a run with --record-image-data. For every episode RoboLab marked successful
(episode_results.jsonl), up to its final step (log_*_env<i>.json), this writes OUT_DIR/ep_<run>_<seed>_<env>/:
exterior.mp4 and wrist.mp4 (180x320, H.264, 15 fps, resized exactly as RoboLab's GR00T client does), arrays.npz
(ee_pos, ee_quat, joints, gripper, actions) and meta.json. Failed episodes are dropped: this is filtered behaviour
cloning on the policy's own successes. Nothing is relabelled or invented.
"""
import glob
import json
import os
import pathlib
import subprocess
import sys

import cv2
import h5py
import numpy as np

HEIGHT, WIDTH, FPS = 180, 320, 15  # RoboLab's GR00T client: RESOLUTION = (180, 320); dt = 1/15
CAMS = {"exterior": "over_shoulder_left_camera", "wrist": "wrist_cam"}


def write_video(frames, path):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt",
                          "yuv420p", "-crf", "18", str(path)], stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write(cv2.resize(f, (WIDTH, HEIGHT), interpolation=cv2.INTER_AREA).astype(np.uint8).tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise RuntimeError(f"ffmpeg failed on {path}")


def main(run_dir, out_dir, seed):
    run_dir, out_dir = pathlib.Path(run_dir), pathlib.Path(out_dir)
    results = {r["env_id"]: r for r in map(json.loads, open(run_dir / "episode_results.jsonl"))}
    task_dir = next(p for p in run_dir.iterdir() if p.is_dir())
    kept = 0
    for h5 in sorted(task_dir.glob("run_*.hdf5")):
        run = int(h5.stem.split("_")[1])
        with h5py.File(h5, "r") as f:
            for demo in sorted(f["data"], key=lambda d: int(d.split("_")[1])):
                env = int(demo.split("_")[1])
                r = results.get(env)
                if not r or not r.get("success"):
                    continue
                log = json.load(open(task_dir / f"log_{run}_env{env}.json"))
                n = int(log["final_step"])
                d = f["data"][demo]
                ep = out_dir / f"ep_{run}_{seed}_{env}"
                ep.mkdir(parents=True, exist_ok=True)
                for name, cam in CAMS.items():
                    write_video(d[f"obs/image_obs/{cam}"][:n], ep / f"{name}.mp4")
                po = d["obs/proprio_obs"]
                np.savez(ep / "arrays.npz", ee_pos=po["ee_pos"][:n], ee_quat=po["ee_quat"][:n],
                         joints=po["arm_joint_pos"][:n], gripper=po["gripper_pos"][:n], actions=d["actions"][:n])
                json.dump({"instruction": r["instruction"], "length": n, "seed": seed, "env_id": env, "run": run,
                           "source": str(run_dir)}, open(ep / "meta.json", "w"))
                kept += 1
    print(json.dumps({"run_dir": str(run_dir), "episodes": len(results), "successes_kept": kept}), flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]))
