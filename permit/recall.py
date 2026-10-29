"""Tavily recall check: before the AI picks an item, look for an official recall notice that names it.

It can only narrow, like the datasheet check: a notice blocks the pick and is cited; finding none allows nothing by
itself (RBAC and the licence still decide). Only official recall sites count (OFFICIAL), and only a page that names
the exact item: searching "Makita XFD131 recall" returns CPSC recalls of other Makita tools, and "bananas recall"
returns FDA recalls of fruit purees (Oct 29), none of which is about the item being picked.
"""
import re

from permit.datasheet import names_part, tavily

OFFICIAL = ["cpsc.gov", "fda.gov", "fsis.usda.gov", "recalls.gov", "nhtsa.gov"]
RECALL = re.compile(r"\brecall", re.I)


def near(text, models, reach=200):
    """Text around each mention of a model number. The rest of the item's name must be in the same stretch:
    a CPSC page's "recent recalls" sidebar listed a Scotch laminator, TL1302Z, on a Makita recall page, and
    matching "Makita" and "TL1302Z" anywhere on the page cited the wrong notice (Oct 29)."""
    for model in models:
        for m in re.finditer(re.escape(model), text, re.I):
            yield text[max(0, m.start() - reach): m.end() + reach]


def check(item, call=tavily):
    found = call("search", {"query": f"{item} recall", "max_results": 5, "search_depth": "advanced",
                            "include_domains": OFFICIAL})
    results = found.get("results", [])
    if not results:
        return {"verdict": "none_found", "item": item, "reason": "no official recall notice found"}
    titles = {r["url"]: r.get("title", "") for r in results}
    pages = call("extract", {"urls": list(titles)[:3]})
    texts = {p["url"]: (p.get("raw_content") or "") for p in pages.get("results", [])}
    for r in results:  # a page Tavily couldn't extract is judged on its search snippet
        texts.setdefault(r["url"], r.get("content") or "")
    # The item must be the notice's subject (named in its title), or, for an item with a model number, named anywhere
    # on the page (notices list affected models in the body). A generic name in the body isn't enough: "bananas"
    # appears in an FDA recall of frozen fruit mixes, which says nothing about a crate of bananas (Oct 29).
    models = [word for word in item.split() if re.search(r"\d", word)]
    for url, text in texts.items():
        title = titles.get(url, "")
        named = names_part(title, item) or any(names_part(window, item) for window in near(text, models))
        if named and RECALL.search(f"{title} {text}"):
            return {"verdict": "block", "item": item, "title": title or url, "source": url}
    return {"verdict": "none_found", "item": item, "reason": "official recall pages found, none naming this item",
            "sources": list(texts)}
