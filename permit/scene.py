"""Scene check: is the cell still the environment a skill's licence was earned in?

A licence is evidence about one scene. When a skill is licensed, a frame of the commissioning scene is kept as its
reference; after each live run, a vision model compares a frame of that run with it. If the background, floor,
lighting or table changed, the licence no longer describes the cell, so it's suspended at once, without waiting for
the success rate to fall.

Like the Tavily check, it can only narrow. "changed" suspends the licence; "same" changes nothing, and so does an
answer we can't parse, or no answer at all.

Which model, measured on Oct 28 on frames from our own Isaac Sim runs (3 trials each of: two runs of the same scene,
a randomized background, a different scene):
- nvidia/Nemotron-3.5-Super-VL on Token Factory: 8 of 9 right, no false alarm (the miss was unparseable, so it
  never acted), ~4 s per check. The default.
- nvidia/Cosmos-Reason2-2B, served on the GPU VM by cloud/cosmos_server.py (it isn't on Token Factory): 6 of 9, and
  it called two runs of the SAME scene "changed" 3 times in 3 (it treated moved task objects as a change), which would
  suspend licences on every run. Not used to suspend; COSMOS_BASE_URL / COSMOS_MODEL switch to it for comparison.
"""
import base64
import json
import os
import re
import subprocess

BASE_URL = os.environ.get("COSMOS_BASE_URL", "https://api.tokenfactory.nebius.com/v1/")
MODEL = os.environ.get("COSMOS_MODEL", "nvidia/Nemotron-3.5-Super-VL")
# A licence covers the environment it was earned in. The task's objects (how many, where) vary from run to run by
# design: asked about "objects present", Cosmos flagged 3 vs 4 visible bananas in two runs of the SAME scene as a
# change (Oct 28), which would suspend licences wrongly. So it answers per part, and only the environment counts.
ENVIRONMENT = ("background", "floor", "lighting", "table")
QUESTION = (
    "Image 1 is the robot cell a skill was tested in. Image 2 is the robot cell now. The robot arm's pose and the "
    "task objects (how many there are, where they lie) differ from run to run; never count them as a change. "
    "Compare only the environment: the background and walls, the floor, the lighting, and the table surface. "
    "Reason in <think></think>, then give only JSON in <answer></answer>: "
    '{"background": true or false, "floor": true or false, "lighting": true or false, "table": true or false, '
    '"changes": ["short description of each environment change"]} where true means that part changed.')
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
    parts = {k: data.get(k) for k in ENVIRONMENT}
    if not all(isinstance(v, bool) for v in parts.values()):
        return {"verdict": "unknown", "changes": [], "reason": "not a true/false answer for every part"}
    changed = [k for k, v in parts.items() if v]
    changes = [str(c)[:120] for c in data.get("changes") or [] if str(c).strip()][:5]
    if changed and not changes:  # "changed" with nothing described isn't evidence enough to suspend a licence
        return {"verdict": "unknown", "changes": [], "reason": "said changed but described no change"}
    return {"verdict": "changed" if changed else "same", "parts": changed, "changes": changes if changed else []}


def check(reference, current, ask=cosmos):
    """Compare two frames. Errors become "unknown": a scene check that can't run must never block or allow."""
    try:
        v = verdict(ask(reference, current))
    except Exception as e:  # server down, timeout, bad image
        v = {"verdict": "unknown", "changes": [], "reason": f"{type(e).__name__}: {str(e)[:120]}"}
    return {**v, "model": MODEL}
