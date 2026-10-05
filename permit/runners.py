"""How a skill's trials run. Each runner returns run_batch({arm: n}) -> {arm: [1, 0, ...]}, the contract of
Hyperion's gate (cell/bandit.py).

mock:    coin flips at set true rates. No GPU; for tests and the demo. The rates dict is read on every call, so a
         demo can "perturb the scene" by changing it.
robolab: real GR00T N1.7 episodes in Isaac Sim through NVIDIA's RoboLab harness (Linux + RTX GPU).
         See docs/LINUX_HANDOFF.md.
"""
from cell.bandit import sim_runner


def mock(rates, seconds_per_batch=0.0):
    return sim_runner(rates, seconds_per_batch=seconds_per_batch)


def robolab(task, ports):
    raise NotImplementedError("RoboLab runner: implement on the Linux laptop, docs/LINUX_HANDOFF.md step 4")
