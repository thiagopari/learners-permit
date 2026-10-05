"""How a skill's trials run. Each runner returns run_batch({arm: n}) -> {arm: [1, 0, ...]}, the contract of
Hyperion's gate (cell/bandit.py).

mock:    coin flips at set true rates. No GPU; for tests and the demo. The rates dict is read on every call, so a
         demo can "perturb the scene" by changing it.
robolab: real GR00T N1.7 episodes in Isaac Sim through NVIDIA's RoboLab harness. Needs an RTX GPU with RT cores
         and 16 GB+ (a Nebius RTX PRO 6000, not the 8 GB laptop). See docs/LINUX_HANDOFF.md.
"""
import json
import os
import pathlib
import signal
import subprocess
import time

from cell.bandit import sim_runner


def mock(rates, seconds_per_batch=0.0):
    return sim_runner(rates, seconds_per_batch=seconds_per_batch)


def robolab(task, ports, video="none", timeout=3600, root=None):
    """Each arm is a GR00T policy server on its own port. One RoboLab process per arm and batch runs n parallel envs,
    one episode each, and records every episode (success or time-out). Unlike LIBERO's rollout_policy.py, nothing
    is dropped for finishing late. Success is read from output/<folder>/episode_results.jsonl, never the exit code."""
    root = root or os.environ.get("ROBOLAB_DIR", os.path.expanduser("~/RoboLab"))

    def run_batch(alloc):
        out = {}
        for arm, n in alloc.items():  # one Isaac Sim at a time on the GPU
            folder = f"lp_{task}_{arm}_{time.time_ns()}"
            cmd = ["uv", "run", "python", "policies/gr00t/run.py", "--headless", "--remote-host", "127.0.0.1",
                   "--remote-port", str(ports[arm]), "--task", task, "--num-envs", str(n), "--num-runs", "1",
                   "--open-loop-horizon", "8", "--instruction-type", "default", "--video-mode", video,
                   "--output-folder-name", folder]
            p = subprocess.Popen(cmd, cwd=root, env={**os.environ, "OMNI_KIT_ACCEPT_EULA": "Y"}, text=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, start_new_session=True)
            try:
                log, _ = p.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid, signal.SIGKILL)  # the whole group: uv's Isaac Sim child would keep the GPU
                p.communicate()
                raise RuntimeError(f"{task}/{arm}: RoboLab timed out after {timeout}s")
            path = pathlib.Path(root, "output", folder, "episode_results.jsonl")
            rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()] if path.exists() else []
            episodes = {(r["env_name"], r["episode"]): r for r in rows if task in (r["env_name"], r.get("task_name"))}
            if len(episodes) != n:  # a resume can re-append, so de-duplicate before counting
                raise RuntimeError(f"{task}/{arm}: expected {n} episodes, got {len(episodes)} "
                                   f"(exit {p.returncode}) {(log or '')[-500:]}")
            out[arm] = [1 if r.get("success") else 0 for r in episodes.values()]  # None = never terminated = fail
        return out
    return run_batch
