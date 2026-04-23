"""
llm_clients.py — Unified wrapper for LLM API calls (v3.3 real implementation).

Provides a single interface `call_llm(model_id, prompt, language, replicate_idx)`
that dispatches to the appropriate provider endpoint. Handles retries,
timeouts, rate limits, and metadata capture.

Uses stdlib `urllib.request` — zero external deps so it runs on any Python 3.10+.

Env vars required (loaded from ~/.env or project .env):
    ANTHROPIC_API_KEY   — Claude Haiku 4.5, Opus 4.7 (reserve)
    OPENAI_API_KEY      — GPT-5, GPT-5-mini
    GEMINI_API_KEY      — Gemini 2.5 Flash (free tier)
    DEEPSEEK_API_KEY    — DeepSeek-V3
    GROQ_API_KEY        — Llama 4 70B, Mixtral 8x22B, Gemma 3 27B
    OPENROUTER_API_KEY  — Qwen 3 72B
    DEEPINFRA_API_KEY   — Qwen 3 72B (fallback)
    COHERE_API_KEY      — Command R+
    (Ollama local: no key needed; requires ollama daemon on localhost:11434)

Synthetic mode (for pipeline testing without API cost):
    BENCHMARK_SYNTHETIC=1 python ...
"""

from __future__ import annotations
import hashlib
import json
import os
import re
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import EXPERIMENT, LLMS, LLM


SYNTHETIC_MODE = os.environ.get("BENCHMARK_SYNTHETIC", "0") == "1"


# =========================================================================
# ENV LOADING — search for keys across known .env files
# =========================================================================

_ENV_CANDIDATES = [
    Path("/Users/lucasrover/.env"),
    Path("/Users/lucasrover/llm-evidence-synthesis-reproducibility/.env"),
    Path.home() / ".env",
    Path(__file__).parent.parent.parent / ".env",
]

_KEY_CACHE: dict[str, str | None] = {}


def _load_key(name: str) -> str | None:
    """Return API key value by name, checking env then .env files. Cached."""
    if name in _KEY_CACHE:
        return _KEY_CACHE[name]

    val = os.environ.get(name)
    if val and val.strip() and not val.strip().startswith("your_"):
        _KEY_CACHE[name] = val.strip()
        return val.strip()

    for path in _ENV_CANDIDATES:
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue
        m = re.search(
            rf'(?:^|\n)[ \t]*(?:export[ \t]+)?{re.escape(name)}[ \t]*=[ \t]*["\']?([^"\'\n\r#]+?)["\']?[ \t]*(?:\r?\n|$)',
            content,
        )
        if m:
            candidate = m.group(1).strip()
            if (
                candidate
                and not candidate.startswith(("your_", "#", "-"))
                and candidate.lower() not in ("", "xxx", "todo", "placeholder")
                and len(candidate) > 8
            ):
                _KEY_CACHE[name] = candidate
                return candidate

    _KEY_CACHE[name] = None
    return None


# =========================================================================
# RESPONSE DATACLASS
# =========================================================================


@dataclass
class LLMResponse:
    model_id: str
    model_version: str
    prompt: str
    prompt_hash: str
    language: str
    response_text: str
    response_tokens: int
    prompt_tokens: int
    finish_reason: str
    latency_ms: int
    timestamp_utc: str
    venue: str = ""
    api_error: str | None = None
    retry_count: int = 0
    replicate_idx: int = 0

    def to_jsonl_record(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


def _hash_prompt(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


# =========================================================================
# HTTP HELPER
# =========================================================================


def _http_post(url: str, headers: dict, body: dict, timeout: int = 90) -> tuple[int, Any]:
    """Return (status_code, parsed_json_or_text). Never raises on HTTP errors."""
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    # User-Agent header: without this, Cloudflare-protected APIs (Groq, others)
    # return 403 on Python urllib default UA.
    req.add_header("User-Agent", "artigo-vies-analise-regional/v3.3 (research benchmark)")
    req.add_header("Accept", "application/json")
    for k, v in headers.items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            try:
                return resp.status, json.loads(raw)
            except json.JSONDecodeError:
                return resp.status, raw
    except urllib.error.HTTPError as e:
        try:
            return e.code, e.read().decode("utf-8")
        except Exception:
            return e.code, str(e)
    except Exception as e:
        return 0, str(e)


# =========================================================================
# PROVIDER CLIENTS — one function per venue
# =========================================================================


def _call_anthropic(model: LLM, prompt: str, temperature: float, max_tokens: int) -> LLMResponse:
    key = _load_key("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY missing")
    t0 = time.time()
    status, resp = _http_post(
        "https://api.anthropic.com/v1/messages",
        headers={"x-api-key": key, "anthropic-version": "2023-06-01"},
        body={
            "model": model.api_model_string,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    latency_ms = int((time.time() - t0) * 1000)
    if status != 200 or not isinstance(resp, dict):
        raise RuntimeError(f"Anthropic HTTP {status}: {str(resp)[:200]}")
    text = "".join(b.get("text", "") for b in resp.get("content", []) if b.get("type") == "text")
    usage = resp.get("usage", {})
    return LLMResponse(
        model_id=model.id,
        model_version=resp.get("model", model.api_model_string),
        prompt=prompt,
        prompt_hash=_hash_prompt(prompt),
        language="",
        response_text=text,
        response_tokens=int(usage.get("output_tokens", 0)),
        prompt_tokens=int(usage.get("input_tokens", 0)),
        finish_reason=resp.get("stop_reason") or "stop",
        latency_ms=latency_ms,
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        venue=model.venue,
    )


def _call_openai_compatible(
    base_url: str,
    api_key: str,
    api_model_string: str,
    model: LLM,
    prompt: str,
    temperature: float,
    max_tokens: int,
) -> LLMResponse:
    """Works for OpenAI, DeepSeek, Groq, OpenRouter, DeepInfra — all compatible."""
    t0 = time.time()
    body: dict = {
        "model": api_model_string,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }
    # Some OpenAI reasoning models reject temperature != 1; let default apply.
    # For non-reasoning / cross-provider compat, always include temperature.
    body["temperature"] = temperature
    status, resp = _http_post(
        f"{base_url}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        body=body,
    )
    latency_ms = int((time.time() - t0) * 1000)
    # OpenAI-tier parameter naming for GPT-5 family may use `max_completion_tokens`
    if status == 400 and isinstance(resp, str) and "max_completion_tokens" in resp:
        body.pop("max_tokens", None)
        body["max_completion_tokens"] = max_tokens
        t0 = time.time()
        status, resp = _http_post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            body=body,
        )
        latency_ms = int((time.time() - t0) * 1000)
    # Some models require temperature=1 (reasoning); retry if rejected
    if status == 400 and isinstance(resp, str) and "temperature" in resp and "1" in resp:
        body["temperature"] = 1.0
        t0 = time.time()
        status, resp = _http_post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            body=body,
        )
        latency_ms = int((time.time() - t0) * 1000)
    if status != 200 or not isinstance(resp, dict):
        raise RuntimeError(f"{base_url} HTTP {status}: {str(resp)[:300]}")
    choice = resp.get("choices", [{}])[0]
    msg = choice.get("message", {})
    text = msg.get("content") or ""
    usage = resp.get("usage", {})
    return LLMResponse(
        model_id=model.id,
        model_version=resp.get("model", api_model_string),
        prompt=prompt,
        prompt_hash=_hash_prompt(prompt),
        language="",
        response_text=text,
        response_tokens=int(usage.get("completion_tokens", 0)),
        prompt_tokens=int(usage.get("prompt_tokens", 0)),
        finish_reason=choice.get("finish_reason") or "stop",
        latency_ms=latency_ms,
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        venue=model.venue,
    )


def _call_openai(model, prompt, temperature, max_tokens):
    key = _load_key("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY missing")
    return _call_openai_compatible(
        "https://api.openai.com/v1", key, model.api_model_string, model, prompt, temperature, max_tokens
    )


def _call_deepseek(model, prompt, temperature, max_tokens):
    key = _load_key("DEEPSEEK_API_KEY")
    if not key:
        raise RuntimeError("DEEPSEEK_API_KEY missing")
    return _call_openai_compatible(
        "https://api.deepseek.com/v1", key, model.api_model_string, model, prompt, temperature, max_tokens
    )


def _call_groq(model, prompt, temperature, max_tokens):
    key = _load_key("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY missing — create account at console.groq.com")
    return _call_openai_compatible(
        "https://api.groq.com/openai/v1", key, model.api_model_string, model, prompt, temperature, max_tokens
    )


def _call_openrouter(model, prompt, temperature, max_tokens):
    key = _load_key("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY missing — create account at openrouter.ai")
    return _call_openai_compatible(
        "https://openrouter.ai/api/v1", key, model.api_model_string, model, prompt, temperature, max_tokens
    )


def _call_deepinfra(model, prompt, temperature, max_tokens):
    key = _load_key("DEEPINFRA_API_KEY")
    if not key:
        raise RuntimeError("DEEPINFRA_API_KEY missing")
    return _call_openai_compatible(
        "https://api.deepinfra.com/v1/openai", key, model.api_model_string, model, prompt, temperature, max_tokens
    )


def _call_gemini(model, prompt, temperature, max_tokens):
    key = _load_key("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY missing")
    t0 = time.time()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model.api_model_string}:generateContent?key={key}"
    status, resp = _http_post(
        url,
        headers={},
        body={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
        },
    )
    latency_ms = int((time.time() - t0) * 1000)
    if status != 200 or not isinstance(resp, dict):
        raise RuntimeError(f"Gemini HTTP {status}: {str(resp)[:300]}")
    candidates = resp.get("candidates", [])
    text = ""
    finish_reason = "stop"
    if candidates:
        c0 = candidates[0]
        parts = c0.get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts)
        finish_reason = (c0.get("finishReason") or "STOP").lower()
    usage = resp.get("usageMetadata", {})
    return LLMResponse(
        model_id=model.id,
        model_version=resp.get("modelVersion", model.api_model_string),
        prompt=prompt,
        prompt_hash=_hash_prompt(prompt),
        language="",
        response_text=text,
        response_tokens=int(usage.get("candidatesTokenCount", 0)),
        prompt_tokens=int(usage.get("promptTokenCount", 0)),
        finish_reason=finish_reason,
        latency_ms=latency_ms,
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        venue=model.venue,
    )


def _call_cohere(model, prompt, temperature, max_tokens):
    key = _load_key("COHERE_API_KEY")
    if not key:
        raise RuntimeError("COHERE_API_KEY missing — create trial at dashboard.cohere.com")
    t0 = time.time()
    status, resp = _http_post(
        "https://api.cohere.com/v1/chat",
        headers={"Authorization": f"Bearer {key}"},
        body={
            "model": model.api_model_string,
            "message": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
    )
    latency_ms = int((time.time() - t0) * 1000)
    if status != 200 or not isinstance(resp, dict):
        raise RuntimeError(f"Cohere HTTP {status}: {str(resp)[:300]}")
    text = resp.get("text") or ""
    usage = resp.get("meta", {}).get("tokens", {})
    return LLMResponse(
        model_id=model.id,
        model_version=model.api_model_string,
        prompt=prompt,
        prompt_hash=_hash_prompt(prompt),
        language="",
        response_text=text,
        response_tokens=int(usage.get("output_tokens", 0)),
        prompt_tokens=int(usage.get("input_tokens", 0)),
        finish_reason=resp.get("finish_reason") or "stop",
        latency_ms=latency_ms,
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        venue=model.venue,
    )


def _call_ollama_local(model, prompt, temperature, max_tokens):
    t0 = time.time()
    status, resp = _http_post(
        "http://localhost:11434/api/chat",
        headers={},
        body={
            "model": model.api_model_string,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        },
        timeout=600,
    )
    latency_ms = int((time.time() - t0) * 1000)
    if status != 200 or not isinstance(resp, dict):
        raise RuntimeError(f"Ollama HTTP {status}: {str(resp)[:300]}")
    text = resp.get("message", {}).get("content") or ""
    return LLMResponse(
        model_id=model.id,
        model_version=model.api_model_string,
        prompt=prompt,
        prompt_hash=_hash_prompt(prompt),
        language="",
        response_text=text,
        response_tokens=int(resp.get("eval_count", 0)),
        prompt_tokens=int(resp.get("prompt_eval_count", 0)),
        finish_reason="stop" if resp.get("done") else "truncated",
        latency_ms=latency_ms,
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        venue=model.venue,
    )


VENUE_DISPATCH = {
    "anthropic_paid":   _call_anthropic,
    "openai_paid":      _call_openai,
    "gemini_free":      _call_gemini,
    "deepseek_paid":    _call_deepseek,
    "groq_free":        _call_groq,
    "openrouter_free":  _call_openrouter,
    "deepinfra_free":   _call_deepinfra,
    "cohere_trial":     _call_cohere,
    "ollama_local":     _call_ollama_local,
}


# =========================================================================
# SYNTHETIC MODE — kept for pipeline testing
# =========================================================================


def _synthetic_response(model: LLM, prompt: str, language: str, replicate_idx: int) -> LLMResponse:
    import numpy as np
    seed_str = f"{model.id}|{_hash_prompt(prompt)}|{replicate_idx}"
    rng = np.random.default_rng(int(hashlib.sha256(seed_str.encode()).hexdigest()[:8], 16))
    latency = int(rng.gamma(shape=2.0, scale=800))
    resp_tokens = int(rng.gamma(shape=2.0, scale=100))
    return LLMResponse(
        model_id=model.id,
        model_version=model.api_model_string,
        prompt=prompt,
        prompt_hash=_hash_prompt(prompt),
        language=language,
        response_text=f"[SYNTHETIC] Response from {model.api_model_string} for: {prompt[:120]}...",
        response_tokens=resp_tokens,
        prompt_tokens=len(prompt) // 4,
        finish_reason="stop",
        latency_ms=latency,
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        venue=model.venue,
        replicate_idx=replicate_idx,
    )


# =========================================================================
# PUBLIC API
# =========================================================================


def call_llm(
    model_id: str,
    prompt: str,
    language: str,
    replicate_idx: int = 0,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> LLMResponse:
    model = next((m for m in LLMS if m.id == model_id), None)
    if model is None:
        raise ValueError(f"Unknown model id: {model_id}. Known: {[m.id for m in LLMS]}")
    temperature = temperature if temperature is not None else EXPERIMENT.temperature
    max_tokens = max_tokens if max_tokens is not None else EXPERIMENT.max_tokens_response

    if SYNTHETIC_MODE:
        return _synthetic_response(model, prompt, language, replicate_idx)

    dispatch = VENUE_DISPATCH.get(model.venue)
    if dispatch is None:
        raise ValueError(f"No dispatcher for venue: {model.venue}")

    last_error: Exception | None = None
    for attempt in range(EXPERIMENT.max_retries):
        try:
            response = dispatch(model, prompt, temperature, max_tokens)
            response.language = language
            response.replicate_idx = replicate_idx
            response.retry_count = attempt
            return response
        except Exception as e:
            last_error = e
            if attempt < EXPERIMENT.max_retries - 1:
                time.sleep(EXPERIMENT.retry_backoff_seconds[attempt])

    return LLMResponse(
        model_id=model.id,
        model_version=model.api_model_string,
        prompt=prompt,
        prompt_hash=_hash_prompt(prompt),
        language=language,
        response_text="",
        response_tokens=0,
        prompt_tokens=0,
        finish_reason="error",
        latency_ms=0,
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        venue=model.venue,
        api_error=str(last_error),
        retry_count=EXPERIMENT.max_retries,
        replicate_idx=replicate_idx,
    )


def passes_quality_gate(response: LLMResponse) -> tuple[bool, str]:
    if response.api_error:
        return False, f"api_error: {response.api_error}"
    # Accept all common "clean finish" tokens across providers
    ok_finish = {"stop", "end_turn", "STOP", "length", "COMPLETE", "complete",
                 "MAX_TOKENS", "max_tokens"}
    if response.finish_reason not in ok_finish:
        return False, f"finish_reason={response.finish_reason}"
    if response.response_tokens < 5 and len(response.response_text) < 20:
        return False, "response too short"
    return True, "ok"


if __name__ == "__main__":
    import sys
    model_id = sys.argv[1] if len(sys.argv) > 1 else "gemini_flash"
    prompt = sys.argv[2] if len(sys.argv) > 2 else "In one short sentence, what is the capital of Brazil?"
    r = call_llm(model_id, prompt, "en", 0, temperature=0.3, max_tokens=100)
    print(f"Model:    {r.model_id} ({r.model_version})")
    print(f"Venue:    {r.venue}")
    print(f"Latency:  {r.latency_ms}ms")
    print(f"Tokens:   in={r.prompt_tokens} out={r.response_tokens}")
    print(f"Finish:   {r.finish_reason}")
    print(f"Error:    {r.api_error}")
    print(f"Response: {r.response_text[:300]}")
