"""The video story end to end, with no GPU and no API keys: refuse -> earn -> block -> revoke.

Uses the mock runner (coin flips at the rates in permit/skills.json). If NEBIUS_API_KEY / TAVILY_API_KEY are
set, the planner and the explanations (Nemotron) and the datasheet check (Tavily) are real. Run from the repo root:
    python demo/four_beats.py
"""
import os
import random
import sys
import tempfile
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from permit import datasheet, envfile, explainer, planner  # noqa: E402
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
        for x in (e, e.get("revocation") or {}):
            if x.get("explanation"):
                print(f"         {x['explained_by']}: {x['explanation']}")


def card(skill, lic):
    print(f"   {skill}: {lic['status'].upper()} on {lic['successes']}/{lic['trials']} trials, "
          f"P(rate >= {lic['thr']}) = {lic['p']}")


envfile.load()  # the project's .env, if any: real Nemotron and Tavily
random.seed(7)
llm, web = bool(os.environ.get("NEBIUS_API_KEY")), bool(os.environ.get("TAVILY_API_KEY"))
# The block beat needs a part the web actually documents: a made-up number finds no page that names it, so with real
# services it's a real item (a cordless drill, ~1.7 kg on its retailer's spec sheet, over the skill's 1.0 kg limit).
# Nemotron reads the part out of the order; the offline planner only spots numbers like PN-48213.
live_block = llm and web
part = os.environ.get("LP_DEMO_PART", "Makita XFD131") if live_block else "PN-48213"
p = Permit(data_dir=tempfile.mkdtemp(), clock=lambda: SimpleNamespace(tm_hour=14),  # demo clock: inside 06-22
           plan=planner.plan if llm else None, explain=explainer.nemotron if llm else None,
           check_part=datasheet.check if live_block
           else (lambda part, limit: datasheet.check(part, limit, call=canned)))
print(f"planner and explanations: {'Nemotron on Token Factory' if llm else 'offline stand-ins'} | "
      f"datasheets: {'Tavily, live' if live_block else 'offline stand-in'}\n")

print("0. Commission the zero-shot policy on both skills (Nebius eval sweeps; mocked here)")
card("bananas_in_bin", p.commission("sue", "bananas_in_bin"))
card("red_dishes_in_bin", p.commission("sue", "red_dishes_in_bin", arms=["n17_droid"]))

print("1. REFUSE: the order needs a skill that hasn't earned a licence")
show(p.order("olga", "Put the red dishes in the bin"))

print("2. EARN: the fine-tuned policy passes the gate")
card("red_dishes_in_bin", p.commission("sue", "red_dishes_in_bin", arms=["n17_droid_ft"]))
show(p.order("olga", "Put the red dishes in the bin"))

print("3. BLOCK: the datasheet says the part is too heavy for the skill")
show(p.order("olga", f"Put the bananas in the bin. The item is part {part}."))

print("4. REVOKE: perturb the scene; live results slip and the licence is pulled")
p.rates["red_dishes_in_bin"]["n17_droid_ft"] = 0.1
for _ in range(50):
    runs = p.order("olga", "Put the red dishes in the bin")
    if any(e.get("revocation") for e in runs):
        show(runs)
        break
show(p.order("olga", "Put the red dishes in the bin"))
print(f"\naudit trail: {p.audit_path}")
