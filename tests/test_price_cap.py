"""cloud/price_cap.sh against a fake nebius CLI: no account, no real pricing policy."""
import os
import pathlib
import shutil
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
# On Windows, plain `bash` may be WSL's, which can't see the temp dir: point LP_TEST_BASH at Git Bash's bash.exe.
BASH = os.environ.get("LP_TEST_BASH") or "bash"
pytestmark = pytest.mark.skipif(shutil.which(BASH) is None or (sys.platform == "win32" and "LP_TEST_BASH" not in os.environ),
                                reason="needs a Linux-style bash (on Windows, set LP_TEST_BASH to Git Bash's bash.exe)")

# Policies live in $STATE as "<name> <id> <max_price> <blocked>" lines; every call is appended to $CALLS.
FAKE = r"""#!/usr/bin/env bash
echo "$*" >> "$CALLS"
arg() { local k=$1; shift; while [ $# -gt 0 ]; do [ "$1" = "$k" ] && { echo "$2"; return; }; shift; done; }
case "$1 $2 $3" in
"billing pricing-policy get-by-name")
    line=$(grep "^$(arg --name "$@") " "$STATE" 2>/dev/null) || exit 1
    echo "$line" | cut -d' ' -f2 ;;
"billing pricing-policy create")
    echo "$(arg --name "$@") policy-new $(arg --pricing-max-price-v1-max-price "$@") no" >> "$STATE"
    echo policy-new ;;
"billing pricing-policy get")
    line=$(grep " $(arg --id "$@") " "$STATE")
    case "$*" in
    *max_price*) echo "$line" | cut -d' ' -f3 ;;
    *) [ "$(echo "$line" | cut -d' ' -f4)" = yes ] && echo '{"status":{"scheduling_state":"SCHEDULING_STATE_BLOCKED"}}' || echo '{}' ;;
    esac ;;
"billing pricing-policy update")
    [ "${FAKE_RUNNING:-0}" = 1 ] && exit 1
    id=$(arg --id "$@") price=$(arg --pricing-max-price-v1-max-price "$@")
    sed "s/ $id [^ ]* / $id $price /" "$STATE" > "$STATE.new" && mv "$STATE.new" "$STATE" ;;
esac
"""


@pytest.fixture
def cli(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "nebius"
    fake.write_text(FAKE)
    fake.chmod(0o755)
    env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}", "STATE": str(tmp_path / "state"),
           "CALLS": str(tmp_path / "calls")}
    env.pop("LP_MAX_PRICE", None)

    def run(max_price=None, **extra):
        e = {**env, **extra, **({"LP_MAX_PRICE": max_price} if max_price else {})}
        r = subprocess.run([BASH, "-c", ". cloud/price_cap.sh && spot_pricing project-1 gpu-rtx6000-a"],
                           cwd=ROOT, env=e, capture_output=True, text=True)
        calls = (tmp_path / "calls").read_text().splitlines() if (tmp_path / "calls").exists() else []
        (tmp_path / "calls").unlink(missing_ok=True)
        return r, calls
    run.state = tmp_path / "state"
    return run


def test_first_spot_run_creates_a_capped_policy_and_uses_it(cli):
    r, calls = cli()
    assert r.returncode == 0 and r.stdout.split() == ["--spot-pricing-policy-id", "policy-new"]
    create = [c for c in calls if c.startswith("billing pricing-policy create")]
    assert len(create) == 1 and "--pricing-max-price-v1-max-price 1.20" in create[0]
    assert "--compute-instance-spec-v1-platform gpu-rtx6000-a" in create[0] and "--name lp-spot-cap-gpu-rtx6000-a" in create[0]
    assert "capped at $1.20" in r.stderr


def test_the_policy_is_reused_and_only_updated_when_the_cap_changes(cli):
    cli()
    r, calls = cli("1.2")  # the same price, written differently
    assert r.returncode == 0 and not [c for c in calls if " create" in c or " update" in c]
    r, calls = cli("1.05")
    assert r.returncode == 0 and any("update --id policy-new --pricing-max-price-v1-max-price 1.05" in c for c in calls)
    assert "1.05" in cli.state.read_text()


def test_changing_the_cap_under_a_running_vm_fails_instead_of_running_uncapped(cli):
    cli()
    r, _ = cli("1.50", FAKE_RUNNING="1")
    assert r.returncode != 0 and r.stdout == "" and "stop it first" in r.stderr


def test_a_blocked_policy_warns_that_it_will_not_start(cli):
    cli()
    cli.state.write_text(cli.state.read_text().replace(" no", " yes"))
    r, _ = cli()
    assert r.returncode == 0 and "above $1.20 right now" in r.stderr


@pytest.mark.parametrize("bad", ["cheap", "-1", "1.2345", "0"])
def test_a_bad_price_is_refused_before_any_call(cli, bad):
    r, calls = cli(bad)
    assert r.returncode != 0 and r.stdout == "" and calls == []


def test_follow_is_uncapped_only_when_asked(cli):
    r, calls = cli("follow")
    assert r.stdout.split() == ["--follows-spot-price"] and calls == [] and "no cap" in r.stderr


@pytest.mark.parametrize("script", ["cloud/vm.sh", "cloud/job.sh"])
def test_both_scripts_use_the_cap_and_never_follow_the_spot_price_directly(script):
    text = (ROOT / script).read_text()
    assert ". cloud/price_cap.sh" in text and "spot_pricing" in text
    assert "--follows-spot-price" not in text.replace("LP_MAX_PRICE=follow", "")
