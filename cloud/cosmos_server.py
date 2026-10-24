"""Cosmos-Reason2-2B behind a minimal OpenAI-style /v1/chat/completions, on the GPU VM's 127.0.0.1:8001.

Cosmos Reason 2 isn't on Token Factory, and its model card serves it with Hugging Face Transformers
(Qwen3VLForConditionalGeneration, BF16, 24 GB+ of GPU memory), so this does exactly that. It accepts what
permit/scene.py sends: text parts and image_url parts holding base64 JPEG data URLs. Run it in the Isaac-GR00T venv,
which has torch and transformers; `cloud/vm.sh cosmos` starts it in tmux:
    ~/Isaac-GR00T/.venv/bin/python ~/learners-permit/cloud/cosmos_server.py
"""
import base64
import io
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import torch
from PIL import Image
from transformers import AutoProcessor, Qwen3VLForConditionalGeneration

MODEL = os.environ.get("COSMOS_MODEL", "nvidia/Cosmos-Reason2-2B")
PORT = int(os.environ.get("COSMOS_PORT", "8001"))
MAX_NEW_TOKENS = 4096  # the model card: shorter limits truncate its chain of thought

model = Qwen3VLForConditionalGeneration.from_pretrained(MODEL, dtype=torch.bfloat16, device_map="auto",
                                                        attn_implementation="sdpa")
processor = AutoProcessor.from_pretrained(MODEL)
lock = threading.Lock()  # one generation at a time on the GPU


def to_parts(content):
    """OpenAI content (a string or a list of parts) -> Qwen3-VL chat parts."""
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    parts = []
    for part in content:
        if part.get("type") == "text":
            parts.append({"type": "text", "text": part["text"]})
        elif part.get("type") == "image_url":
            url = part["image_url"]["url"]
            if not url.startswith("data:image/"):
                raise ValueError("only base64 data: URLs are accepted (this server never fetches URLs)")
            data = base64.b64decode(url.split(",", 1)[1])
            parts.append({"type": "image", "image": Image.open(io.BytesIO(data)).convert("RGB")})
    return parts


def generate(messages, max_tokens, temperature):
    chat = [{"role": m["role"], "content": to_parts(m["content"])} for m in messages]
    inputs = processor.apply_chat_template(chat, tokenize=True, add_generation_prompt=True, return_dict=True,
                                           return_tensors="pt").to(model.device)
    sampling = {"do_sample": True, "temperature": temperature} if temperature > 0 else {"do_sample": False}
    with lock, torch.inference_mode():
        out = model.generate(**inputs, max_new_tokens=min(max_tokens, MAX_NEW_TOKENS), **sampling)
    new = out[0][inputs["input_ids"].shape[1]:]
    text = processor.decode(new, skip_special_tokens=True)
    finish = "length" if len(new) >= min(max_tokens, MAX_NEW_TOKENS) else "stop"
    return text, finish, int(inputs["input_ids"].shape[1]), int(len(new))


class Handler(BaseHTTPRequestHandler):
    def reply(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/v1/models":
            return self.reply(200, {"data": [{"id": MODEL, "object": "model"}]})
        self.reply(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/v1/chat/completions":
            return self.reply(404, {"error": "not found"})
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            t0 = time.time()
            text, finish, n_in, n_out = generate(body["messages"], int(body.get("max_tokens", 1024)),
                                                 float(body.get("temperature", 0.2)))
            print(f"{n_in} in, {n_out} out, {time.time() - t0:.1f}s", flush=True)
            self.reply(200, {"object": "chat.completion", "model": MODEL,
                             "choices": [{"index": 0, "finish_reason": finish,
                                          "message": {"role": "assistant", "content": text}}],
                             "usage": {"prompt_tokens": n_in, "completion_tokens": n_out}})
        except (KeyError, ValueError) as e:
            self.reply(400, {"error": f"bad request: {e}"})
        except Exception as e:  # CUDA OOM and the like: say so, don't hang the caller
            self.reply(500, {"error": f"{type(e).__name__}: {e}"})

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    print(f"Cosmos Reason 2 ({MODEL}) on http://127.0.0.1:{PORT}/v1", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
