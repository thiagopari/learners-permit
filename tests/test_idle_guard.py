import os
import pathlib
import subprocess
import time

import pytest

GUARD = pathlib.Path(__file__).parent.parent / "cloud" / "idle_guard.sh"


@pytest.fixture
def vm(tmp_path):
    """A fake /run, /proc and /dev/pts, and stub nvidia-smi / systemctl / logger that record instead of acting."""
    for d in ("run", "proc", "dev/pts", "bin"):
        (tmp_path / d).mkdir(parents=True)
    (tmp_path / "proc/loadavg").write_text("0.10 0.20 0.30 1/200 999\n")
    old = time.time() - 3600
    (tmp_path / "dev/pts/0").touch()
    os.utime(tmp_path / "dev/pts/0", (old, old))  # nobody has typed for an hour
    (tmp_path / "gpu").write_text("0")
    stubs = {"nvidia-smi": f'cat {tmp_path}/gpu', "systemctl": f'echo "$@" >> {tmp_path}/calls', "logger": "true"}
    for name, body in stubs.items():
        (tmp_path / "bin" / name).write_text(f"#!/bin/sh\n{body}\n")
        (tmp_path / "bin" / name).chmod(0o755)

    def run(idle_for_min=None):
        if idle_for_min is not None:
            (tmp_path / "run/lp-idle-guard").write_text(str(int(time.time() - idle_for_min * 60)))
        env = {**os.environ, "LP_GUARD_TEST_ROOT": str(tmp_path), "PATH": f"{tmp_path}/bin:{os.environ['PATH']}"}
        out = subprocess.run(["bash", str(GUARD)], env=env, capture_output=True, text=True, check=True).stdout
        calls = (tmp_path / "calls").read_text() if (tmp_path / "calls").exists() else ""
        return out, calls
    run.root = tmp_path
    return run


def test_powers_off_after_the_idle_window(vm):
    out, calls = vm(idle_for_min=31)
    assert "idle for 31 of 30" in out and calls == "poweroff\n"


def test_fresh_boot_starts_the_clock_instead_of_powering_off(vm):
    out, calls = vm()  # no state file yet, as after a boot (/run is tmpfs)
    assert "idle for 0" in out and calls == ""


@pytest.mark.parametrize("make_busy, reason", [
    (lambda root: (root / "gpu").write_text("85"), "gpu 85%"),
    (lambda root: (root / "proc/loadavg").write_text("3.0 2.5 2.0 5/300 999\n"), "load 2.5"),
    (lambda root: (root / "dev/pts/0").touch(), "typing"),
    (lambda root: (root / "run/lp-keepalive").touch(), "keepalive"),
])
def test_any_sign_of_work_resets_the_clock(vm, make_busy, reason):
    make_busy(vm.root)
    out, calls = vm(idle_for_min=90)
    assert reason in out and calls == ""
    assert int((vm.root / "run/lp-idle-guard").read_text()) >= time.time() - 5  # clock reset to now
