"""Decoder for Navigator's authoritative packed flight-solutions payload.

This module performs *no navigation math*. It only decodes Python-authored
Sequence-B display/state arrays using the codec declared by Navigator. The
renderer remains a consumer of Navigator truth, never an interpolator of it.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import struct
from typing import Any, Mapping


FLIGHT_PAYLOAD_VERSION = "3.0-SEQUENCE-B"
FLIGHT_BINARY_CODEC = "FLIGHT_DELTA2_VARINT53_V1"


class FlightPayloadDecodeError(ValueError):
    pass


def _read_uvarints(data: bytes, offset: int, length: int) -> list[int]:
    end = offset + length
    if offset < 0 or end > len(data):
        raise FlightPayloadDecodeError("binary series range is outside payload")
    out: list[int] = []
    value = 0
    shift = 0
    for byte in data[offset:end]:
        value |= (byte & 0x7F) << shift
        if byte & 0x80:
            shift += 7
            if shift > 63:
                raise FlightPayloadDecodeError("varint exceeds 64-bit safety bound")
            continue
        out.append(value)
        value = 0
        shift = 0
    if shift:
        raise FlightPayloadDecodeError("truncated varint series")
    return out


def _zigzag(value: int) -> int:
    return (value >> 1) ^ -(value & 1)


def _presence_indices(data: bytes, offset: int | None, length: int, count: int) -> list[int]:
    if not length:
        return list(range(count))
    if offset is None or offset < 0 or offset + length > len(data):
        raise FlightPayloadDecodeError("presence bitmap is outside payload")
    bits = data[offset:offset + length]
    return [i for i in range(count) if bits[i >> 3] & (1 << (i & 7))]


def _decode_series(desc: Mapping[str, Any], binary: bytes) -> list[float | None]:
    count = int(desc.get("count", 0))
    scale = float(desc.get("scale", 1.0))
    if count < 0 or not scale:
        raise FlightPayloadDecodeError("invalid series count/scale")
    present = _presence_indices(
        binary,
        desc.get("presence_offset"),
        int(desc.get("presence_bytes", 0) or 0),
        count,
    )
    expected_present = int(desc.get("present_count", len(present)))
    if expected_present != len(present):
        raise FlightPayloadDecodeError("presence bitmap count mismatch")
    codes = _read_uvarints(
        binary,
        int(desc.get("data_offset", 0)),
        int(desc.get("data_bytes", 0)),
    )
    if len(codes) != len(present):
        raise FlightPayloadDecodeError(
            f"series varint count mismatch: expected {len(present)}, got {len(codes)}"
        )

    values: list[float | None] = [None] * count
    base = float(desc.get("base", 0.0))
    current = base
    delta_q = 0
    for j, (index, encoded) in enumerate(zip(present, codes)):
        delta_q += _zigzag(encoded)
        if j == 0:
            current = base + delta_q / scale
        else:
            current += delta_q / scale
        values[index] = current
    return values


def _decode_column(column: Mapping[str, Any], binary: bytes) -> list[Any]:
    kind = column.get("type")
    if kind == "num":
        series = column.get("series")
        if not isinstance(series, Mapping):
            raise FlightPayloadDecodeError("numeric column missing series descriptor")
        return _decode_series(series, binary)
    if kind == "strdict":
        codes_desc = column.get("codes")
        values = column.get("values")
        if not isinstance(codes_desc, Mapping) or not isinstance(values, list):
            raise FlightPayloadDecodeError("string-dictionary column malformed")
        codes = _decode_series(codes_desc, binary)
        out: list[Any] = []
        for code in codes:
            if code is None:
                out.append(None)
                continue
            idx = int(round(code))
            if idx < 0 or idx >= len(values):
                raise FlightPayloadDecodeError(f"string dictionary code out of range: {idx}")
            out.append(values[idx])
        return out
    raise FlightPayloadDecodeError(f"unsupported packed column type: {kind!r}")


@dataclass(frozen=True)
class PackedFlightSolutions:
    metadata: Mapping[str, Any]
    binary: bytes

    @classmethod
    def decode_header(cls, payload: bytes | bytearray) -> "PackedFlightSolutions":
        if not isinstance(payload, (bytes, bytearray)) or len(payload) < 4:
            raise FlightPayloadDecodeError("packed flightSolutionsPayload bytes required")
        raw = bytes(payload)
        metadata_len = struct.unpack_from("<I", raw, 0)[0]
        end = 4 + metadata_len
        if metadata_len <= 0 or end > len(raw):
            raise FlightPayloadDecodeError("invalid packed metadata length")
        try:
            metadata = json.loads(raw[4:end].decode("utf-8"))
        except Exception as exc:
            raise FlightPayloadDecodeError("invalid packed metadata JSON") from exc
        if metadata.get("payload_version") != FLIGHT_PAYLOAD_VERSION:
            raise FlightPayloadDecodeError(
                f"unsupported flight payload version: {metadata.get('payload_version')!r}"
            )
        if metadata.get("_flight_binary_codec") != FLIGHT_BINARY_CODEC:
            raise FlightPayloadDecodeError(
                f"unsupported flight binary codec: {metadata.get('_flight_binary_codec')!r}"
            )
        return cls(metadata=metadata, binary=raw[end:])

    def block(self, ref: Mapping[str, Any] | str) -> Any:
        block_id = ref if isinstance(ref, str) else ref.get("$bin")
        if not block_id:
            raise FlightPayloadDecodeError("binary block reference missing")
        blocks = self.metadata.get("_flight_binary_blocks")
        if not isinstance(blocks, Mapping) or block_id not in blocks:
            raise FlightPayloadDecodeError(f"unknown binary block: {block_id}")
        desc = blocks[block_id]
        if not isinstance(desc, Mapping):
            raise FlightPayloadDecodeError("binary block descriptor malformed")
        if desc.get("kind") == "matrix":
            axes = desc.get("axes")
            rows = int(desc.get("rows", 0))
            cols = int(desc.get("cols", 0))
            if not isinstance(axes, list) or len(axes) != cols:
                raise FlightPayloadDecodeError("matrix axes/column count mismatch")
            decoded = [_decode_series(axis, self.binary) for axis in axes]
            if any(len(axis) != rows for axis in decoded):
                raise FlightPayloadDecodeError("decoded matrix row count mismatch")
            return [[decoded[c][r] for c in range(cols)] for r in range(rows)]
        if "columns" in desc:
            columns = desc.get("columns")
            rows = int(desc.get("rows", 0))
            if not isinstance(columns, list):
                raise FlightPayloadDecodeError("table columns malformed")
            decoded = [_decode_column(col, self.binary) for col in columns]
            if any(len(col) != rows for col in decoded):
                raise FlightPayloadDecodeError("decoded table row count mismatch")
            return [[decoded[c][r] for c in range(len(decoded))] for r in range(rows)]
        if "series" in desc and desc.get("type") in {"num", "strdict"}:
            return _decode_column(desc, self.binary)
        if all(k in desc for k in ("count", "data_offset", "data_bytes")):
            return _decode_series(desc, self.binary)
        raise FlightPayloadDecodeError(f"unsupported binary block descriptor for {block_id}")

    def select_solution(self, *, route_plan_id: str | None = None, solution_key: str | None = None) -> Mapping[str, Any]:
        plans = self.metadata.get("route_plans")
        if not isinstance(plans, Mapping) or not plans:
            raise FlightPayloadDecodeError("route_plans missing from flight payload")
        if route_plan_id and route_plan_id in plans:
            plan = plans[route_plan_id]
        elif len(plans) == 1:
            plan = next(iter(plans.values()))
        else:
            raise FlightPayloadDecodeError("route plan selection is ambiguous")
        solutions = plan.get("solutions") if isinstance(plan, Mapping) else None
        if not isinstance(solutions, Mapping) or not solutions:
            raise FlightPayloadDecodeError("solutions missing from route plan")
        if solution_key and solution_key in solutions:
            return solutions[solution_key]
        if len(solutions) == 1:
            return next(iter(solutions.values()))
        raise FlightPayloadDecodeError("flight solution selection is ambiguous")

    def timeline_rows(self, solution: Mapping[str, Any]) -> list[dict[str, Any]]:
        timeline = solution.get("timeline")
        contract = self.metadata.get("timeline_contract")
        if not isinstance(timeline, Mapping) or not isinstance(contract, Mapping):
            raise FlightPayloadDecodeError("timeline or timeline contract missing")
        ref = timeline.get("samples")
        if not isinstance(ref, Mapping):
            raise FlightPayloadDecodeError("timeline sample block missing")
        raw_rows = self.block(ref)
        field_index = contract.get("field_index")
        if not isinstance(field_index, Mapping):
            raise FlightPayloadDecodeError("timeline field index missing")
        names_by_index = {int(index): str(name) for name, index in field_index.items()}
        return [
            {names_by_index[i]: row[i] for i in range(len(row)) if i in names_by_index}
            for row in raw_rows
        ]


def decode_flight_solutions(payload: bytes | bytearray) -> PackedFlightSolutions:
    return PackedFlightSolutions.decode_header(payload)
