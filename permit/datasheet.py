"""Tavily datasheet check. It can only narrow: a part heavier than the skill's limit is blocked, citing the page
the mass came from. Any other outcome leaves the decision to RBAC and the licence.
The mass is parsed from Tavily's extracted page text, never from an LLM.
"""
import json
import os
import re
import urllib.request

API = "https://api.tavily.com"
MASS = re.compile(r"(?:weight|mass)\D{0,40}?(\d+(?:\.\d+)?)\s*(kg|g|lbs?)\b", re.I)
TO_KG = {"kg": 1.0, "g": 0.001, "lb": 0.4536, "lbs": 0.4536}


def tavily(endpoint, body):
    req = urllib.request.Request(f"{API}/{endpoint}", data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {os.environ['TAVILY_API_KEY']}",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def check(part_number, limit_kg, call=tavily):
    found = call("search", {"query": f"{part_number} datasheet weight", "max_results": 5})
    urls = [r["url"] for r in found.get("results", [])][:3]
    if not urls:
        return {"verdict": "unknown", "part": part_number, "reason": "no datasheet found"}
    pages = call("extract", {"urls": urls, "query": "weight mass kg"})
    for page in pages.get("results", []):
        m = MASS.search(page.get("raw_content") or "")
        if m:
            kg = round(float(m.group(1)) * TO_KG[m.group(2).lower()], 3)
            return {"verdict": "block" if kg > limit_kg else "within_limit", "part": part_number, "mass_kg": kg,
                    "limit_kg": limit_kg, "source": page["url"], "evidence": m.group(0)}
    return {"verdict": "unknown", "part": part_number, "reason": "no mass in the extracted pages", "sources": urls}
