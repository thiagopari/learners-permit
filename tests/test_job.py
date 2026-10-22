import fnmatch
import json
import pathlib
import random
import shutil
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cloud" / "job"))
import sweep  # noqa: E402


def env(state, **kw):
    return {"LP_SKILL": "bananas_in_bin", "LP_RUNNER": "mock", "LP_STATE": str(state), "LP_COMMIT": "abc123", **kw}


def perfect(calls, die_after=None):
    def run_batch(alloc):
        if die_after is not None and len(calls) >= die_after:
            raise RuntimeError("preempted")
        calls.append(alloc)
        return {a: [1] * n for a, n in alloc.items()}
    return run_batch


def test_a_sweep_job_writes_its_licence_checkpoint_and_summary_to_the_bucket(tmp_path):
    random.seed(0)
    s = sweep.main(env(tmp_path, LP_USD_PER_HOUR="1.80"), run_batch=perfect([]))
    assert s["status"] == "licensed" and s["trials"] == 16 and s["episodes_this_attempt"] == 16
    assert s["source"] == "mock:job:abc123" and s["scope"] == {"speed_pct": [40]}
    on_disk = json.loads((tmp_path / "summary.json").read_text())
    assert on_disk == s
    assert json.loads((tmp_path / "licences.json").read_text())["bananas_in_bin"]["status"] == "licensed"
    assert json.loads((tmp_path / "sweeps.json").read_text()) == {}  # a finished sweep leaves no checkpoint
    assert not list(tmp_path.glob("*.part"))


def test_a_preempted_job_resumes_from_the_bucket_with_no_lost_batches(tmp_path):
    calls = []
    with pytest.raises(RuntimeError, match="preempted"):
        sweep.main(env(tmp_path), run_batch=perfect(calls, die_after=2))
    checkpoint = json.loads((tmp_path / "sweeps.json").read_text())
    assert len(next(iter(checkpoint.values()))["log"]) == 2  # copied out after each batch, before the crash
    again = []
    s = sweep.main(env(tmp_path), run_batch=perfect(again))
    assert s["status"] == "licensed" and s["trials"] == 16 and s["resumed"] == 1
    assert len(again) == 2 and s["episodes_this_attempt"] == 8  # only the batches this attempt ran


def test_a_new_image_or_scene_never_resumes_an_old_sweep(tmp_path):
    with pytest.raises(RuntimeError):
        sweep.main(env(tmp_path), run_batch=perfect([], die_after=2))
    calls = []
    s = sweep.main(env(tmp_path, LP_COMMIT="def456"), run_batch=perfect(calls))
    assert s["resumed"] == 0 and len(calls) == 4
    calls = []
    s = sweep.main(env(tmp_path, LP_COMMIT="def456", LP_BACKGROUND_SEED="7"), run_batch=perfect(calls))
    assert s["resumed"] == 0 and s["source"] == "mock:job:def456:background_seed=7"


def test_the_job_runs_end_to_end_on_the_mock_runner(tmp_path):
    random.seed(3)
    s = sweep.main(env(tmp_path, LP_SKILL="red_dishes_in_bin", LP_ARMS="n17_droid", LP_SPEEDS="25,40"))
    assert s["status"] in ("licensed", "refused") and s["policy"] == "n17_droid"
    assert s["scope"] == {"speed_pct": [25, 40]}


@pytest.mark.parametrize("bad,message", [({"LP_SKILL": "open_door"}, "unknown skill"),
                                         ({"LP_ARMS": "n17_droid_ft"}, "has no arm")])
def test_bad_settings_fail_before_any_gpu_time(tmp_path, bad, message):
    with pytest.raises(SystemExit, match=message):
        sweep.main(env(tmp_path, **bad), run_batch=lambda alloc: pytest.fail("ran trials"))


def test_import_puts_a_job_licence_into_the_control_plane(tmp_path):
    sweep.main(env(tmp_path / "bucket"), run_batch=perfect([]))
    data = tmp_path / "permit-data"
    assert sweep.import_licence(str(tmp_path / "bucket" / "licences.json"), str(data)) == ["bananas_in_bin"]
    from permit.server import Permit
    p = Permit(data_dir=str(data))
    assert p.licences.covers("bananas_in_bin", {"speed_pct": 40})


def test_the_image_gets_every_file_the_job_needs():
    ignored = [line.strip() for line in (ROOT / ".dockerignore").read_text().splitlines()
               if line.strip() and not line.startswith("#")]
    needed = ["permit/server.py", "permit/skills.json", "permit/policy.cedar", "cloud/job/sweep.py",
              "cloud/job/entrypoint.sh", "cloud/measure.py", "requirements.txt"]
    for path in needed:
        assert (ROOT / path).exists()
        parts = pathlib.PurePosixPath(path).parts
        hit = [p for p in ignored if any(fnmatch.fnmatch("/".join(parts[:i + 1]), p.removeprefix("**/"))
                                         for i in range(len(parts)))]
        assert not hit, f"{path} is excluded by .dockerignore {hit}"
    assert "/opt/learners-permit/cloud/job/entrypoint.sh" in (ROOT / "cloud/job/Dockerfile").read_text()


@pytest.mark.skipif(shutil.which("bash") is None, reason="needs bash")
@pytest.mark.parametrize("script", ["cloud/job.sh", "cloud/job/entrypoint.sh"])
def test_the_job_scripts_parse(script):
    subprocess.run(["bash", "-n", script], cwd=ROOT, check=True)  # relative: WSL's bash can't read D:\ paths
