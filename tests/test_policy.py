import pytest

from permit import authz

A = authz.AGENT
SUE = {"__entity": {"type": "User", "id": "sue"}}
OLGA = {"__entity": {"type": "User", "id": "olga"}}
BASE = dict(object_class="housing", bin="B", speed_pct=40, hour=14, human_in_zone=False, skill_licensed=True)

CASES = [
    ("AI in envelope", A, "pick_place", "cell1", {}, True),
    ("AI wrong object", A, "pick_place", "cell1", {"object_class": "valve"}, False),
    ("AI wrong bin", A, "pick_place", "cell1", {"bin": "C"}, False),
    ("AI too fast", A, "pick_place", "cell1", {"speed_pct": 70}, False),
    ("AI after hours", A, "pick_place", "cell1", {"hour": 23}, False),
    ("AI unlicensed skill", A, "pick_place", "cell1", {"skill_licensed": False}, False),
    ("AI unlicensed + supervisor approval", A, "pick_place", "cell1", {"skill_licensed": False, "approver": SUE}, True),
    ("AI + operator 'approval'", A, "pick_place", "cell1", {"object_class": "valve", "approver": OLGA}, False),
    ("AI approved but too fast", A, "pick_place", "cell1", {"approver": SUE, "speed_pct": 70}, False),
    ("AI change_mode even approved", A, "change_mode", "cell1", {"approver": SUE}, False),
    ("operator 70%", "olga", "pick_place", "cell1", {"speed_pct": 70}, True),
    ("operator 90%", "olga", "pick_place", "cell1", {"speed_pct": 90}, False),
    ("person in cell at 40%", "olga", "pick_place", "cell1", {"human_in_zone": True}, False),
    ("person in cell at 20%", "olga", "pick_place", "cell1", {"human_in_zone": True, "speed_pct": 20}, True),
    ("supervisor change_mode", "sue", "change_mode", "cell1", {}, True),
    ("operator change_mode", "olga", "change_mode", "cell1", {}, False),
    ("maintenance in maint zone", "max", "change_mode", "maint", {"speed_pct": 20}, True),
    ("maintenance in cell1", "max", "change_mode", "cell1", {"speed_pct": 20}, False),
]


@pytest.mark.parametrize("name,user,action,zone,ctx,allowed", CASES, ids=[c[0] for c in CASES])
def test_policy(name, user, action, zone, ctx, allowed):
    assert authz.decide(user, action, zone, {**BASE, **ctx}) is allowed


@pytest.mark.parametrize("missing", ["human_in_zone", "speed_pct", "skill_licensed"])
def test_fails_closed_when_context_is_missing(missing):
    assert authz.decide(A, "pick_place", "cell1", {k: v for k, v in BASE.items() if k != missing}) is False
