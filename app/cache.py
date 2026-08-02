"""Simple disk-based cache for LLM responses, keyed by prompt content.

Avoids re-paying for identical review requests -- e.g. running
`codechk review` twice with no changes in between, or re-running the
same file review after an unrelated edit elsewhere.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

CACHE_DIR = Path.home() / ".codechk" / "cache"


def _cache_key(model: str, system: str, user: str) -> str:
    raw = f"{model}::{system}::{user}"
    return hashlib.sha256(raw.encode()).hexdigest()


def get(model: str, system: str, user: str) -> list[dict] | None:
    path = CACHE_DIR / f"{_cache_key(model, system, user)}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def set(model: str, system: str, user: str, findings: list[dict]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"{_cache_key(model, system, user)}.json"
    path.write_text(json.dumps(findings))