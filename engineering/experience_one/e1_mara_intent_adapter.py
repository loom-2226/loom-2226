from __future__ import annotations

"""Audited Mara/OpenAI adapter for Experience One flight intent only.

Mara may translate natural language into destination + priority. It has zero
calculation, planning, state, authorization, or execution authority. Any provider
output that attempts to carry additional authority fails closed before it reaches
Navigator.
"""

import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable, Mapping

from engineering.experience_one.e1_flight_interaction_contract import FlightIntent, IntentOrigin
from engineering.experience_one.spikes.openai_dev_audit import OpenAIDevAudit

API_URL = "https://api.openai.com/v1/responses"
ALLOWED_KEYS = {"destination", "priority"}
SYSTEM_INSTRUCTIONS = """You are Mara at the bounded Experience One intent boundary.
Translate the user's travel intent into exactly one JSON object with exactly two keys:
destination and priority.

Hard authority rules:
- You have ZERO calculation authority.
- You have ZERO campaign/state authority.
- You have ZERO planning authority.
- You have ZERO authorization or execution authority.
- Do not choose a plan, route geometry, metric mode, torch mode, timing, coordinates,
  state id, flight id, or any quantitative flight value.
- Do not claim that an action occurred.
- If destination or priority cannot be determined from the user's words, return an
  empty string for that field. Do not infer hidden state.
- Output JSON only. No markdown and no extra keys.
"""


def parse_mara_intent_json(text: str, *, requested_by: str = "MARA") -> FlightIntent:
    try:
        raw = json.loads(text.strip())
    except Exception as exc:
        raise ValueError("Mara intent response must be valid JSON") from exc
    if not isinstance(raw, dict):
        raise ValueError("Mara intent response must be a JSON object")
    keys = set(raw)
    if keys != ALLOWED_KEYS:
        extras = sorted(keys - ALLOWED_KEYS)
        missing = sorted(ALLOWED_KEYS - keys)
        raise ValueError(f"Mara intent schema mismatch; extras={extras} missing={missing}")
    destination = str(raw.get("destination") or "").strip()
    priority = str(raw.get("priority") or "").strip()
    if not destination or not priority:
        raise ValueError("Mara did not resolve both destination and priority")
    return FlightIntent(
        destination=destination,
        priority=priority,
        origin=IntentOrigin.MARA,
        requested_by=requested_by,
    )


def _response_output_text(response: Mapping[str, Any]) -> str:
    direct = response.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()
    chunks: list[str] = []
    for item in response.get("output", []) or []:
        if not isinstance(item, Mapping) or item.get("type") != "message":
            continue
        for content in item.get("content", []) or []:
            if isinstance(content, Mapping) and content.get("type") == "output_text":
                chunks.append(str(content.get("text") or ""))
    return "".join(chunks).strip()


def _http_provider_call(api_key: str, payload: dict[str, Any], timeout_s: float) -> dict[str, Any]:
    data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    request = urllib.request.Request(
        API_URL,
        data=data,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout_s) as response:
            body = json.loads(response.read())
            return {
                "response": body,
                "http_status": getattr(response, "status", 200),
                "latency_s": time.perf_counter() - start,
            }
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise RuntimeError(f"OpenAI HTTP {exc.code}: {detail[:1200]}") from exc


class OpenAIMaraIntentAdapter:
    def __init__(
        self,
        *,
        api_key: str,
        audit_path: Path,
        model: str = "gpt-5.6-luna",
        timeout_s: float = 90.0,
        provider_call: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
    ) -> None:
        key = api_key.strip()
        if not key:
            raise ValueError("OpenAI API key is required")
        self.api_key = key
        self.model = model
        self.timeout_s = timeout_s
        self.audit = OpenAIDevAudit(audit_path, key, endpoint=API_URL)
        self.provider_call = provider_call

    def _call(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self.provider_call is not None:
            return self.provider_call(payload)
        return _http_provider_call(self.api_key, payload, self.timeout_s)

    def interpret(self, user_text: str) -> FlightIntent:
        text = user_text.strip()
        if not text:
            raise ValueError("user flight intent is required")
        payload = {
            "model": self.model,
            "instructions": SYSTEM_INSTRUCTIONS,
            "input": text,
            "store": False,
        }
        start = time.perf_counter()
        try:
            result = self._call(payload)
            response = result.get("response")
            if not isinstance(response, Mapping):
                raise ValueError("provider response payload missing")
            latency = float(result.get("latency_s", time.perf_counter() - start))
            status = int(result.get("http_status", 200))
            self.audit.append(
                stage="e1.mara.intent",
                request_payload=payload,
                response_payload=dict(response),
                http_status=status,
                latency_s=latency,
                metadata={"authority": "INTENT_TRANSLATION_ONLY"},
            )
            output = _response_output_text(response)
            return parse_mara_intent_json(output)
        except Exception as exc:
            # If the provider call itself failed before a response could be audited,
            # record the failure. Do not duplicate an already-audited response parse
            # failure: the successful provider response above remains the evidence.
            if self.audit.sequence == 0:
                self.audit.append(
                    stage="e1.mara.intent",
                    request_payload=payload,
                    error={"type": type(exc).__name__, "message": str(exc)},
                    latency_s=time.perf_counter() - start,
                    metadata={"authority": "INTENT_TRANSLATION_ONLY"},
                )
            raise
