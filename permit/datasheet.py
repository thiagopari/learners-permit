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
# Net weight: 2.4 kg | Weighs only 3.6 lbs. (a retailer's product copy, Oct 22)
AFTER = re.compile(rf"(?:weigh(?:t|s|ing)?|mass)[^\d\n]{{0,40}}?{NUM}\s*{UNIT}\b", re.I)
# Weight (kg): 2.4 | Weight (lbs.) | 3.8 (a spec table as Tavily extracts it: cells separated by pipes)
BEFORE = re.compile(rf"(?:weight|mass)\s*\(\s*{UNIT}\.?\s*\)\s*[:=|]?\s*{NUM}", re.I)
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


def names_part(text, part_number):
    """Every word of the part number appears in the text as a whole token, ignoring case and the separators
    inside it: PN-48213 matches "PN 48213" or "pn48213", not "48213-04030"; "Makita XFD131" needs both words.
    Curly apostrophes count as straight ones (official pages write "Rock ‘n Play")."""
    curly = str.maketrans({chr(0x2018): "'", chr(0x2019): "'"})
    text, part_number = text.translate(curly), part_number.translate(curly)
    for word in part_number.split():
        pieces = [re.escape(x) for x in re.split(r"[-_./]", word) if x]
        if pieces and not re.search(r"(?<![A-Za-z0-9])" + r"[-_./ ]?".join(pieces) + r"(?![A-Za-z0-9])", text, re.I):
            return False
    return True


def check(part_number, limit_kg, call=tavily):
    # Tested on Oct 22 with a real tool: "<part> datasheet weight" at basic depth returned only company-profile
    # sites; "specifications" at advanced depth (2 credits instead of 1) found the manufacturer's own page.
    found = call("search", {"query": f"{part_number} specifications weight", "max_results": 5,
                            "search_depth": "advanced"})
    urls = [r["url"] for r in found.get("results", [])][:3]
    if not urls:
        return {"verdict": "unknown", "part": part_number, "reason": "no datasheet found"}
    pages = call("extract", {"urls": urls, "query": "weight mass kg"})
    # Only a page that names the part is evidence about it. On Oct 22 the made-up demo part PN-48213 matched a
    # Toyota leaf spring numbered 48213-04030 (19.7 kg) and would have blocked the pick citing it.
    about = [p for p in pages.get("results", []) if names_part(p.get("url", "") + " " + (p.get("raw_content") or ""),
                                                               part_number)]
    if not about:
        return {"verdict": "unknown", "part": part_number, "reason": "no page found that names this part",
                "sources": urls}
    seen = [(kg, ev, page["url"]) for page in about for kg, ev in masses(page.get("raw_content") or "")]
    if not seen:
        return {"verdict": "unknown", "part": part_number, "reason": "no mass in the extracted pages", "sources": urls}
    kg, evidence, url = max(seen)
    return {"verdict": "block" if kg > limit_kg else "within_limit", "part": part_number, "mass_kg": round(kg, 3),
            "limit_kg": limit_kg, "source": url, "evidence": evidence}
