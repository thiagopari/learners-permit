"""Cosmos Reason 2 scene check: is the cell still the scene a skill's licence was earned in?

A licence is evidence about one scene. When a skill is licensed, a frame of the commissioning scene is kept as its
reference; after each live run, Cosmos Reason 2 compares a frame of that run with it. If the background, lighting or
the objects present have changed, the licence no longer describes the cell, so it's suspended at once: the drift
statistics would take ~8 failed runs to notice the same thing.

Like the Tavily check, it can only narrow. "changed" suspends the licence; "same" changes nothing, and so does an
answer we can't parse, or no answer at all. The model is reached through an OpenAI-compatible chat endpoint:
cloud/cosmos_server.py serves Cosmos-Reason2-2B on the GPU VM (it isn't on Token Factory); COSMOS_BASE_URL and
COSMOS_MODEL can point it at another vision model, e.g. nvidia/Nemotron-3.5-Super-VL on Token Factory.
"""
import base64
import json
import os
import re
import subprocess

BASE_URL = os.environ.get("COSMOS_BASE_URL", "http://127.0.0.1:8001/v1")
MODEL = os.environ.get("COSMOS_MODEL", "nvidia/Cosmos-Reason2-2B")
QUESTION = (
    "Image 1 is the scene a robot skill was tested in. Image 2 is the same robot cell now. Ignore the robot arm's "
    "pose and where the movable objects sit: those change in every run. Has anything changed that the test did not "
    "cover: the background, the lighting, the table, or which objects are present and their colours? "
    "Reason in <think></think>, then give only JSON in <answer></answer>: "
    '{"same_conditions": true or false, "changes": ["short description of each change"]}')
ANSWER = re.compile(r"<answer>(.*?)</answer>", re.S)
JSON = re.compile(r"\{.*\}", re.S)


def frame(video, out, at_s=0.5):
    """One JPEG from a video, via ffmpeg (on the VM; setup_vm.sh installs it). Returns the JPEG's path."""
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(at_s), "-i", str(video), "-frames:v", "1",
                    "-q:v", "3", str(out)], check=True, timeout=60)
    return str(out)


def image_part(path):
    with open(path, "rb") as f:
        return {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()}}


def cosmos(reference, current, client=None):
    """Ask the vision model; returns its raw text."""
    if client is None:
        from openai import OpenAI
        key = os.environ.get("COSMOS_API_KEY") or (os.environ.get("NEBIUS_API_KEY") if "nebius" in BASE_URL else "local")
        client = OpenAI(base_url=BASE_URL, api_key=key, timeout=120, max_retries=1)
    r = client.chat.completions.create(model=MODEL, temperature=0.2, max_tokens=1024, messages=[
        {"role": "system", "content": "You are a careful visual inspector for a robot work cell."},
        {"role": "user", "content": [image_part(reference), image_part(current), {"type": "text", "text": QUESTION}]}])
    return r.choices[0].message.content or ""


def verdict(text):
    """{"verdict": "same" | "changed" | "unknown", "changes": [...]}. Anything unclear is "unknown", which never acts."""
    m = ANSWER.search(text or "")
    body = m.group(1) if m else (JSON.findall(text or "") or [""])[-1]
    try:
        data = json.loads(JSON.search(body).group(0))
    except (AttributeError, ValueError):
        return {"verdict": "unknown", "changes": [], "reason": "no JSON answer"}
    same = data.get("same_conditions")
    if not isinstance(same, bool):
        return {"verdict": "unknown", "changes": [], "reason": "same_conditions isn't true or false"}
    changes = [str(c)[:120] for c in data.get("changes") or [] if str(c).strip()][:5]
    if not same and not changes:  # "changed" with nothing named isn't evidence enough to suspend a licence
        return {"verdict": "unknown", "changes": [], "reason": "said changed but named no change"}
    return {"verdict": "same" if same else "changed", "changes": [] if same else changes}


def check(reference, current, ask=cosmos):
    """Compare two frames. Errors become "unknown": a scene check that can't run must never block or allow."""
    try:
        v = verdict(ask(reference, current))
    except Exception as e:  # server down, timeout, bad image
        v = {"verdict": "unknown", "changes": [], "reason": f"{type(e).__name__}: {str(e)[:120]}"}
    return {**v, "model": MODEL}
