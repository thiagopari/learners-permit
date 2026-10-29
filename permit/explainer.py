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
          "given; quote numbers exactly as written there and add no others. Write for a person: no JSON keys or "
          "field names (say \"40% speed\", not \"speed_pct 40\"), and name skills in plain words (\"the red dishes "
          "skill\", not \"red_dishes_in_bin\"). Don't soften the decision, don't suggest bypassing it, and don't use "
          "markdown. Licences belong to skills, never to people: never say a person lacks a licence. Confidence is how sure "
          "the system is about a success rate; it is not itself a success rate.")
NUMBER = re.compile(r"\d+(?:\.\d+)?")
THINK = re.compile(r"<think>.*?</think>", re.S)
NARROW_NBSP, NBSP = chr(0x202F), chr(0xA0)


def needs(entry):
    """Explain what a supervisor has to act on: every denial and every revocation."""
    return entry.get("decision") == "deny" or entry.get("action") == "revoke"


def facts(entry, licence):
    """The only input Nemotron sees: what the control plane decided, and the evidence it decided on."""
    ctx = entry.get("context") or {}
    sheet, notice = entry.get("datasheet") or {}, entry.get("recall") or {}
    heavy, recalled = sheet.get("verdict") == "block", notice.get("verdict") == "block"
    blocked = heavy or recalled
    event = "revoked" if entry.get("action") == "revoke" else "blocked" if blocked else "refused"
    f = {"event": event, "skill": entry["skill"], "skill_name": plain(entry["skill"]),
         "reasons": [r for r in entry.get("reasons", []) if not r.startswith(("datasheet:", "recall:"))]}
    if event != "revoked":  # a revocation is about the skill, not about whoever's run tipped it
        f["requested_by"] = entry.get("requester") or entry.get("actor")
    if ctx:
        f["request"] = {k: ctx[k] for k in ("speed_pct", "hour", "human_in_zone", "requester_role") if k in ctx}
    if heavy:
        f["datasheet"] = {"part": sheet.get("part"), "mass_kg": sheet["mass_kg"], "limit_kg": sheet["limit_kg"],
                          "source": sheet["source"]}
    if recalled:
        f["recall"] = {"item": notice["item"], "notice": notice["title"], "source": notice["source"]}
    if licence:
        # Pre-worded evidence: given a bare "p": 0.9775, Nemotron called it "a 97.75% success rate" (Oct 22 test).
        live, bar, sure = licence.get("live", []), round(licence["thr"] * 100), round(licence["p"] * 100, 2)
        f["licence"] = {"status": licence["status"], "tier": licence["tier"], "belongs_to": "the skill, not a person",
                        "evidence": f"{licence['successes']} of {licence['trials']} commissioning trials passed, so "
                                    f"the system is {sure}% confident the skill's true success rate is at least "
                                    f"{bar}%; a licence needs 95% confidence",
                        "bar_pct": bar, "trials": licence["trials"], "successes": licence["successes"],
                        "confidence_rate_meets_bar": licence["p"], "confidence_needed": 0.95,
                        "live_runs": len(live), "live_successes": sum(live)}
        if licence.get("reason"):
            f["licence"]["reason"] = licence["reason"]
        if licence["status"] == "revoked":  # the revocation itself, and any refusal while revoked
            floor = round(licence["revoke_below"] * 100)
            f["licence"]["revoke_below_pct"] = floor
            # The commissioning numbers no longer describe the skill; given them, Nemotron mixed the two rules up.
            if licence.get("revoked_by") == "scene":  # the vision check saw a different scene; the success rate didn't decide it
                f["licence"]["evidence"] = (f"a vision check compared the cell after a live run with the scene the "
                                            f"skill was commissioned in, and found that {licence['reason']}; the "
                                            f"licence is evidence about the commissioning scene only")
            else:
                f["licence"]["evidence"] = (f"{sum(live)} of the last {len(live)} live runs succeeded, so the system "
                                            f"is at least 95% confident the skill's live success rate has fallen "
                                            f"below {floor}%, the floor for a {licence['tier']} licence")
            for stale in ("confidence_rate_meets_bar", "confidence_needed", "trials", "successes", "bar_pct"):
                f["licence"].pop(stale)
            if licence.get("revoked_by") == "scene":
                # No success-rate rule decided it. Given the 70% floor and the live counts anyway, Nemotron wrote that
                # a scene change "triggered an automatic revocation below the 70% threshold" (Oct 28, real run).
                for stale in ("revoke_below_pct", "live_runs", "live_successes"):
                    f["licence"].pop(stale, None)
    else:
        f["licence"] = {"status": "none", "belongs_to": "the skill, not a person",
                        "evidence": "the skill has never been commissioned, so it has no licence"}
    if event == "revoked":
        f["next_step"] = "until a supervisor commissions the skill again, the AI asks a person before every run"
    elif recalled:
        f["next_step"] = ("web evidence can only block, so no approval overrides this; set the item aside and check "
                          "its lot against the recall notice")
    elif blocked:
        f["next_step"] = "web evidence can only block, so no approval overrides this; use a skill rated for the part"
    elif entry.get("escalate"):
        f["next_step"] = "a supervisor can approve this exact command once; the approval is single use and lasts 10 minutes"
    else:
        f["next_step"] = "this request is outside the requester's own role"
    return f


def plain(skill):
    """red_dishes_in_bin -> "red dishes in bin": what a supervisor would call it."""
    return skill.replace("_", " ")


def offline(f):
    """The template answer: used with no key, on an error, or when Nemotron's answer isn't grounded."""
    lic = f["licence"]
    if f["event"] == "revoked":
        return (f"The licence for {f['skill_name']} was revoked: {lic['evidence']}. "
                f"Next: {f['next_step']}.")
    if f["event"] == "blocked" and "recall" in f:
        r = f["recall"]
        return (f"The pick of {r['item']} was blocked: an official recall notice names it ({r['notice']}; source: "
                f"{r['source']}). Next: {f['next_step']}.")
    if f["event"] == "blocked":
        d = f["datasheet"]
        return (f"The pick of part {d['part']} was blocked: its datasheet lists {d['mass_kg']} kg, over the "
                f"{d['limit_kg']} kg limit for {f['skill_name']} (source: {d['source']}). Next: {f['next_step']}.")
    why = "; ".join(f["reasons"]) or "outside the AI's envelope"
    if lic["status"] == "none":
        evidence = " The skill has never been commissioned."
    elif lic["status"] == "licensed":
        evidence = ""
    elif lic["status"] == "revoked":
        evidence = f" Its licence was revoked: {lic.get('reason', 'live results slipped')}."
    else:
        evidence = (f" Its licence is {lic['status']}: {lic['successes']}/{lic['trials']} trials passed, and "
                    f"P(rate >= {lic['bar_pct']}%) = {lic['confidence_rate_meets_bar']}, against the "
                    f"{lic['confidence_needed']} needed.")
    return f"The AI did not run {f['skill_name']} for {f['requested_by']}: {why}.{evidence} Next: {f['next_step']}."


def grounded(text, f):
    """Every number Nemotron wrote must appear in the facts, so it can't invent a success rate or a weight. A number
    may be restated as a percentage or a fraction (0.95 <-> 95%), nothing else."""
    given = [float(n) for n in NUMBER.findall(json.dumps(f))]
    allowed = {round(v * k, 6) for v in given for k in (1, 100, 0.01)}
    return all(round(float(n), 6) in allowed for n in NUMBER.findall(text))


def licence_on_a_person(text, f):
    """True if the answer says a person has, holds or lacks a licence. Licences belong to skills; Nemotron wrote
    "she does not have a license" and "Olga has a supervised licence" on Oct 22 despite the prompt saying so."""
    people = [re.escape(str(f["requested_by"]))] if f.get("requested_by") else []
    who = r"\b(?:" + "|".join(people + ["she", "he", "they", "the operator", "the requester", "the user"]) + r")\b"
    claim = r"\b(?:has|have|holds?|hold|lacks?|doesn.t have|does not have|didn.t have|did not have|without)\b"
    noun = r"\blicen[cs]es?\b"  # the noun only: "the skill, which has never been licensed" is a correct sentence
    return re.search(who + r"[^.]{0,40}?" + claim + r"[^.]{0,40}?" + noun, text, re.I) is not None


class CutOff(Exception):
    """The answer hit the token limit: a half sentence is worse than the template."""


def nemotron(f, client=None):
    if client is None:
        from openai import OpenAI
        client = OpenAI(base_url=planner.BASE_URL, api_key=os.environ["NEBIUS_API_KEY"], timeout=20, max_retries=1)
    # Reasoning off: measured on Token Factory, it spent ~250 hidden tokens before a 3-sentence answer (and could run
    # past the limit); off, the answer took 1.3 s instead of 3-4 s. The planner keeps its reasoning.
    r = client.chat.completions.create(
        model=planner.MODEL, temperature=0.2, max_tokens=300,
        extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": json.dumps(f)}])
    choice = r.choices[0]
    if getattr(choice, "finish_reason", None) == "length":
        raise CutOff()
    return tidy(choice.message.content or "")


def tidy(text):
    """Drop any <think> block, turn narrow no-break spaces (seen before numbers) into plain ones, collapse spaces."""
    text = THINK.sub("", text).replace(NARROW_NBSP, " ").replace(NBSP, " ")
    return " ".join(text.split())


def explain(f, llm=None):
    """(text, by). by is "nemotron" or says why the template was used instead."""
    fallback = offline(f)
    if llm is None:
        return fallback, "template"
    try:
        text = llm(f)
    except CutOff:
        return fallback, "template (Nemotron's answer was cut off)"
    except Exception as e:  # Token Factory down, no key, timeout: the decision stands either way
        return fallback, f"template (Nemotron error: {type(e).__name__})"
    if not text:
        return fallback, "template (Nemotron gave no answer)"
    if not grounded(text, f):
        return fallback, "template (Nemotron's answer quoted numbers not in the record)"
    if licence_on_a_person(text, f):
        return fallback, "template (Nemotron's answer gave a person the skill's licence)"
    return text, "nemotron"
