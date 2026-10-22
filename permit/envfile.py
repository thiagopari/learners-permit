"""API keys for local runs: the project's .env (git-ignored), else ~/.config/learners-permit.env.

Lines are KEY=VALUE; blank lines and # comments are skipped, and quotes around a value are dropped. A variable
already set in the environment wins, so `NEBIUS_API_KEY=... python -m permit.server` still overrides the file.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATHS = (os.path.join(ROOT, ".env"), os.path.expanduser("~/.config/learners-permit.env"))


def parse(text):
    out = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip().removeprefix("export ").strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key:
            out[key] = value
    return out


def load(paths=PATHS, environ=os.environ):
    """Load the first file that exists; returns its path (or None). Never prints values."""
    for path in paths:
        if os.path.isfile(path):
            with open(path, encoding="utf-8-sig") as f:  # -sig: Notepad may save a BOM
                for key, value in parse(f.read()).items():
                    environ.setdefault(key, value)
            return path
    return None
