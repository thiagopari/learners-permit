"""Tavily datasheet check. It can only narrow: if any weight on the found pages exceeds the skill's limit, the
part is blocked, citing the page. Any other outcome leaves the decision to RBAC and the licence.
Masses are parsed from Tavily's extracted page text, never from an LLM. Taking the largest one is conservative.
"""
import json
import os
import re
import urllib.request

API = "https://api.tavily.com"
NUM = r"(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:[.,]\d+)?)"   # 1,250 | 1,250.5 | 2.4 | 2,4
UNIT = r"(kgs?|kilograms?|g|grams?|lbs?|pounds?)"
AFTER = re.compile(rf"(?:weight|mass)[^\d\n]{{0,40}}?{NUM}\s*{UNIT}\b", re.I)    # Net weight: 2.4 kg
BEFORE = re.compile(rf"(?:weight|mass)\s*\(\s*{UNIT}\s*\)\s*[:=]?\s*{NUM}", re.I)  # Weight (kg): 2.4
TO_KG = {"k": 1.0, "g": 0.001, "l": 0.4536, "p": 0.4536}  # by the unit's first letter


def number(text):
    if re.fullmatch(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?", text):
        return float(text.replace(",", ""))  # thousands separators
    return float(text.replace(",", "."))      # decimal comma


def masses(text):
    for m in AFTER.finditer(text):
        yield number(m.group(1)) * TO_KG[m.group(2)[0].lower()], m.group(0)
    for m in BEFORE.finditer(text):
        yield number(m.group(2)) * TO_KG[m.group(1)[0].lower()], m.group(0)


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
    seen = [(kg, ev, page["url"]) for page in pages.get("results", []) for kg, ev in masses(page.get("raw_content") or "")]
    if not seen:
        return {"verdict": "unknown", "part": part_number, "reason": "no mass in the extracted pages", "sources": urls}
    kg, evidence, url = max(seen)
    return {"verdict": "block" if kg > limit_kg else "within_limit", "part": part_number, "mass_kg": round(kg, 3),
            "limit_kg": limit_kg, "source": url, "evidence": evidence}
