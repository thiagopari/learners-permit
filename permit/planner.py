"""Nemotron (on Nebius Token Factory) turns an order into skill calls. It sees only the skill catalogue: it can't
name a role, an approver or an unlisted skill, and any argument outside ARGS is dropped.
"""
import json
import os
import re

BASE_URL = os.environ.get("TOKEN_FACTORY_BASE_URL", "https://api.tokenfactory.nebius.com/v1/")
MODEL = os.environ.get("NEMOTRON_MODEL", "nvidia/nemotron-3-super-120b-a12b")
ARGS = {"speed_pct": {"type": "integer", "minimum": 5, "maximum": 100, "description": "arm speed, percent of max"},
        "part_number": {"type": "string", "description": "part number on the item, if the order gives one"}}
SYSTEM = ("You dispatch robot skills for one warehouse cell. Call the skill tools that fulfil the order, once each, "
          "in order. Use only the tools given; if none fits, call none. Pass a part number only if the order has one, "
          "and a speed only if the order states one.")


def tools(skills):
    return [{"type": "function", "function": {"name": name, "description": s["instruction"],
             "parameters": {"type": "object", "properties": ARGS}}} for name, s in skills.items()]


def plan(order, skills, client=None):
    if client is None:
        from openai import OpenAI
        client = OpenAI(base_url=BASE_URL, api_key=os.environ["NEBIUS_API_KEY"])
    r = client.chat.completions.create(model=MODEL, tools=tools(skills), messages=[
        {"role": "system", "content": SYSTEM}, {"role": "user", "content": order}])
    calls = r.choices[0].message.tool_calls or []
    return [{"skill": c.function.name,
             "args": {k: v for k, v in json.loads(c.function.arguments or "{}").items() if k in ARGS}}
            for c in calls if c.function.name in skills]


def offline_plan(order, skills):
    """Stand-in when there's no Token Factory key: the skill whose instruction the order contains."""
    part = re.search(r"\b[A-Z]{2,}-\d{3,}\b", order)
    args = {"part_number": part.group(0)} if part else {}
    return [{"skill": n, "args": dict(args)} for n, s in skills.items() if s["instruction"] in order.lower()]
