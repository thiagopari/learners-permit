"""Turn the extracted successful episodes into a LeRobot v2.1 dataset laid out like GR00T's DROID sample.

    ~/Isaac-GR00T/.venv/bin/python build_dataset.py EPISODES_DIR OUT_DIR

Mirrors ~/Isaac-GR00T/demo_data/droid_sample exactly (its modality.json, its info.json schema: v2.1, 15 fps, two
180x320 videos, 17-D state and action), then lets GR00T's own tools compute stats.json and relative_stats.json.

    state  (17) = eef_9d (9), gripper_position (1), joint_position (7), built from the recorded proprio exactly as
                  RoboLab's GR00T client builds it for the live policy (ee_pos, ee_quat, DROID rotation correction)
    action (17) = the same layout as absolute targets, as in the DROID sample: eef_9d of the next step, and the
                  gripper and joint commands the policy actually sent (RoboLab's recorded actions: 7 joints + gripper)
"""
import json
import pathlib
import shutil
import sys

import numpy as np
import pandas as pd

GR00T = pathlib.Path.home() / "Isaac-GR00T"
SAMPLE = GR00T / "demo_data" / "droid_sample"
sys.path.insert(0, str(GR00T))
# Same constants as RoboLab's policies/gr00t/client.py, so training states match what the policy sees live.
DROID_EEF_ROTATION_CORRECT = np.array([[0, 0, -1], [-1, 0, 0], [0, 1, 0]], dtype=np.float64)


def quat_wxyz_to_matrix(q):
    w, x, y, z = q / np.linalg.norm(q)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def eef_9d(pos, quat):
    rot = quat_wxyz_to_matrix(np.asarray(quat, dtype=np.float64)) @ DROID_EEF_ROTATION_CORRECT
    return np.concatenate([np.asarray(pos, dtype=np.float64), rot[:2, :].reshape(6)])


def episode_frames(a):
    n = len(a["joints"])
    eef = np.stack([eef_9d(a["ee_pos"][t], a["ee_quat"][t]) for t in range(n)])
    state = np.concatenate([eef, a["gripper"].reshape(n, 1), a["joints"]], axis=1).astype(np.float32)
    eef_next = np.concatenate([eef[1:], eef[-1:]])  # the last step holds its pose
    action = np.concatenate([eef_next, a["actions"][:, 7:8], a["actions"][:, :7]], axis=1).astype(np.float32)
    return state, action


def main(src, out):
    src, out = pathlib.Path(src), pathlib.Path(out)
    if out.exists():
        shutil.rmtree(out)
    (out / "meta").mkdir(parents=True)
    episodes = sorted(p for p in src.iterdir() if (p / "arrays.npz").exists())
    tasks, rows_meta, index = {}, [], 0
    for e, ep in enumerate(episodes):
        meta = json.load(open(ep / "meta.json"))
        task = tasks.setdefault(meta["instruction"], len(tasks))
        state, action = episode_frames(np.load(ep / "arrays.npz"))
        n = len(state)
        df = pd.DataFrame({"observation.state": list(state), "action": list(action),
                           "timestamp": np.arange(n, dtype=np.float32) / 15.0, "frame_index": np.arange(n),
                           "episode_index": e, "index": np.arange(index, index + n), "task_index": task})
        (out / "data" / "chunk-000").mkdir(parents=True, exist_ok=True)
        df.to_parquet(out / "data" / "chunk-000" / f"episode_{e:06d}.parquet")
        for key, name in (("exterior_1_left", "exterior"), ("wrist_left", "wrist")):
            d = out / "videos" / "chunk-000" / f"observation.images.{key}"
            d.mkdir(parents=True, exist_ok=True)
            shutil.copy(ep / f"{name}.mp4", d / f"episode_{e:06d}.mp4")
        rows_meta.append({"episode_index": e, "tasks": [meta["instruction"]], "length": n,
                          "source": f"seed {meta['seed']} env {meta['env_id']}"})
        index += n
    info = json.load(open(SAMPLE / "meta" / "info.json"))
    info.update(total_episodes=len(episodes), total_frames=index, total_tasks=len(tasks), total_videos=2 * len(episodes),
                total_chunks=1, splits={"train": f"0:{len(episodes)}"})
    json.dump(info, open(out / "meta" / "info.json", "w"), indent=2)
    shutil.copy(SAMPLE / "meta" / "modality.json", out / "meta" / "modality.json")
    with open(out / "meta" / "episodes.jsonl", "w") as f:
        f.writelines(json.dumps(r) + "\n" for r in rows_meta)
    with open(out / "meta" / "tasks.jsonl", "w") as f:
        f.writelines(json.dumps({"task_index": i, "task": t}) + "\n" for t, i in tasks.items())
    from gr00t.data.embodiment_tags import EmbodimentTag
    from gr00t.data.stats import generate_rel_stats, generate_stats
    generate_stats(out)
    generate_rel_stats(out, EmbodimentTag.OXE_DROID_RELATIVE_EEF_RELATIVE_JOINT)
    print(json.dumps({"episodes": len(episodes), "frames": index, "tasks": list(tasks)}))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
