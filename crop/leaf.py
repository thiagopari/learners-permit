"""A non-robot skill under the same licence: few-shot leaf diagnosis by a vision model, licensed per crop.

The skill is "diagnose a leaf photo": Nemotron-3.5-Super-VL on Token Factory, shown one verified reference leaf per
diagnosis (few-shot, no training) and then the query leaf. Each trial is one labelled photo from the public
PlantVillage dataset: correct or not against its true label. The trust gate (permit/gate.py, through
permit/licences.py) licenses the skill for a crop only when P(accuracy >= 80%) >= 0.95, and the licence's scope is
that crop: a tomato licence says nothing about peppers.

Honesty rules: the model sees only image bytes, never a file name (PlantVillage names hint at the label); an
answer that isn't one of the allowed diagnoses counts as a wrong one; and every prediction is written out, so the
numbers can be checked. Nothing here invents scores.
"""
import base64
import json
import os
import pathlib
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor

from permit import planner

MODEL = os.environ.get("CROP_MODEL", "nvidia/Nemotron-3.5-Super-VL")
BASE_URL = os.environ.get("CROP_BASE_URL", planner.BASE_URL)
DATA = pathlib.Path(__file__).resolve().parents[1] / "data" / "plantvillage"
# crop -> diagnosis -> PlantVillage folder
CROPS = {
    "tomato": {"healthy": "Tomato___healthy", "early_blight": "Tomato___Early_blight",
               "late_blight": "Tomato___Late_blight"},
    "pepper": {"healthy": "Pepper,_bell___healthy", "bacterial_spot": "Pepper,_bell___Bacterial_spot"},
}
JSON = re.compile(r"\{.*?\}", re.S)


class OutOfPhotos(RuntimeError):
    """The gate wanted more trials than there are labelled photos."""


def references(crop, data=DATA):
    """The one verified reference leaf per diagnosis (files named ref_*), never used as a trial."""
    return {label: next((data / folder).glob("ref_*")) for label, folder in CROPS[crop].items()}


def trials(crop, data=DATA, seed=0):
    """(path, true label) for every non-reference photo of this crop, in a fixed shuffled order."""
    items = [(p, label) for label, folder in CROPS[crop].items() for p in sorted((data / folder).iterdir())
             if not p.name.startswith("ref_")]
    random.Random(f"{crop}-{seed}").shuffle(items)
    return items


def image_part(path):
    return {"type": "image_url",
            "image_url": {"url": "data:image/jpeg;base64," + base64.b64encode(pathlib.Path(path).read_bytes()).decode()}}


def ask(refs, query, client=None):
    """The model's raw answer. Only image bytes and the label names are sent; file names never are."""
    if client is None:
        from openai import OpenAI
        client = OpenAI(base_url=BASE_URL, api_key=os.environ["NEBIUS_API_KEY"], timeout=60, max_retries=2)
    labels = list(refs)
    content = [{"type": "text", "text": "Verified reference leaves, one per possible diagnosis:"}]
    for label, path in refs.items():
        content += [{"type": "text", "text": f"REFERENCE: {label}"}, image_part(path)]
    content += [{"type": "text", "text": "Now diagnose this new leaf. It has exactly one of these diagnoses: "
                 + ", ".join(labels) + '. Answer with only JSON: {"diagnosis": "<one of them>"}'}, image_part(query)]
    r = client.chat.completions.create(model=MODEL, temperature=0, max_tokens=50,
                                       extra_body={"chat_template_kwargs": {"enable_thinking": False}},
                                       messages=[{"role": "user", "content": content}])
    return r.choices[0].message.content or ""


def parse(text, labels):
    """The diagnosis if the answer names exactly one allowed label, else None (which counts as wrong)."""
    m = JSON.search(text or "")
    if m:
        try:
            value = str(json.loads(m.group(0)).get("diagnosis", "")).strip().lower().replace(" ", "_")
            return value if value in labels else None
        except ValueError:
            pass
    named = [label for label in labels if re.search(rf"\b{label.replace('_', '[ _]')}\b", text or "", re.I)]
    return named[0] if len(named) == 1 else None


def trained(model_path, device=None):
    """predict(path, crop, labels) -> label from a model crop/train.py trained, choosing among this crop's labels only
    (the few-shot model is offered the same choices)."""
    import torch
    from PIL import Image
    from crop.train import model_for, transform
    ckpt = torch.load(model_path, map_location="cpu")
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    model = model_for(len(ckpt["classes"]))
    model.load_state_dict(ckpt["state_dict"])
    model.to(device).eval()
    t = transform(False)

    def predict(path, crop, labels):
        idx = [ckpt["classes"].index(f"{crop}:{label}") for label in labels]
        with torch.no_grad():
            logits = model(t(Image.open(path).convert("RGB")).unsqueeze(0).to(device))[0]
        return labels[int(logits[idx].argmax())]
    return predict


def runner(crop, record, client=None, workers=8, data=DATA, predict=None):
    """A trust-gate runner (run_batch({arm: n}) -> {arm: [1, 0, ...]}) whose trials are the next n labelled photos.
    record(row) receives every prediction. Each photo is used once; the gate stops before they run out.
    predict(path, crop, labels) -> label replaces the few-shot vision model (e.g. trained(model.pt))."""
    refs, queue = references(crop, data), trials(crop, data)
    labels = list(refs)

    def one(item):
        path, truth = item
        t0 = time.time()
        if predict is not None:
            guess = predict(path, crop, labels)
            raw = guess
        else:
            try:
                raw = ask(refs, path, client)
            except Exception as e:  # an API failure is a failed trial, not a skipped one
                raw = f"error: {type(e).__name__}"
            guess = parse(raw, labels)
        row = {"crop": crop, "image": path.name, "truth": truth, "predicted": guess, "correct": guess == truth,
               "seconds": round(time.time() - t0, 1), "raw": raw[:200]}
        record(row)
        return int(row["correct"])

    def run_batch(alloc):
        if not queue:  # never invent trials: an undecided gate with no photos left is the honest result
            raise OutOfPhotos(f"{crop}: no labelled photos left")
        out = {}
        with ThreadPoolExecutor(workers) as pool:
            for arm, n in alloc.items():
                batch = [queue.pop(0) for _ in range(min(n, len(queue)))]
                out[arm] = list(pool.map(one, batch))
        return out
    run_batch.available = lambda: len(queue)
    return run_batch
