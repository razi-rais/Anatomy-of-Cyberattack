"""Shared Ollama client for the lab kit.

Unlike a bare client this one also returns token usage for each call (how many
input tokens went in and how many output tokens came back) and can look up
static facts about the model (parameter size, quantization, size on disk). The
web UI uses both to show a small, expandable "model info" panel.

Standard library only, so it runs anywhere Python 3 and Ollama are available.
"""

from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass

DEFAULT_MODEL = "qwen2.5:1.5b"
OLLAMA_BASE = "http://localhost:11434"
OLLAMA_CHAT_URL = f"{OLLAMA_BASE}/api/chat"
OLLAMA_TAGS_URL = f"{OLLAMA_BASE}/api/tags"


@dataclass
class ChatResult:
    content: str
    input_tokens: int | None
    output_tokens: int | None
    model: str


class OllamaClient:
    """A small client for the Ollama /api/chat endpoint."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        url: str = OLLAMA_CHAT_URL,
        temperature: float = 0.0,
        timeout: int = 120,
    ) -> None:
        self.model = model
        self.url = url
        self.temperature = temperature
        self.timeout = timeout

    def chat(self, system: str, user: str) -> ChatResult:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
            "options": {"temperature": self.temperature},
        }
        request = urllib.request.Request(
            self.url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            body = json.loads(response.read())
        return ChatResult(
            content=body["message"]["content"],
            input_tokens=body.get("prompt_eval_count"),
            output_tokens=body.get("eval_count"),
            model=self.model,
        )


def get_model_info(model: str = DEFAULT_MODEL, url: str = OLLAMA_TAGS_URL) -> dict:
    """Return static facts about the model from the Ollama tags endpoint.

    Falls back to a minimal record if the lookup fails so the UI never breaks.
    """
    info = {
        "name": model,
        "parameter_size": "unknown",
        "quantization": "unknown",
        "family": "unknown",
        "size_mb": None,
    }
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            tags = json.loads(response.read())
        for entry in tags.get("models", []):
            if entry.get("name") == model or entry.get("model") == model:
                details = entry.get("details", {})
                info["parameter_size"] = details.get("parameter_size", "unknown")
                info["quantization"] = details.get("quantization_level", "unknown")
                info["family"] = details.get("family", "unknown")
                size = entry.get("size")
                if size:
                    info["size_mb"] = round(size / (1024 * 1024))
                break
    except Exception:
        pass
    return info
