"""The Tavily recall check, on page shapes seen in real searches on Oct 29 (no network)."""
import json
import types

import pytest

from permit import authz, explainer, recall
from permit.server import Permit

AI = authz.AGENT
ROCK = "https://www.cpsc.gov/Recalls/2023/Fisher-Price-Reannounces-Recall-of-4-7-Million-Rock-n-Play-Sleepers"
GREASE = "https://www.cpsc.gov/Recalls/2025/Makita-USA-Inc-Recalls-Cordless-Grease-Guns-and-Grease-Gun-Hoses"
SAW = "https://www.cpsc.gov/Recalls/2002/cpsc-makita-usa-inc-announce-recall-to-repair-circular-saws"
FRUIT = "https://www.fda.gov/safety/recalls-market-withdrawals-safety-alerts/voluntary-recall-specific-frozen-fruit"
PAGES = {
    ROCK: ("Fisher-Price Reannounces Recall of 4.7 Million Rock ‘n Play Sleepers",
           "Fisher-Price is reannouncing the recall of Rock ‘n Play Sleepers."),
    GREASE: ("Makita U.S.A., Inc. Recalls Cordless Grease Guns and Grease Gun Hoses",
             "This recall involves Makita 18V LXT cordless grease guns, model XPG01Z. ... Recent recalls: "
             + "x" * 400 + " Recalled Scotch Thermal Laminator model number TL1302Z"),
    SAW: ("CPSC, Makita U.S.A. Inc. Announce Recall to Repair Circular Saws", "Makita circular saws, model 5007NB."),
    FRUIT: ("Voluntary Recall of Specific Frozen Fruit Products", "Mixes of strawberries, bananas and mango."),
}


def tavily_with(*urls):
    def call(endpoint, body):
        if endpoint == "search":
            return {"results": [{"url": u, "title": PAGES[u][0], "content": ""} for u in urls]}
        return {"results": [{"url": u, "raw_content": PAGES[u][1]} for u in body["urls"]]}
    return call


@pytest.mark.parametrize("item,urls,verdict,source", [
    ("Fisher-Price Rock 'n Play", [ROCK], "block", ROCK),     # named in the notice's title (curly apostrophe)
    ("Makita XPG01Z", [GREASE, SAW], "block", GREASE),         # a model number named in the notice's body
    ("Makita XFD131", [SAW, GREASE], "none_found", None),     # recalls of other Makita tools
    ("bananas", [FRUIT], "none_found", None),                  # only mentioned in a fruit-mix recall's body
    ("Makita TL1302Z", [GREASE], "none_found", None),          # a laminator in the page's sidebar, far from "Makita"
    ("Makita XFD131", [], "none_found", None),
])
def test_only_a_notice_that_names_the_item_blocks(item, urls, verdict, source):
    v = recall.check(item, call=tavily_with(*urls))
    assert v["verdict"] == verdict and v.get("source") == source


def test_the_search_asks_only_official_recall_sites():
    seen = []
    recall.check("X1", call=lambda endpoint, body: seen.append(body) or {"results": []})
    assert set(seen[0]["include_domains"]) == set(recall.OFFICIAL) and "recall" in seen[0]["query"]


def permit(tmp_path, notice):
    p = Permit(data_dir=str(tmp_path), clock=lambda: types.SimpleNamespace(tm_hour=14), lock_timeout=0.2,
               check_recall=lambda item: recall.check(item, call=notice))
    p.rates["bananas_in_bin"]["n17_droid"] = 1.0
    p.commission("sue", "bananas_in_bin")
    return p


def test_a_recalled_item_is_blocked_cited_and_explained(tmp_path):
    p = permit(tmp_path, tavily_with(ROCK))
    e = p.execute(AI, "bananas_in_bin", {"part_number": "Fisher-Price Rock 'n Play"}, requester="olga")
    assert e["decision"] == "deny" and e["reasons"][0].startswith("recall: Fisher-Price Reannounces Recall")
    assert ROCK in e["reasons"][0] and e["recall"]["verdict"] == "block"
    assert "official recall notice names it" in e["explanation"] and ROCK in e["explanation"]
    f = explainer.facts(e, p.licences.data["bananas_in_bin"])
    assert f["event"] == "blocked" and f["recall"]["source"] == ROCK and "check its lot" in f["next_step"]


def test_no_recall_never_widens_anything(tmp_path):
    p = permit(tmp_path, tavily_with(SAW))
    assert p.execute(AI, "bananas_in_bin", {"part_number": "Makita XFD131"}, requester="olga")["decision"] == "allow"
    e = p.execute(AI, "bananas_in_bin", {"part_number": "Makita XFD131", "speed_pct": 90}, requester="olga")
    assert e["decision"] == "deny" and e["recall"] is None  # outside the envelope: not even looked up
    p.licences.data["bananas_in_bin"]["status"] = "revoked"
    assert p.execute(AI, "bananas_in_bin", {"part_number": "Makita XFD131"}, requester="olga")["decision"] == "deny"
    audit = [json.loads(line) for line in open(p.audit_path)]
    assert any((x.get("recall") or {}).get("verdict") == "none_found" for x in audit)


def test_a_heavy_recalled_item_reports_both_reasons(tmp_path):
    """On Oct 29 both real recalled items were also over the skill's mass limit; the recall must still show."""
    p = permit(tmp_path, tavily_with(ROCK))
    p.check_part = lambda part, limit: {"verdict": "block", "part": part, "mass_kg": 11.3, "limit_kg": limit,
                                        "source": "https://example.com/spec"}
    e = p.execute(AI, "bananas_in_bin", {"part_number": "Fisher-Price Rock 'n Play"}, requester="olga")
    assert [r.split(":")[0] for r in e["reasons"]] == ["datasheet", "recall"]
    assert "official recall notice names it" in e["explanation"]  # the recall is the reason that's explained
