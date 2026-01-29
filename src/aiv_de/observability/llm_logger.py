import hashlib
import json
import os
import re
from datetime import datetime
from typing import Any, Dict, Optional

REDACTION_PATTERNS = [
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "[REDACTED_API_KEY]"),
    (re.compile(r"(?i)openai[_-]?api[_-]?key\s*[:=]\s*\S+"), "OPENAI_API_KEY=[REDACTED]"),
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "[REDACTED_EMAIL]"),
    (re.compile(r"\+?\d[\d\s().-]{8,}\d"), "[REDACTED_PHONE]"),
    (re.compile(r"[A-Za-z]:\\(?:[^\\\r\n]+\\)*[^\\\r\n]*"), "[REDACTED_PATH]"),
]


def _redact(text: str) -> str:
    out = text
    for pat, repl in REDACTION_PATTERNS:
        out = pat.sub(repl, out)
    return out


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


class SafeLLMLogger:
    """Opt-in JSONL logger for LLM prompts/responses.
    Stores redacted previews + hashes, not full secrets."""

    def __init__(self, base_dir: str, enabled: bool = False, max_chars: int = 2000) -> None:
        self.enabled = enabled
        self.base_dir = base_dir
        self.max_chars = max_chars
        os.makedirs(self.base_dir, exist_ok=True)

    def log(
        self,
        *,
        run_id: str,
        agent: str,
        phase: str,
        prompt: str,
        response: str,
        meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        if not self.enabled:
            return

        prompt_red = _redact(prompt)
        resp_red = _redact(response)

        event = {
            "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "run_id": run_id,
            "agent": agent,
            "phase": phase,
            "prompt_sha256": _sha256(prompt),
            "response_sha256": _sha256(response),
            "prompt_preview": prompt_red[: self.max_chars],
            "response_preview": resp_red[: self.max_chars],
            "meta": meta or {},
        }

        path = os.path.join(self.base_dir, f"{run_id}.llm.jsonl")
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
