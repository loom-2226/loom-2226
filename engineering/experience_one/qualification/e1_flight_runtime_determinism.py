#!/usr/bin/env python3
from __future__ import annotations

"""Bounded E1 flight-runtime determinism adapter.

Sequence H's normal target_determinism_gate recompiles the complete Sequence B/C/D
Solar presentation payload. That is appropriate for the legacy whole-map browser
qualification, but it is not a dependency of authoritative flight mechanics and it
cannot be satisfied at the 2226 E1 epoch because some unrelated natural-satellite
Horizons queries end before 2226.

This adapter is qualification-only. It does not replace Navigator calculation or
state authority. It runs the existing Sequence A authoritative solver twice against
the exact same normalized mission and acquired route dependencies, requires both
Sequence A validations to PASS, and requires byte-canonical runtime hashes to match.
It returns a deterministic, explicitly non-production HTML marker only because the
existing Navigator campaign wrapper records an HTML hash as ancillary evidence.
"""

from typing import Any


def install_flight_runtime_determinism(core: Any) -> None:
    """Replace only the loaded core's presentation-coupled determinism gate."""
    if getattr(core, "_loom_e1_flight_runtime_determinism_installed", False):
        return

    original = core.target_determinism_gate

    def flight_runtime_determinism_gate(normalized: dict, acquisition: dict, cache_dir, b1_package):
        runtime1, seq_a1 = core.solve_sequence_a(normalized, acquisition, cache_dir)
        runtime2, seq_a2 = core.solve_sequence_a(normalized, acquisition, cache_dir)

        if seq_a1.get("status") != "PASS" or seq_a2.get("status") != "PASS":
            raise core.WorkflowError("E1 flight-runtime determinism requires Sequence A PASS on both solves")

        hash1 = core.sha256_bytes(core.canonical_json_bytes(runtime1))
        hash2 = core.sha256_bytes(core.canonical_json_bytes(runtime2))
        if hash1 != hash2:
            raise core.WorkflowError("E1 flight-runtime determinism gate failed: authoritative runtime hashes differ")

        html = (
            "<!doctype html><meta charset='utf-8'>"
            "<title>LOOM E1 flight qualification</title>"
            "<body><h1>LOOM E1 FLIGHT QUALIFICATION</h1>"
            "<p>Sequence B/C/D whole-map presentation is explicitly out of scope.</p>"
            f"<p>Authoritative runtime SHA-256: {hash1}</p></body>"
        )
        html_sha = core.sha256_bytes(html.encode("utf-8"))
        validation = {
            "schema": "LOOM_E1_FLIGHT_RUNTIME_VALIDATION_V1",
            "status": "PASS",
            "sequence_a_first": seq_a1,
            "sequence_a_second": seq_a2,
            "presentation": "OUT_OF_SCOPE_SEQUENCE_B_C_D",
            "authority": {
                "flight_calculation": "EXISTING_SEQUENCE_A_PYTHON_AUTHORITY",
                "campaign_state": "EXISTING_NAVIGATOR_AUTHORITY",
                "llm_calculation_authority": "ZERO",
                "llm_state_authority": "ZERO",
            },
        }
        det = {
            "schema": "LOOM_E1_FLIGHT_RUNTIME_DETERMINISM_V1",
            "status": "PASS",
            "checks": {"canonical_runtime_hash": True},
            "canonical_runtime_sha256": hash1,
            "payload_sha256": {},
            "html_sha256": html_sha,
            "html_bytes": len(html.encode("utf-8")),
            "presentation_scope": "EXCLUDED_FROM_FLIGHT_SEAM_QUALIFICATION",
        }
        return runtime1, {}, html, validation, det

    core._loom_e1_original_target_determinism_gate = original
    core.target_determinism_gate = flight_runtime_determinism_gate
    core._loom_e1_flight_runtime_determinism_installed = True
