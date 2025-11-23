import requests
from typing import Optional, List, Dict

import config


def ask_brain(prompt: str, history: Optional[List[Dict]] = None) -> str:
    """
    Send a prompt to Ollama chat API and return the reply text.

    history: optional list of {"role": "...", "content": "..."} dicts
             if you want to keep conversation context later.
    """
    if history is None:
        history = []

    # Ollama chat format
    messages = history + [{"role": "user", "content": prompt}]

    url = f"http://{config.LLM_HOST}:{config.LLM_PORT}/api/chat"
    payload = {
        "model": config.LLM_MODEL,
        "messages": messages,
        "stream": False,
    }

    resp = requests.post(url, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    # Typical Ollama response shape:
    # {"model": "...", "message": {"role": "assistant", "content": "..."}, ...}
    msg = data.get("message") or data.get("choices", [{}])[0].get("message")
    if msg and isinstance(msg, dict):
        return (msg.get("content") or "").strip()

    # Fallback – just stringify whatever came back
    return str(data)
