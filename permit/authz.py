"""Cedar decisions. People, roles and the AI agent are defined here, server-side: the LLM can't name or claim any."""
import pathlib

import cedarpy

POLICY = pathlib.Path(__file__).with_name("policy.cedar").read_text()
PEOPLE = {"sue": "supervisor", "olga": "operator", "max": "maintenance"}  # demo staff; replace for a real cell
AGENT = "nemotron"


def _entity(kind, uid, roles=()):
    return {"uid": {"type": kind, "id": uid}, "attrs": {}, "parents": [{"type": "Role", "id": r} for r in roles]}


ENTITIES = ([_entity("Role", r) for r in ("ai_agent", "operator", "supervisor", "maintenance")]
            + [_entity("Zone", "cell1"), _entity("Zone", "maint"), _entity("Agent", AGENT, ["ai_agent"])]
            + [_entity("User", user, [role]) for user, role in PEOPLE.items()])


def decide(user, action, zone, context):
    who = f'Agent::"{AGENT}"' if user == AGENT else f'User::"{user}"'
    r = cedarpy.is_authorized({"principal": who, "action": f'Action::"{action}"', "resource": f'Zone::"{zone}"',
                               "context": context}, POLICY, ENTITIES)
    return r.decision == cedarpy.Decision.Allow
