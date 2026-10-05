import random
import types

import pytest

from cell.bandit import p_at_least
from permit import authz, datasheet, planner
from permit.licences import Licences
from permit.server import Permit


@pytest.fixture
def p(tmp_path):
    random.seed(0)
    return Permit(data_dir=str(tmp_path), clock=lambda: types.SimpleNamespace(tm_hour=14))


def licensed(p, skill, arm="n17_droid"):
    p.rates[skill][arm] = 1.0
    assert p.commission("sue", skill, arms=[arm])["status"] == "licensed"


def test_gate_math():
    assert round(p_at_least(38, 2), 3) == 0.993
    assert p_at_least(12, 0) < 0.95 <= p_at_least(16, 0)  # batches of 4: the first pass is at 16/16
    assert p_at_least(297, 0, 0.99) < 0.95 <= p_at_least(298, 0, 0.99)  # "unattended" tier: 298 straight


def test_refused_then_earned(p):
    p.rates["red_dishes_in_bin"].update(n17_droid=0.0, n17_droid_ft=1.0)
    assert p.commission("sue", "red_dishes_in_bin", arms=["n17_droid"])["status"] == "refused"
    e = p.execute(authz.AGENT, "red_dishes_in_bin", {})
    assert e["decision"] == "deny" and "not licensed" in e["reasons"][0] and e["escalate"]["command_hash"]
    assert p.commission("sue", "red_dishes_in_bin", arms=["n17_droid_ft"])["status"] == "licensed"
    assert p.execute(authz.AGENT, "red_dishes_in_bin", {})["decision"] == "allow"


def test_llm_cannot_supply_identity_or_approval(p):
    licensed(p, "bananas_in_bin")
    e = p.execute(authz.AGENT, "bananas_in_bin", {"speed_pct": 90, "role": "supervisor", "approver": "sue"})
    assert e["decision"] == "deny" and e["args"] == {"speed_pct": 90}


def test_approval_is_single_use_and_bound_to_one_command(p):
    token = p.approve("sue", "red_dishes_in_bin", {"speed_pct": 30})
    assert p.execute(authz.AGENT, "red_dishes_in_bin", {"speed_pct": 40}, approval=token)["decision"] == "deny"
    token = p.approve("sue", "red_dishes_in_bin", {"speed_pct": 30})  # the mismatch above burned the first one
    assert p.execute(authz.AGENT, "red_dishes_in_bin", {"speed_pct": 30}, approval=token)["decision"] == "allow"
    assert p.execute(authz.AGENT, "red_dishes_in_bin", {"speed_pct": 30}, approval=token)["decision"] == "deny"
    with pytest.raises(PermissionError):
        p.approve("olga", "red_dishes_in_bin", {})


def test_people_work_under_their_own_role(p):
    assert p.execute("olga", "red_dishes_in_bin", {"speed_pct": 70})["decision"] == "allow"  # no licence needed
    assert p.execute("olga", "red_dishes_in_bin", {"speed_pct": 90})["decision"] == "deny"
    p.sensors["human_in_zone"] = True
    assert p.execute("olga", "red_dishes_in_bin", {"speed_pct": 40})["decision"] == "deny"
    assert p.execute("olga", "red_dishes_in_bin", {"speed_pct": 20})["decision"] == "allow"


def test_datasheet_can_only_block(p):
    licensed(p, "bananas_in_bin")

    def page(text):
        return lambda endpoint, body: {"results": [{"url": "https://x/ds", "raw_content": text}]}

    p.check_part = lambda part, limit: datasheet.check(part, limit, call=page("Net weight: 2.4 kg"))
    e = p.execute(authz.AGENT, "bananas_in_bin", {"part_number": "PN-1"})
    assert e["decision"] == "deny" and "2.4 kg > 1.0 kg" in e["reasons"][0] and "https://x/ds" in e["reasons"][0]
    p.check_part = lambda part, limit: datasheet.check(part, limit, call=page("Weight 500 g"))
    assert p.execute(authz.AGENT, "bananas_in_bin", {"part_number": "PN-1"})["decision"] == "allow"
    # "within limit" never widens: an out-of-envelope speed stays denied
    assert p.execute(authz.AGENT, "bananas_in_bin", {"part_number": "PN-1", "speed_pct": 90})["decision"] == "deny"


def test_live_drift_revokes(p):
    licensed(p, "bananas_in_bin")
    p.rates["bananas_in_bin"]["n17_droid"] = 0.0
    for _ in range(8):
        p.execute(authz.AGENT, "bananas_in_bin", {})
    assert p.licences.data["bananas_in_bin"]["status"] == "revoked"
    assert p.execute(authz.AGENT, "bananas_in_bin", {})["decision"] == "deny"


def test_one_early_miss_does_not_revoke(tmp_path):
    lic = Licences(str(tmp_path / "l.json"))
    lic.data["s"] = {"status": "licensed", "thr": 0.8, "scope": {}, "live": []}
    lic.record_live("s", False)
    assert lic.data["s"]["status"] == "licensed"


def test_scope_limits_the_licence(tmp_path):
    lic = Licences(str(tmp_path / "l.json"))
    lic.data["s"] = {"status": "licensed", "thr": 0.8, "scope": {"color": ["red", "blue"]}, "live": []}
    assert lic.covers("s", {"color": "red"}) and not lic.covers("s", {"color": "green"}) and not lic.covers("s", {})


def test_planner_keeps_only_catalogue_skills_and_allowed_args():
    def reply(calls):
        tool_calls = [types.SimpleNamespace(function=types.SimpleNamespace(name=n, arguments=a)) for n, a in calls]
        msg = types.SimpleNamespace(tool_calls=tool_calls)
        create = lambda **kw: types.SimpleNamespace(choices=[types.SimpleNamespace(message=msg)])  # noqa: E731
        return types.SimpleNamespace(chat=types.SimpleNamespace(completions=types.SimpleNamespace(create=create)))

    skills = {"bananas_in_bin": {"instruction": "put the bananas in the bin"}}
    client = reply([("bananas_in_bin", '{"speed_pct": 30, "role": "supervisor"}'), ("open_door", "{}")])
    assert planner.plan("x", skills, client=client) == [{"skill": "bananas_in_bin", "args": {"speed_pct": 30}}]
