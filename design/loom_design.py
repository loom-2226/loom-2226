#!/usr/bin/env python3
"""LOOM design system: Python adapter, validator and CSS generator in one stdlib-only file.

Files this expects beside it: loom-tokens.json (tokens + $manifest), the three logo SVGs.

As a library (Pygame, Pillow, Rich, Termux ANSI):
    from loom_design import get, rgb, ansi_fg, status, type_style

    rgb("interface.surface.canvas")         # (5, 7, 11)
    status("caution")["label"]              # "CAUTION"
    ansi_fg("brand.color.accent.ion-blue")  # 24-bit ANSI foreground escape
    type_style("label")                     # size, weight, tracking, transform ...

As a command:
    python loom_design.py           # validate everything, then (re)write loom-tokens.css
    python loom_design.py --check   # validate; fail if loom-tokens.css is stale (CI)
    python loom_design.py --report  # also print contrast + colour-vision report

Rules for callers (see LOOM_STYLE_GUIDE.md): never hard-code a hex value that exists as a token;
render every status with its shape and label, not colour alone.
Exit code 0 = no errors (warnings allowed). 1 = at least one error.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
DESIGN = HERE
TOKENS_FILE = HERE / "loom-tokens.json"

_REF = re.compile(r"^\{([^{}]+)\}$")
_HEX = re.compile(r"^#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")


# =========================================================================== ADAPTER
LAYERS = ("brand", "interface", "domain")


class TokenError(Exception):
    """Raised for unknown tokens, alias cycles or malformed values."""


@dataclass(frozen=True)
class Token:
    path: str
    raw: Any
    type: str | None
    provenance: str | None
    description: str
    file: str

    @property
    def layer(self) -> str:
        return self.path.split(".", 1)[0]


def _walk(node: dict, prefix: str, inherited_type: str | None,
          inherited_prov: str | None, file: str, out: dict[str, Token]) -> None:
    node_type = node.get("$type", inherited_type)
    node_prov = (node.get("$extensions", {}).get("loom", {}).get("provenance", inherited_prov))
    if "$value" in node:
        out[prefix] = Token(prefix, node["$value"], node_type, node_prov,
                            node.get("$description", ""), file)
        return
    for key, child in node.items():
        if key.startswith("$") or not isinstance(child, dict):
            continue
        _walk(child, f"{prefix}.{key}" if prefix else key, node_type, node_prov, file, out)


@lru_cache(maxsize=4)
def raw(path: str | None = None) -> dict:
    """Parsed loom-tokens.json (including $manifest)."""
    return json.loads(Path(path or TOKENS_FILE).read_text(encoding="utf-8"))


def manifest() -> dict:
    return raw().get("$manifest", {})


@lru_cache(maxsize=4)
def load(path: str | None = None) -> dict[str, Token]:
    """Flatten all tokens into {dotted.path: Token}."""
    out: dict[str, Token] = {}
    for key, child in raw(path).items():
        if key.startswith("$") or not isinstance(child, dict):
            continue
        _walk(child, key, None, None, "loom-tokens.json", out)
    return out


def _resolve(value: Any, tokens: dict[str, Token], trail: tuple[str, ...]) -> Any:
    if isinstance(value, str):
        m = _REF.match(value)
        if not m:
            return value
        target = m.group(1)
        if target in trail:
            raise TokenError("alias cycle: " + " -> ".join(trail + (target,)))
        if target not in tokens:
            raise TokenError(f"unknown token reference {{{target}}}")
        return _resolve(tokens[target].raw, tokens, trail + (target,))
    if isinstance(value, dict):
        return {k: _resolve(v, tokens, trail) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve(v, tokens, trail) for v in value]
    return value


def get(path: str) -> Any:
    """Resolved value of a token, e.g. get('brand.color.accent.ion-blue') -> '#00D1FF'."""
    tokens = load()
    if path not in tokens:
        raise TokenError(f"unknown token '{path}'")
    return _resolve(tokens[path].raw, tokens, (path,))


def group(prefix: str) -> dict[str, Any]:
    """All resolved tokens beneath a prefix, keyed by the remaining path."""
    tokens = load()
    p = prefix.rstrip(".") + "."
    return {t.path[len(p):]: get(t.path) for t in tokens.values() if t.path.startswith(p)}


def rgba(path: str) -> tuple[int, int, int, float]:
    """(r, g, b, alpha 0..1) for a colour token."""
    v = get(path)
    if not isinstance(v, str) or not _HEX.match(v):
        raise TokenError(f"'{path}' is not a colour token (value: {v!r})")
    h = v[1:]
    a = int(h[6:8], 16) / 255 if len(h) == 8 else 1.0
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), round(a, 4)


def rgb(path: str) -> tuple[int, int, int]:
    r, g, b, _ = rgba(path)
    return r, g, b


def hex_color(path: str) -> str:
    return get(path)


def ansi_fg(path: str) -> str:
    """24-bit ANSI foreground escape (works in Termux)."""
    r, g, b = rgb(path)
    return f"\x1b[38;2;{r};{g};{b}m"


def ansi_bg(path: str) -> str:
    r, g, b = rgb(path)
    return f"\x1b[48;2;{r};{g};{b}m"


ANSI_RESET = "\x1b[0m"


def status(name: str) -> dict[str, Any]:
    """Resolved status record: color, shape, icon, label, severity, condition, threshold-source."""
    rec = group(f"domain.status.{name}")
    if not rec:
        raise TokenError(f"unknown status '{name}'")
    return rec


def certainty(name: str) -> dict[str, Any]:
    rec = group(f"domain.certainty.{name}")
    if not rec:
        raise TokenError(f"unknown certainty state '{name}'")
    return rec


def type_style(name: str) -> dict[str, Any]:
    """Resolved HUD type style: size, line-height, weight, tracking, transform, numeric."""
    rec = group(f"interface.type.style.{name}")
    if not rec:
        raise TokenError(f"unknown type style '{name}'")
    return rec


def font_family() -> list[str]:
    return list(get("brand.font.family.primary"))


def px(path: str) -> float:
    """Numeric pixel value of a dimension token expressed in px."""
    v = get(path)
    if not (isinstance(v, str) and v.endswith("px")):
        raise TokenError(f"'{path}' is not a px dimension (value: {v!r})")
    return float(v[:-2])


# =========================================================================== VALIDATOR / GENERATOR
KNOWN_TYPES = {"color", "dimension", "number", "fontFamily", "fontWeight",
               "duration", "cubicBezier", "shadow", "string"}
PROVENANCE = {"source", "observed", "derived", "proposed"}
DIM = re.compile(r"^-?\d+(\.\d+)?(px|rem|em)$")
DUR = re.compile(r"^\d+(\.\d+)?(ms|s)$")
HEX = re.compile(r"^#(?:[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})$")
GENERIC_FAMILIES = {"serif", "sans-serif", "monospace", "system-ui", "cursive", "fantasy"}
CSS_STRING_LEAVES = {"dash", "transform", "numeric"}
STATUS_FIELDS = ("color", "shape", "icon", "label", "severity", "condition", "threshold-source")

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


# --------------------------------------------------------------------------- colour maths
def _rgb(hexv: str) -> tuple[float, float, float]:
    h = hexv[1:]
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def _alpha(hexv: str) -> float:
    h = hexv[1:]
    return int(h[6:8], 16) / 255 if len(h) == 8 else 1.0


def _lin(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _lum(rgb: tuple[float, float, float]) -> float:
    r, g, b = (_lin(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg_hex: str, bg_hex: str) -> float:
    """WCAG contrast ratio; a translucent foreground is composited over the background."""
    bg = _rgb(bg_hex)
    fg = _rgb(fg_hex)
    a = _alpha(fg_hex)
    fg = tuple(a * f + (1 - a) * b for f, b in zip(fg, bg))
    l1, l2 = _lum(fg), _lum(bg)  # type: ignore[arg-type]
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


_CVD = {  # Machado et al. 2009, severity 1.0, applied in linear RGB
    "protanopia":   [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
    "deuteranopia": [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]],
    "tritanopia":   [[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]],
}


def _lab(lin_rgb: list[float] | tuple[float, ...]) -> tuple[float, float, float]:
    r, g, b = lin_rgb
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116  # noqa: E731
    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def delta_e(a_hex: str, b_hex: str, mode: str | None) -> float:
    def conv(h: str) -> tuple[float, float, float]:
        lin = [_lin(c) for c in _rgb(h)]
        if mode:
            m = _CVD[mode]
            lin = [min(1.0, max(0.0, sum(m[i][j] * lin[j] for j in range(3)))) for i in range(3)]
        return _lab(lin)
    return math.dist(conv(a_hex), conv(b_hex))


# --------------------------------------------------------------------------- validation
def manifest_or_none() -> dict | None:
    try:
        m = manifest()
    except (OSError, json.JSONDecodeError) as exc:
        err(f"cannot read loom-tokens.json: {exc}")
        return None
    return m or None


def refs_in(value: Any) -> list[str]:
    if isinstance(value, str):
        m = re.match(r"^\{([^{}]+)\}$", value)
        return [m.group(1)] if m else []
    if isinstance(value, dict):
        return [r for v in value.values() for r in refs_in(v)]
    if isinstance(value, list):
        return [r for v in value for r in refs_in(v)]
    return []


def check_value(path: str, ttype: str | None, v: Any) -> None:
    if ttype is None:
        err(f"{path}: no $type (set it on the token or an ancestor group)")
        return
    if ttype not in KNOWN_TYPES:
        err(f"{path}: unknown $type '{ttype}'")
        return
    ok = True
    if ttype == "color":
        ok = isinstance(v, str) and bool(HEX.match(v))
    elif ttype == "dimension":
        ok = isinstance(v, str) and bool(DIM.match(v))
    elif ttype == "number":
        ok = isinstance(v, (int, float)) and not isinstance(v, bool)
    elif ttype == "fontFamily":
        ok = isinstance(v, list) and len(v) > 0 and all(isinstance(x, str) and x for x in v)
    elif ttype == "fontWeight":
        ok = isinstance(v, int) and not isinstance(v, bool) and 1 <= v <= 1000
    elif ttype == "duration":
        ok = isinstance(v, str) and bool(DUR.match(v))
    elif ttype == "cubicBezier":
        ok = (isinstance(v, list) and len(v) == 4 and all(isinstance(x, (int, float)) for x in v)
              and 0 <= v[0] <= 1 and 0 <= v[2] <= 1)
    elif ttype == "shadow":
        ok = (isinstance(v, dict) and set(v) == {"color", "offsetX", "offsetY", "blur", "spread"}
              and bool(HEX.match(str(v["color"]))) and all(DIM.match(str(v[k])) for k in ("offsetX", "offsetY", "blur", "spread")))
    elif ttype == "string":
        ok = isinstance(v, str)
    if not ok:
        err(f"{path}: value {v!r} is not a valid {ttype}")


def validate_tokens(manifest: dict) -> dict[str, Token]:
    try:
        tokens = load()
    except (OSError, json.JSONDecodeError) as e:
        err(f"cannot load tokens: {e}")
        return {}
    layer_rules = {k: set(v["may_reference"]) | {k} for k, v in manifest["layers"].items()}

    for t in tokens.values():
        if t.layer not in layer_rules:
            err(f"{t.path}: top-level group '{t.layer}' is not a declared layer")
            continue
        if t.provenance not in PROVENANCE:
            err(f"{t.path}: missing or invalid provenance ({t.provenance!r})")
        for r in refs_in(t.raw):
            if r not in tokens:
                err(f"{t.path}: reference {{{r}}} does not exist")
            else:
                target_layer = tokens[r].layer
                if target_layer not in layer_rules[t.layer]:
                    err(f"{t.path}: {t.layer} layer may not reference {target_layer} layer ({{{r}}})")
        try:
            resolved = get(t.path)
        except TokenError as e:
            err(f"{t.path}: {e}")
            continue
        check_value(t.path, t.type, resolved)

    # duplicates and derived-colour consistency
    palette_rgb = {v[:7].upper() for k, t in tokens.items() if k.startswith("brand.color.")
                   for v in [t.raw] if isinstance(v, str) and HEX.match(v)}
    seen: dict[str, str] = {}
    for t in tokens.values():
        if t.type == "color" and isinstance(t.raw, str) and HEX.match(t.raw):
            key = t.raw.upper()
            if key in seen:
                err(f"duplicate colour {key}: {seen[key]} and {t.path} (alias one to the other)")
            else:
                seen[key] = t.path
            if len(key) == 9:
                if key[:7] not in palette_rgb:
                    err(f"{t.path}: alpha colour {key} is not an alpha variant of a brand palette colour")
                if t.provenance != "derived":
                    warn(f"{t.path}: alpha colour should carry provenance 'derived'")
        elif t.type == "shadow" and isinstance(t.raw, dict):
            if str(t.raw["color"])[:7].upper() not in palette_rgb:
                err(f"{t.path}: shadow colour is not a brand palette colour")
    return tokens


def validate_domain(tokens: dict[str, Token]) -> None:
    status_names = sorted({p.split(".")[2] for p in tokens if p.startswith("domain.status.")})
    recs = {}
    for n in status_names:
        rec = group(f"domain.status.{n}")
        missing = [f for f in STATUS_FIELDS if f not in rec]
        if missing:
            err(f"domain.status.{n}: missing {', '.join(missing)}")
        recs[n] = rec
    for field in ("shape", "icon", "label", "severity", "color"):
        vals = [r.get(field) for r in recs.values() if field in r]
        dup = [v for v, c in Counter(vals).items() if c > 1]
        if dup:
            err(f"domain.status: duplicate {field} {dup}: statuses must be distinguishable without colour")
    status_colours = {str(r["color"]).upper() for r in recs.values() if "color" in r}
    brand_hexes = {str(get(p)).upper() for p in tokens if p.startswith("brand.color.")}
    if status_colours & brand_hexes:
        err(f"status colours collide with brand palette: {sorted(status_colours & brand_hexes)}")
    hl = str(get("domain.selection.highlight")).upper()
    if hl in status_colours:
        err("domain.selection.highlight must not equal a status colour")
    undefined = [n for n, r in recs.items() if r.get("threshold-source") == "UNDEFINED"]
    if undefined:
        warn(f"status threshold-source is UNDEFINED for: {', '.join(undefined)} "
             "(each producing system must cite its governing spec before shipping these states)")

    cert = {p.split(".")[2]: group(f"domain.certainty.{p.split('.')[2]}")
            for p in tokens if p.startswith("domain.certainty.")}
    sig = [(c.get("dash"), c.get("affix"), c.get("label")) for c in cert.values()]
    if len(set(sig)) != len(sig):
        err("domain.certainty: states must differ in dash/affix/label")
    for n, c in cert.items():
        if str(c.get("color", "")).upper() in status_colours:
            err(f"domain.certainty.{n}: uncertainty must not use a status colour")

    routes = {p.split(".")[2] for p in tokens if p.startswith("domain.nav.")}
    sigs = {}
    for r in sorted(routes):
        rec = group(f"domain.nav.{r}")
        sigs[r] = (rec.get("dash"), rec.get("width"), rec.get("marker"))
    dups = [k for k, c in Counter(sigs.values()).items() if c > 1]
    if dups:
        err(f"domain.nav: states share dash+width+marker {dups}: they would be identical in greyscale")


def validate_assets(manifest: dict) -> None:
    for group_name, files in manifest["assets"].items():
        for rel in files:
            p = DESIGN / rel
            if not p.is_file():
                err(f"missing asset: {rel}")
                continue
            if p.suffix == ".svg":
                try:
                    root = ET.parse(p).getroot()
                except ET.ParseError as e:
                    err(f"{rel}: malformed SVG ({e})")
                    continue
                if not any(el.tag.endswith("title") for el in root.iter()):
                    warn(f"{rel}: SVG has no <title> (accessibility)")
    for rel in manifest["sources"]:
        if not (DESIGN / rel["path"]).is_file():
            err(f"missing source reference: {rel['path']}")
    for rel in manifest["fonts"]["files"]:
        if not (DESIGN / rel).is_file():
            warn(f"font file not present: {rel} (see LOOM_STYLE_GUIDE.md Appendix B); UI falls back to the system stack")
    for rel in [manifest["fonts"]["css"], *manifest["generated"]]:
        if not (DESIGN / rel).is_file() and rel not in manifest["generated"]:
            err(f"missing file: {rel}")


def validate_manifest(manifest: dict) -> None:
    status = manifest.get("status")
    appr = manifest.get("approval", {})
    if status not in {"DRAFT", "APPROVED"}:
        err(f"manifest.status must be DRAFT or APPROVED (got {status!r})")
    if status == "DRAFT" and appr.get("approved"):
        err("manifest.status is DRAFT but approval.approved is true")
    if status == "APPROVED" and not (appr.get("approved") and appr.get("approved_by") and appr.get("approved_on")):
        err("manifest.status is APPROVED but approval.approved/approved_by/approved_on are not all set")
    if status == "DRAFT" and not str(manifest.get("version", "")).endswith("-draft"):
        err("DRAFT versions must carry a '-draft' suffix")


def contrast_rows(manifest: dict) -> list[dict]:
    rows = []
    surface_hex = lambda p: get(p)  # noqa: E731
    for chk in manifest["checks"]["contrast"]:
        fg_path = chk["fg"]
        try:
            fg = surface_hex(fg_path)
        except TokenError as e:
            err(f"contrast check '{chk['use']}': {e}")
            continue
        for bg_path in chk["bg"]:
            try:
                bg = surface_hex(bg_path)
            except TokenError as e:
                err(f"contrast check '{chk['use']}': {e}")
                continue
            ratio = contrast(fg, bg)
            ok = ratio >= chk["min"]
            rows.append({"use": chk["use"], "fg": fg_path, "bg": bg_path, "ratio": ratio,
                         "min": chk["min"], "ok": ok})
            if not ok:
                err(f"contrast {ratio:.2f}:1 < {chk['min']}:1 for {fg_path} on {bg_path} ({chk['use']})")
    return rows


def cvd_rows(manifest: dict, tokens: dict[str, Token]) -> list[dict]:
    threshold = manifest["checks"]["cvd_min_delta_e_warn"]
    names = sorted({p.split(".")[2] for p in tokens if p.startswith("domain.status.")},
                   key=lambda n: get(f"domain.status.{n}.severity"))
    cols = {n: str(get(f"domain.status.{n}.color")) for n in names}
    cols["selection"] = str(get("domain.selection.highlight"))
    rows = []
    for a, b in itertools.combinations(cols, 2):
        d = {"normal": delta_e(cols[a], cols[b], None)}
        for mode in _CVD:
            d[mode] = delta_e(cols[a], cols[b], mode)
        d["min"] = min(d.values())
        rows.append({"a": a, "b": b, **d, "low": d["min"] < threshold})
    return rows


# --------------------------------------------------------------------------- generation
def _css_family(names: list[str]) -> str:
    return ", ".join(n if n in GENERIC_FAMILIES or re.fullmatch(r"[A-Za-z][A-Za-z0-9-]*", n) else f'"{n}"' for n in names)


def _css_name(path: str) -> str:
    return "--loom-" + path.replace(".", "-")


def _css_literal(t: Token, v: Any) -> str:
    if t.type == "fontFamily":
        return _css_family(v)
    if t.type == "cubicBezier":
        return "cubic-bezier(" + ", ".join(f"{x:g}" for x in v) + ")"
    if t.type == "shadow":
        return f"{v['offsetX']} {v['offsetY']} {v['blur']} {v['spread']} {v['color']}"
    if t.type == "number":
        return f"{v:g}"
    return str(v)


def build_css(tokens: dict[str, Token], manifest: dict) -> str:
    out = [
        "/* GENERATED by loom_design.py. DO NOT EDIT.",
        f"   LOOM design tokens v{manifest['version']} ({manifest['status']}).",
        "   Edit loom-tokens.json and run: python loom_design.py. */",
        "",
        "@font-face {",
        '  font-family: "Montserrat";',
        "  font-style: normal;",
        "  font-weight: 100 900;",
        "  font-display: swap;",
        '  src: local("Montserrat"), url("./Montserrat-VF.woff2") format("woff2");',
        "}",
        "",
        ":root {",
    ]
    for t in tokens.values():
        leaf = t.path.rsplit(".", 1)[-1]
        if t.type == "string" and leaf not in CSS_STRING_LEAVES:
            continue
        refs = refs_in(t.raw)
        if isinstance(t.raw, str) and len(refs) == 1 and refs[0] in tokens:
            tgt = tokens[refs[0]]
            tgt_leaf = tgt.path.rsplit(".", 1)[-1]
            if not (tgt.type == "string" and tgt_leaf not in CSS_STRING_LEAVES):
                out.append(f"  {_css_name(t.path)}: var({_css_name(refs[0])});")
                continue
        out.append(f"  {_css_name(t.path)}: {_css_literal(t, get(t.path))};")
    out += ["}", ""]

    styles = sorted({p.split(".")[3] for p in tokens if p.startswith("interface.type.style.")})
    out.append("/* HUD type styles: <p class=\"loom-type-body\"> */")
    for s in styles:
        base = f"--loom-interface-type-style-{s}"
        out += [
            f".loom-type-{s} {{",
            "  font-family: var(--loom-brand-font-family-primary);",
            f"  font-size: var({base}-size);",
            f"  line-height: var({base}-line-height);",
            f"  font-weight: var({base}-weight);",
            f"  letter-spacing: var({base}-tracking);",
            f"  text-transform: var({base}-transform);",
            f"  font-variant-numeric: var({base}-numeric);",
            "}",
        ]
    out.append("")
    out.append("/* Status and certainty colour hooks. Components must ALSO render the status shape and label. */")
    for n in sorted({p.split(".")[2] for p in tokens if p.startswith("domain.status.")}):
        out.append(f'[data-loom-status="{n}"] {{ --loom-status-color: var(--loom-domain-status-{n}-color); }}')
    for n in sorted({p.split(".")[2] for p in tokens if p.startswith("domain.certainty.")}):
        out.append(f'[data-loom-certainty="{n}"] {{ --loom-certainty-color: var(--loom-domain-certainty-{n}-color); }}')
    out += [
        "",
        "/* Keyboard focus: always visible. */",
        ":where(a, button, input, select, textarea, summary, [tabindex]):focus-visible {",
        "  outline: var(--loom-interface-focus-ring-width) solid var(--loom-interface-focus-ring-color);",
        "  outline-offset: var(--loom-interface-focus-ring-offset);",
        "}",
        "",
        "/* Motion: honour the user's preference. */",
        "@media (prefers-reduced-motion: reduce) {",
        "  :root {",
        "    --loom-interface-motion-duration-fast: 0ms;",
        "    --loom-interface-motion-duration-base: 0ms;",
        "    --loom-interface-motion-duration-slow: 0ms;",
        "  }",
        "}",
        "",
    ]
    return "\n".join(out)


def build_report(tokens: dict[str, Token], manifest: dict, crows: list[dict], vrows: list[dict]) -> str:
    out = [
        "<!-- Generated by loom_design.py --report -->",
        f"# LOOM design system: generated report (v{manifest['version']}, {manifest['status']})",
        "",
        "## Token provenance by layer",
        "",
        "| Layer | source | observed | derived | proposed | total |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for layer in LAYERS:
        c = Counter(t.provenance for t in tokens.values() if t.layer == layer)
        total = sum(c.values())
        out.append(f"| {layer} | {c['source']} | {c['observed']} | {c['derived']} | {c['proposed']} | {total} |")
    out += [
        "",
        "`proposed` and `observed` tokens are not on the brand sheet and need owner approval before the system leaves DRAFT.",
        "",
        "## WCAG contrast (text 4.5:1, graphics 3:1)",
        "",
        "| Use | Foreground | Background | Ratio | Minimum | Result |",
        "|---|---|---|---:|---:|---|",
    ]
    for r in crows:
        out.append(f"| {r['use']} | `{r['fg']}` | `{r['bg']}` | {r['ratio']:.2f} | {r['min']:g} | {'PASS' if r['ok'] else 'FAIL'} |")
    out += [
        "",
        "## Colour-vision-deficiency separation of status colours",
        "",
        "CIE76 delta-E between colour pairs, simulated (Machado 2009, severity 1.0). Below "
        f"{manifest['checks']['cvd_min_delta_e_warn']} the pair is hard to tell apart by colour alone, "
        "so shape and label are what carry the meaning there. Shape and label are required for every status regardless of these numbers.",
        "",
        "| Pair | Normal | Protan | Deutan | Tritan | Min | Colour reliable on its own? |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for r in vrows:
        out.append(f"| {r['a']} / {r['b']} | {r['normal']:.0f} | {r['protanopia']:.0f} | {r['deuteranopia']:.0f} | "
                   f"{r['tritanopia']:.0f} | {r['min']:.0f} | {'NO (below threshold)' if r['low'] else 'marginal at best; still add shape + label'} |")
    out.append("")
    return "\n".join(out)


def write_or_check(rel: str, content: str, check: bool) -> None:
    p = DESIGN / rel
    if check:
        if not p.is_file() or p.read_text(encoding="utf-8") != content:
            err(f"generated file is stale: {rel} (run: python loom_design.py)")
    else:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="do not write; fail if loom-tokens.css is stale")
    ap.add_argument("--report", action="store_true", help="also print the contrast / colour-vision report (Markdown)")
    args = ap.parse_args()

    manifest = manifest_or_none()
    if manifest is None:
        print("ERROR: cannot read $manifest in loom-tokens.json", file=sys.stderr)
        return 1
    validate_manifest(manifest)
    tokens = validate_tokens(manifest)
    crows: list[dict] = []
    vrows: list[dict] = []
    if tokens:
        try:
            validate_domain(tokens)
            crows = contrast_rows(manifest)
            vrows = cvd_rows(manifest, tokens)
        except TokenError as e:
            err(f"cannot complete semantic checks: {e}")
    validate_assets(manifest)

    generated = bool(tokens) and not errors
    report_text = ""
    if generated:
        write_or_check("loom-tokens.css", build_css(tokens, manifest), args.check)
        report_text = build_report(tokens, manifest, crows, vrows)

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    n = len(tokens)
    if args.report and report_text:
        print(report_text)
    if not generated:
        tail = "loom-tokens.css NOT written (fix errors first)."
    else:
        tail = "loom-tokens.css checked." if args.check else "loom-tokens.css written."
    print(f"{'FAIL' if errors else 'OK'}: {n} tokens, {len(crows)} contrast checks, "
          f"{len(errors)} error(s), {len(warnings)} warning(s); {tail}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
