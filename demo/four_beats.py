"""The video story end to end, with no GPU and no API keys: refuse -> earn -> block -> revoke.

Uses the mock runner (coin flips at the rates in permit/skills.json). If NEBIUS_API_KEY / TAVILY_API_KEY are
set, the planner (Nemotron) and the datasheet check (Tavily) are real. Run from the repo root:
    python demo/four_beats.py
"""
import os
import random
import sys
import tempfile
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from permit import datasheet, planner  # noqa: E402
from permit.server import Permit  # noqa: E402

PAGE = "https://example.com/datasheets/PN-48213 (offline stand-in for Tavily)"


def canned(endpoint, body):
    """Offline stand-in for Tavily's search and extract, so the real mass parser still runs."""
    if endpoint == "search":
        return {"results": [{"url": PAGE}]}
    return {"results": [{"url": PAGE, "raw_content": "PN-48213 produce crate. Net weight: 2.4 kg. 40 x 30 cm."}]}


def show(entries):
    for e in entries:
        why = "; ".join(e.get("reasons") or []) or e.get("result")
        print(f"   {e['decision'].upper():5} {e['skill']} {e.get('args') or ''} -> {why}  [licence: {e['licence']}]")


def card(skill, lic):
    print(f"   {skill}: {lic['status'].upper()} on {lic['successes']}/{lic['trials']} trials, "
          f"P(rate >= {lic['thr']}) = {lic['p']}")


random.seed(7)
p = Permit(data_dir=tempfile.mkdtemp(), clock=lambda: SimpleNamespace(tm_hour=14),  # demo clock: inside 06-22
           plan=planner.plan if os.environ.get("NEBIUS_API_KEY") else None,
           check_part=datasheet.check if os.environ.get("TAVILY_API_KEY")
           else (lambda part, limit: datasheet.check(part, limit, call=canned)))

print("0. Commission the zero-shot policy on both skills (Nebius eval sweeps; mocked here)")
card("bananas_in_bin", p.commission("sue", "bananas_in_bin"))
card("red_dishes_in_bin", p.commission("sue", "red_dishes_in_bin", arms=["n17_droid"]))

print("1. REFUSE: the order needs a skill that hasn't earned a licence")
show(p.order("olga", "Put the red dishes in the bin"))

print("2. EARN: the fine-tuned policy passes the gate")
card("red_dishes_in_bin", p.commission("sue", "red_dishes_in_bin", arms=["n17_droid_ft"]))
show(p.order("olga", "Put the red dishes in the bin"))

print("3. BLOCK: the datasheet says the part is too heavy for the skill")
show(p.order("olga", "Put the bananas in the bin. Crate PN-48213."))

print("4. REVOKE: perturb the scene; live results slip and the licence is pulled")
p.rates["red_dishes_in_bin"]["n17_droid_ft"] = 0.1
for _ in range(50):
    if p.licences.data["red_dishes_in_bin"]["status"] != "licensed":
        break
    p.order("olga", "Put the red dishes in the bin")
print("   " + p.licences.data["red_dishes_in_bin"].get("reason", "still licensed"))
show(p.order("olga", "Put the red dishes in the bin"))
print(f"\naudit trail: {p.audit_path}")
