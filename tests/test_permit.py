import json
import random
import subprocess
import threading
import types

import pytest

from cell.bandit import p_at_least
from permit import authz, datasheet, planner, runners
from permit.licences import Licences
from permit.server import Permit

AI = authz.AGENT


@pytest.fixture
def p(tmp_path):
    random.seed(0)
    return Permit(data_dir=str(tmp_path), clock=lambda: types.SimpleNamespace(tm_hour=14), lock_timeout=0.2)


def licensed(p, skill, arm="n17_droid", tier="supervised"):
    p.rates[skill][arm] = 1.0
    assert p.commission("sue", skill, arms=[arm], tier=tier)["status"] == "licensed"


def test_gate_math():
    assert round(p_at_least(38, 2), 3) == 0.993
    assert p_at_least(12, 0) < 0.95 <= p_at_least(16, 0)                # batches of 4: the first pass is at 16/16
    assert p_at_least(297, 0, 0.99) < 0.95 <= p_at_least(298, 0, 0.99)  # "unattended" tier: 298 straight


def test_refused_then_earned(p):
    p.rates["red_dishes_in_bin"].update(n17_droid=0.0, n17_droid_ft=1.0)
    assert p.commission("sue", "red_dishes_in_bin", arms=["n17_droid"])["status"] == "refused"
    e = p.execute(AI, "red_dishes_in_bin", {}, requester="olga")
    assert e["decision"] == "deny" and "not licensed" in e["reasons"][0] and e["escalate"]["command_hash"]
    assert p.commission("sue", "red_dishes_in_bin", arms=["n17_droid_ft"])["status"] == "licensed"
    assert p.execute(AI, "red_dishes_in_bin", {}, requester="olga")["decision"] == "allow"


def test_unattended_tier_licenses_a_perfect_policy_and_refuses_a_broken_one(p):
    p.rates["bananas_in_bin"]["n17_droid"] = 1.0
    lic = p.commission("sue", "bananas_in_bin", tier="unattended")
    assert lic["status"] == "licensed" and lic["trials"] >= 298 and lic["revoke_below"] == 0.95
    p.rates["bananas_in_bin"]["n17_droid"] = 0.0
    lic = p.commission("sue", "bananas_in_bin", tier="unattended")
    assert lic["status"] == "refused" and lic["trials"] >= 20  # no early fail before 20 trials


def test_llm_cannot_supply_identity_or_approval(p):
    # unlicensed skill: honouring an LLM-supplied approver would allow it via the approval permit
    e = p.execute(AI, "red_dishes_in_bin", {"approver": "sue", "role": "supervisor"}, requester="olga")
    assert e["decision"] == "deny" and e["args"] == {} and "approver" not in e["context"]


def test_requester_role_cannot_be_laundered_through_the_ai(p):
    licensed(p, "bananas_in_bin")
    assert p.execute("max", "bananas_in_bin", {})["decision"] == "deny"  # maintenance can't pick directly...
    assert p.order("max", "Put the bananas in the bin")[0]["decision"] == "deny"  # ...or through the AI
    assert p.execute(AI, "bananas_in_bin", {})["decision"] == "deny"  # no requester at all: fail closed
    assert p.order("olga", "Put the bananas in the bin")[0]["decision"] == "allow"


def test_approval_is_single_use_and_bound_to_command_repeat_and_person(p):
    first = p.approve("sue", "red_dishes_in_bin", {"speed_pct": 30}, "olga")
    assert p.execute(AI, "red_dishes_in_bin", {"speed_pct": 40}, approval=first, requester="olga")["decision"] == "deny"
    assert p.execute(AI, "red_dishes_in_bin", {"speed_pct": 30}, approval=first, requester="olga")["decision"] == "deny"  # burned
    t = p.approve("sue", "red_dishes_in_bin", {"speed_pct": 30}, "olga")
    assert p.execute(AI, "red_dishes_in_bin", {"speed_pct": 30}, approval=t, requester="olga", repeat=100)["decision"] == "deny"
    t = p.approve("sue", "red_dishes_in_bin", {"speed_pct": 30}, "olga")
    assert p.execute(AI, "red_dishes_in_bin", {"speed_pct": 30}, approval=t, requester="max")["decision"] == "deny"
    t = p.approve("sue", "red_dishes_in_bin", {"speed_pct": 30}, "olga")
    assert p.execute(AI, "red_dishes_in_bin", {"speed_pct": 30}, approval=t, requester="olga")["decision"] == "allow"
    assert p.execute(AI, "red_dishes_in_bin", {"speed_pct": 30}, approval=t, requester="olga")["decision"] == "deny"
    with pytest.raises(PermissionError):
        p.approve("olga", "red_dishes_in_bin", {}, "olga")


def test_licence_covers_only_the_tested_speed(p):
    licensed(p, "bananas_in_bin")  # default scope: commissioned at 40%
    assert p.execute(AI, "bananas_in_bin", {}, requester="olga")["decision"] == "allow"
    e = p.execute(AI, "bananas_in_bin", {"speed_pct": 30}, requester="olga")
    assert e["decision"] == "deny" and "not licensed" in e["reasons"][0]


def test_invalid_speed_or_repeat_is_denied(p):
    for args, repeat in (({"speed_pct": 50.9}, 1), ({"speed_pct": -500}, 1), ({"speed_pct": True}, 1), ({}, 0), ({}, 101)):
        e = p.execute("olga", "red_dishes_in_bin", args, repeat=repeat)
        assert e["decision"] == "deny" and "invalid" in e["reasons"][0]


def test_people_work_under_their_own_role(p):
    assert p.execute("olga", "red_dishes_in_bin", {"speed_pct": 70})["decision"] == "allow"  # no licence needed
    assert p.execute("olga", "red_dishes_in_bin", {"speed_pct": 90})["decision"] == "deny"
    p.sensors["human_in_zone"] = True
    assert p.execute("olga", "red_dishes_in_bin", {"speed_pct": 40})["decision"] == "deny"
    assert p.execute("olga", "red_dishes_in_bin", {"speed_pct": 20})["decision"] == "allow"


@pytest.mark.parametrize("text,kg", [
    ("Net weight: 2.4 kg", 2.4), ("Weight 500 g", 0.5), ("Mass: 1,250 g", 1.25), ("Gewicht/weight 2,4 kg", 2.4),
    ("weight 2400 grams", 2.4), ("Weight: 5.3 pounds", 2.404), ("weight 2.4 kgs", 2.4), ("Weight (kg): 2.4", 2.4),
    ("payload weight 0.5 kg ... Net weight 2.4 kg", 2.4),  # the largest wins: conservative
])
def test_datasheet_mass_formats(text, kg):
    page = {"results": [{"url": "https://x/ds", "raw_content": text}]}
    assert datasheet.check("PN-1", 1.0, call=lambda endpoint, body: page)["mass_kg"] == kg


def test_datasheet_can_only_block(p):
    licensed(p, "bananas_in_bin")

    def page(text):
        return lambda endpoint, body: {"results": [{"url": "https://x/ds", "raw_content": text}]}

    p.check_part = lambda part, limit: datasheet.check(part, limit, call=page("Net weight: 2.4 kg"))
    e = p.execute(AI, "bananas_in_bin", {"part_number": "PN-1"}, requester="olga")
    assert e["decision"] == "deny" and "2.4 kg > 1.0 kg" in e["reasons"][0] and "https://x/ds" in e["reasons"][0]
    p.check_part = lambda part, limit: datasheet.check(part, limit, call=page("Weight 500 g"))
    assert p.execute(AI, "bananas_in_bin", {"part_number": "PN-1"}, requester="olga")["decision"] == "allow"
    # "within limit" never widens: an out-of-envelope speed stays denied
    e = p.execute(AI, "bananas_in_bin", {"part_number": "PN-1", "speed_pct": 90}, requester="olga")
    assert e["decision"] == "deny" and e["datasheet"] is None


def test_live_drift_revokes(p):
    licensed(p, "bananas_in_bin")
    p.rates["bananas_in_bin"]["n17_droid"] = 0.0
    for _ in range(8):
        p.execute(AI, "bananas_in_bin", {}, requester="olga")
    assert p.licences.data["bananas_in_bin"]["status"] == "revoked"
    assert p.execute(AI, "bananas_in_bin", {}, requester="olga")["decision"] == "deny"


def test_one_early_miss_does_not_revoke(tmp_path):
    lic = Licences(str(tmp_path / "l.json"))
    lic.data["s"] = {"status": "licensed", "thr": 0.8, "revoke_below": 0.7, "scope": {}, "live": [1] * 8}
    lic.record_live("s", False)
    assert lic.data["s"]["status"] == "licensed"


def test_crashed_run_is_logged_and_counts_against_the_skill(p):
    licensed(p, "bananas_in_bin")

    def crash(skill):
        raise RuntimeError("Isaac Sim died")
    p.run_batch = crash
    e = p.execute(AI, "bananas_in_bin", {}, requester="olga")
    assert e["result"] == "error: Isaac Sim died" and p.licences.data["bananas_in_bin"]["live"] == [0]
    assert json.loads(open(p.audit_path).read().splitlines()[-1])["result"] == "error: Isaac Sim died"


def test_busy_cell_denies_instead_of_queueing(p):
    held, release = threading.Event(), threading.Event()

    def hold():
        with p.lock:
            held.set()
            release.wait(5)
    threading.Thread(target=hold, daemon=True).start()
    held.wait(5)
    e = p.execute("olga", "red_dishes_in_bin", {})
    release.set()
    assert e["decision"] == "deny" and e["reasons"] == ["cell busy"]


def test_repeat_runs_n_episodes_under_one_decision(p):
    licensed(p, "bananas_in_bin")
    e = p.execute("olga", "bananas_in_bin", {}, repeat=5)
    assert e["decision"] == "allow" and e["result"] == "5/5 succeeded"
    assert len(p.licences.data["bananas_in_bin"]["live"]) == 5


def test_planner_keeps_only_catalogue_skills_and_allowed_args():
    def reply(calls):
        tool_calls = [types.SimpleNamespace(function=types.SimpleNamespace(name=n, arguments=a)) for n, a in calls]
        msg = types.SimpleNamespace(tool_calls=tool_calls)
        create = lambda **kw: types.SimpleNamespace(choices=[types.SimpleNamespace(message=msg)])  # noqa: E731
        return types.SimpleNamespace(chat=types.SimpleNamespace(completions=types.SimpleNamespace(create=create)))

    skills = {"bananas_in_bin": {"instruction": "put the bananas in the bin"}}
    client = reply([("bananas_in_bin", '{"speed_pct": 30, "role": "supervisor"}'), ("open_door", "{}")])
    assert planner.plan("x", skills, client=client) == [{"skill": "bananas_in_bin", "args": {"speed_pct": 30}}]


class FakeRoboLab:
    """Stands in for subprocess.Popen: writes the episode_results.jsonl a real RoboLab run would."""
    rows = staticmethod(lambda n: [{"env_name": "RedDishesInBinTask", "episode": i, "success": [True, False, None][i % 3]}
                                   for i in range(n)])

    def __init__(self, cmd, cwd, env, **kw):
        assert env["OMNI_KIT_ACCEPT_EULA"] == "Y" and kw["start_new_session"]
        folder, n = cmd[cmd.index("--output-folder-name") + 1], int(cmd[cmd.index("--num-envs") + 1])
        rows = self.rows(n)
        out = FakeRoboLab.root / "output" / folder
        out.mkdir(parents=True)
        (out / "episode_results.jsonl").write_text("\n".join(json.dumps(r) for r in rows + rows[:1]) + "\n")  # resume
        self.returncode, self.pid = 0, 0

    def communicate(self, timeout=None):
        return "", None


def test_robolab_runner_reads_episode_results(tmp_path, monkeypatch):
    FakeRoboLab.root = tmp_path
    monkeypatch.setattr(runners.subprocess, "Popen", FakeRoboLab)
    run_batch = runners.robolab("RedDishesInBinTask", {"ft": 5556}, root=str(tmp_path))
    assert run_batch({"ft": 6}) == {"ft": [1, 0, 0, 1, 0, 0]}  # None (never terminated) counts as a failure


def test_robolab_runner_refuses_a_short_batch(tmp_path, monkeypatch):
    class Crash:
        def __init__(self, cmd, **kw):
            self.returncode, self.pid = 1, 0

        def communicate(self, timeout=None):
            return "Isaac crashed", None
    monkeypatch.setattr(runners.subprocess, "Popen", Crash)
    with pytest.raises(RuntimeError, match="expected 4 episodes, got 0"):
        runners.robolab("RedDishesInBinTask", {"a": 5555}, root=str(tmp_path))({"a": 4})


def test_robolab_runner_kills_the_whole_group_on_timeout(tmp_path, monkeypatch):
    killed = []

    class Hang:
        def __init__(self, cmd, **kw):
            self.pid, self.calls = 4242, 0

        def communicate(self, timeout=None):
            self.calls += 1
            if self.calls == 1:
                raise subprocess.TimeoutExpired("uv", timeout)
            return "", None
    monkeypatch.setattr(runners.subprocess, "Popen", Hang)
    monkeypatch.setattr(runners.os, "killpg", lambda pid, sig: killed.append(pid))
    with pytest.raises(RuntimeError, match="timed out"):
        runners.robolab("RedDishesInBinTask", {"a": 5555}, timeout=1, root=str(tmp_path))({"a": 4})
    assert killed == [4242, 4242]  # the launch and its one retry


def test_robolab_runner_retries_a_crashed_launch_once(tmp_path, monkeypatch):
    FakeRoboLab.root, launches = tmp_path, []

    class CrashOnce(FakeRoboLab):
        def __init__(self, cmd, cwd, env, **kw):
            launches.append(cmd)
            if len(launches) > 1:
                super().__init__(cmd, cwd, env, **kw)
            self.returncode, self.pid = (1 if len(launches) == 1 else 0), 0
    monkeypatch.setattr(runners.subprocess, "Popen", CrashOnce)
    assert runners.robolab("RedDishesInBinTask", {"ft": 5556}, root=str(tmp_path))({"ft": 3}) == {"ft": [1, 0, 0]}
    folder = lambda cmd: cmd[cmd.index("--output-folder-name") + 1]  # noqa: E731
    assert len(launches) == 2 and folder(launches[0]) != folder(launches[1])  # the retry never reuses a folder


def crash_after(batches):
    """A perfect policy whose runner dies after `batches` batches, the way a preempted VM would."""
    calls = []

    def run_batch(alloc):
        calls.append(alloc)
        if len(calls) > batches:
            raise RuntimeError("VM preempted")
        return {a: [1] * n for a, n in alloc.items()}
    return run_batch, calls


def test_interrupted_sweep_keeps_its_batches_and_resumes_only_when_asked(p):
    dies, _ = crash_after(2)
    p.run_batch = lambda skill: dies
    with pytest.raises(RuntimeError, match="preempted"):
        p.commission("sue", "bananas_in_bin")
    assert len(p.sweep("bananas_in_bin")[2]["log"]) == 2
    assert len(json.load(open(p.licences.sweeps_path)).popitem()[1]["log"]) == 2  # on disk, for a restarted server
    with pytest.raises(ValueError, match="interrupted after 2 batches"):
        p.commission("sue", "bananas_in_bin")
    works, calls = crash_after(99)
    p.run_batch = lambda skill: works
    lic = p.commission("sue", "bananas_in_bin", resume=True)
    assert lic["status"] == "licensed" and lic["trials"] == 16 and lic["resumed"] == 1 and len(calls) == 2
    assert p.sweep("bananas_in_bin")[2] is None


def test_resume_false_discards_the_interrupted_sweep(p):
    dies, _ = crash_after(2)
    p.run_batch = lambda skill: dies
    with pytest.raises(RuntimeError):
        p.commission("sue", "bananas_in_bin")
    works, calls = crash_after(99)
    p.run_batch = lambda skill: works
    lic = p.commission("sue", "bananas_in_bin", resume=False)
    assert lic["trials"] == 16 and lic["resumed"] == 0 and len(calls) == 4


def test_a_sweep_resumes_only_into_the_same_runner(p):
    dies, _ = crash_after(1)
    p.run_batch = lambda skill: dies
    with pytest.raises(RuntimeError):
        p.commission("sue", "bananas_in_bin")
    p.runner = "robolab"  # same skill, arms and scope; real episodes must not continue a mock sweep
    assert p.sweep("bananas_in_bin")[2] is None


def test_a_perturbed_scene_reaches_robolab_and_never_resumes_a_default_scene_sweep(p, monkeypatch):
    seen = []
    monkeypatch.setattr(runners, "robolab", lambda task, arms, **kw: seen.append(kw) or (lambda alloc: {}))
    p.runner = "robolab"
    p.run_batch("bananas_in_bin")
    p.scene = {"background_seed": 7}
    p.run_batch("bananas_in_bin")
    assert seen[0]["extra_args"] == [] and seen[1]["extra_args"] == ["--randomize-background", "--background-seed", "7"]
    p.scene = {}
    dies, _ = crash_after(1)
    p.run_batch = lambda skill: dies
    with pytest.raises(RuntimeError):
        p.commission("sue", "bananas_in_bin")
    assert p.sweep("bananas_in_bin")[2] is not None
    p.scene = {"background_seed": 7}  # the world changed: that sweep's trials don't describe this scene
    assert p.sweep("bananas_in_bin")[2] is None


def test_robolab_runner_passes_extra_args_through(tmp_path, monkeypatch):
    FakeRoboLab.root, cmds = tmp_path, []

    class Recording(FakeRoboLab):
        def __init__(self, cmd, cwd, env, **kw):
            cmds.append(cmd)
            super().__init__(cmd, cwd, env, **kw)
    monkeypatch.setattr(runners.subprocess, "Popen", Recording)
    extra = ["--randomize-background", "--background-seed", "3"]
    runners.robolab("RedDishesInBinTask", {"ft": 5556}, root=str(tmp_path), extra_args=extra)({"ft": 1})
    assert cmds[0][-3:] == extra
