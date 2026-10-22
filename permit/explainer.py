"""Nemotron's second job: tell the supervisor, in plain English, why the AI was refused, blocked or revoked.

The explanation is advisory. It is written after the decision, from facts the control plane itself produced, and it
can't change anything. Nemotron sees only those facts: never the person's order text, never raw web page text, so
neither can steer what it says. An answer that quotes a number not in the facts is discarded, and a template answer
is used instead; the same happens with no key or when Token Factory is down.
"""
import json
import os
import re

from permit import planner

SYSTEM = ("You explain a robot cell's safety decisions to the shift supervisor. You get one decision as JSON facts. "
          "In two or three plain sentences, say what happened, why, and what can be done next. Use only the facts "
          "given; quote numbers exactly as written there and add no others. Don't soften the decision, don't suggest "
          "bypassing it, and don't use markdown.")
NUMBER = re.compile(r"\d+(?:\.\d+)?")
THINK = re.compile(r"<think>.*?</think>", re.S)


def needs(entry):
    """Explain what a supervisor has to act on: every denial and every revocation."""
    return entry.get("decision") == "deny" or entry.get("action") == "revoke"


def facts(entry, licence):
    """The only input Nemotron sees: what the control plane decided, and the evidence it decided on."""
    ctx = entry.get("context") or {}
    sheet = entry.get("datasheet") or {}
    blocked = sheet.get("verdict") == "block"
    event = "revoked" if entry.get("action") == "revoke" else "blocked" if blocked else "refused"
    f = {"event": event, "skill": entry["skill"],
         "reasons": [r for r in entry.get("reasons", []) if not r.startswith("datasheet:")]}
    if event != "revoked":  # a revocation is about the skill, not about whoever's run tipped it
        f["for"] = entry.get("requester") or entry.get("actor")
    if ctx:
        f["request"] = {k: ctx[k] for k in ("speed_pct", "hour", "human_in_zone", "requester_role") if k in ctx}
    if blocked:
        f["datasheet"] = {"part": sheet.get("part"), "mass_kg": sheet["mass_kg"], "limit_kg": sheet["limit_kg"],
                          "source": sheet["source"]}
    if licence:
        live = licence.get("live", [])
        f["licence"] = {"status": licence["status"], "tier": licence["tier"], "bar_pct": round(licence["thr"] * 100),
                        "trials": licence["trials"], "successes": licence["successes"], "p": licence["p"],
                        "confidence_needed": 0.95, "live_runs": len(live), "live_successes": sum(live)}
        if licence.get("reason"):
            f["licence"]["reason"] = licence["reason"]
        if event == "revoked":
            f["licence"]["revoke_below_pct"] = round(licence["revoke_below"] * 100)
    else:
        f["licence"] = {"status": "none"}
    if event == "revoked":
        f["next_step"] = "until a supervisor commissions the skill again, the AI asks a person before every run"
    elif blocked:
        f["next_step"] = "web evidence can only block, so no approval overrides this; use a skill rated for the part"
    elif entry.get("escalate"):
        f["next_step"] = "a supervisor can approve this exact command once; the approval is single use and lasts 10 minutes"
    else:
        f["next_step"] = "this request is outside the requester's own role"
    return f


def offline(f):
    """The template answer: used with no key, on an error, or when Nemotron's answer isn't grounded."""
    lic = f["licence"]
    if f["event"] == "revoked":
        return (f"The licence for {f['skill']} was revoked: {lic.get('reason', 'live results slipped')}. "
                f"Live runs now show, with 95% confidence, a success rate under the {lic['revoke_below_pct']}% floor for a "
                f"{lic['tier']} licence. "
                f"Next: {f['next_step']}.")
    if f["event"] == "blocked":
        d = f["datasheet"]
        return (f"The pick of part {d['part']} was blocked: its datasheet lists {d['mass_kg']} kg, over the "
                f"{d['limit_kg']} kg limit for {f['skill']} (source: {d['source']}). Next: {f['next_step']}.")
    why = "; ".join(f["reasons"]) or "outside the AI's envelope"
    if lic["status"] == "none":
        evidence = " The skill has never been commissioned."
    elif lic["status"] == "licensed":
        evidence = ""
    elif lic["status"] == "revoked":
        evidence = f" Its licence was revoked: {lic.get('reason', 'live results slipped')}."
    else:
        evidence = (f" Its licence is {lic['status']}: {lic['successes']}/{lic['trials']} trials passed, and "
                    f"P(rate >= {lic['bar_pct']}%) = {lic['p']}, against the {lic['confidence_needed']} needed.")
    return f"The AI did not run {f['skill']} for {f['for']}: {why}.{evidence} Next: {f['next_step']}."


def grounded(text, f):
    """Every number Nemotron wrote must appear in the facts, so it can't invent a success rate or a weight. A number
    may be restated as a percentage or a fraction (0.95 <-> 95%), nothing else."""
    given = [float(n) for n in NUMBER.findall(json.dumps(f))]
    allowed = {round(v * k, 6) for v in given for k in (1, 100, 0.01)}
    return all(round(float(n), 6) in allowed for n in NUMBER.findall(text))


def nemotron(f, client=None):
    if client is None:
        from openai import OpenAI
        client = OpenAI(base_url=planner.BASE_URL, api_key=os.environ["NEBIUS_API_KEY"], timeout=20, max_retries=1)
    r = client.chat.completions.create(model=planner.MODEL, temperature=0.2, max_tokens=600, messages=[
        {"role": "system", "content": SYSTEM}, {"role": "user", "content": json.dumps(f)}])
    text = THINK.sub("", r.choices[0].message.content or "")
    return " ".join(text.split())


def explain(f, llm=None):
    """(text, by). by is "nemotron" or says why the template was used instead."""
    fallback = offline(f)
    if llm is None:
        return fallback, "template"
    try:
        text = llm(f)
    except Exception as e:  # Token Factory down, no key, timeout: the decision stands either way
        return fallback, f"template (Nemotron error: {type(e).__name__})"
    if not text:
        return fallback, "template (Nemotron gave no answer)"
    if not grounded(text, f):
        return fallback, "template (Nemotron's answer quoted numbers not in the record)"
    return text, "nemotron"
