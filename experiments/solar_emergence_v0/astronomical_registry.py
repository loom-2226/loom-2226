"""Frozen, source-backed Solar candidate identities for the Run-1 experiment."""

from __future__ import annotations

import hashlib
import gzip
import json
import re
from html.parser import HTMLParser
from pathlib import Path


class _DiscoveryTable(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows: list[list[str]] = []
        self.row: list[str] | None = None
        self.cell: list[str] | None = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell = []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.cell is not None:
            self.row.append(" ".join(" ".join(self.cell).split()))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)


def parse_discovery_html(html: str) -> list[dict]:
    parser = _DiscoveryTable()
    parser.feed(html)
    rows = []
    parent = None
    for cells in parser.rows:
        if len(cells) == 1 and cells[0].startswith("Satellites of"):
            heading = cells[0].split(":", 1)[0]
            parent = heading.removeprefix("Satellites of").strip().removeprefix("Dwarf Planet ")
        elif len(cells) >= 3 and parent:
            rows.append({
                "parent_name": parent,
                "iau_number": cells[0] or None,
                "iau_name": cells[1] or None,
                "provisional_designation": cells[2] or None,
            })
    return rows


def parse_horizons_major_bodies(text: str) -> list[dict]:
    records = []
    for line in text.splitlines():
        fields = re.split(r"\s{2,}", line.strip(), maxsplit=3)
        if len(fields) >= 2 and re.fullmatch(r"-?\d+", fields[0]):
            records.append({
                "naif_id": fields[0],
                "display_name": fields[1],
                "aliases": " ".join(fields[2:]),
            })
    return records


def normalize_named_moons(
    discovery_rows: list[dict], major_bodies: list[dict],
    planets: list[dict], dwarf_planets: list[dict], *, include_supplements: bool = True,
) -> tuple[list[dict], int]:
    """Require both permanent JPL discovery name and unique Horizons identity."""
    physical_parents = {r["display_name"]: r for r in (*planets, *dwarf_planets)}
    by_name: dict[str, list[dict]] = {}
    for row in major_bodies:
        by_name.setdefault(row["display_name"].casefold(), []).append(row)
    moons = []
    excluded_provisional = 0
    for row in discovery_rows:
        if row["parent_name"] not in physical_parents:
            continue
        if not row["iau_name"] or not row["iau_number"]:
            excluded_provisional += 1
            continue
        matches = by_name.get(row["iau_name"].casefold(), [])
        if len(matches) != 1:
            raise ValueError(f"Named moon lacks unique Horizons ID: {row['iau_name']}")
        moon = matches[0]
        moons.append({
            "display_name": row["iau_name"], "iau_name": row["iau_name"],
            "iau_number": row["iau_number"],
            "provisional_designation": row["provisional_designation"],
            "parent_name": row["parent_name"],
            "parent_naif_id": physical_parents[row["parent_name"]]["naif_id"],
            "naif_id": moon["naif_id"], "horizons_target_id": moon["naif_id"],
            "registry_source": "JPL_SATELLITE_DISCOVERY_AND_HORIZONS_MB",
        })
    if include_supplements:
        # The JPL discovery table explicitly excludes Earth; the major-body list
        # itself gives the stable identity for the Moon.
        earth = physical_parents.get("Earth")
        moon_matches = by_name.get("moon", [])
        if earth is None or len(moon_matches) != 1:
            raise ValueError("Earth-Moon major-body identity unavailable")
        moon = moon_matches[0]
        moons.append({
            "display_name": "Moon", "iau_name": "Moon", "iau_number": "I",
            "provisional_designation": None, "parent_name": "Earth",
            "parent_naif_id": earth["naif_id"], "naif_id": moon["naif_id"],
            "horizons_target_id": moon["naif_id"],
            "registry_source": "JPL_HORIZONS_MB_EARTH_MOON",
        })
        # JPL's planetary discovery table includes Pluto, but not satellites of
        # other dwarf planets. The major-body aliases identify named satellites
        # as '<recognized dwarf name> <IAU Roman number>'.
        for parent_name, parent in physical_parents.items():
            if parent.get("body_class") != "DWARF_PLANET" or parent_name == "Pluto":
                continue
            pattern = re.compile(rf"\b{re.escape(parent_name)}\s+([IVXLCDM]+)\b")
            for body in major_bodies:
                match = pattern.search(body["aliases"])
                if not match or not body["display_name"] or "(" in body["display_name"]:
                    continue
                moons.append({
                    "display_name": body["display_name"],
                    "iau_name": body["display_name"], "iau_number": match.group(1),
                    "provisional_designation": None, "parent_name": parent_name,
                    "parent_naif_id": parent["naif_id"], "naif_id": body["naif_id"],
                    "horizons_target_id": body["naif_id"],
                    "registry_source": "JPL_HORIZONS_MB_DWARF_SATELLITE",
                })
    keys = [(m["parent_name"], m["naif_id"]) for m in moons]
    if len(keys) != len(set(keys)) or len({m["naif_id"] for m in moons}) != len(moons):
        raise ValueError("Duplicate named-moon astronomical identity")
    return sorted(moons, key=lambda row: (row["parent_name"], int(row["naif_id"]))), excluded_provisional


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_frozen_sources(source_dir: Path) -> dict:
    source_dir = Path(source_dir)
    manifest = json.loads((source_dir / "source_manifest.json").read_text(encoding="utf-8"))
    for entry in manifest["files"]:
        path = source_dir / entry["path"]
        if _sha256(path) != entry["sha256"]:
            raise ValueError(f"Frozen astronomical source hash mismatch: {path}")
    raw_major = gzip.decompress((source_dir / "raw" / "solar_horizons_mb.raw.gz").read_bytes())
    if hashlib.sha256(raw_major).hexdigest() != next(
        source["raw_response_sha256"] for source in manifest["sources"]
        if source["name"] == "Horizons major-body list (COMMAND=MB)"
    ):
        raise ValueError("Compressed Horizons response differs from frozen raw SHA-256")
    trimmed_major = "\n".join(line.rstrip() for line in raw_major.decode("utf-8").splitlines()) + "\n"
    if trimmed_major != (source_dir / "raw" / "solar_horizons_mb.txt").read_text(encoding="utf-8"):
        raise ValueError("Horizons parser text differs from whitespace-normalized raw response")
    raw_discovery = gzip.decompress((source_dir / "raw" / "solar_sats_discovery.raw.gz").read_bytes())
    if hashlib.sha256(raw_discovery).hexdigest() != next(
        source["raw_response_sha256"] for source in manifest["sources"]
        if source["name"] == "Planetary Satellite Discovery Circumstances"
    ):
        raise ValueError("Compressed satellite discovery response differs from frozen raw SHA-256")
    trimmed_discovery = "\n".join(line.rstrip() for line in raw_discovery.decode("utf-8").splitlines()) + "\n"
    if trimmed_discovery != (source_dir / "raw" / "solar_sats_discovery.html").read_text(encoding="utf-8"):
        raise ValueError("Satellite discovery parser HTML differs from whitespace-normalized raw response")
    result = {"manifest": manifest, "excluded_provisional_count": manifest["excluded_provisional_count"]}
    for key, filename in (("planets", "normalized_planets.json"),
                          ("dwarf_planets", "normalized_dwarf_planets.json"),
                          ("moons", "normalized_moons.json")):
        result[key] = json.loads((source_dir / filename).read_text(encoding="utf-8"))[key]
    major = parse_horizons_major_bodies((source_dir / "raw" / "solar_horizons_mb.txt").read_text(encoding="utf-8"))
    discovery = parse_discovery_html((source_dir / "raw" / "solar_sats_discovery.html").read_text(encoding="utf-8"))
    moons, excluded = normalize_named_moons(discovery, major, result["planets"], result["dwarf_planets"])
    if moons != result["moons"] or excluded != result["excluded_provisional_count"]:
        raise ValueError("Frozen normalized moon registry disagrees with retained JPL source")
    return result


def build_astronomical_registry(sources: dict, conn, root: Path) -> list[dict]:
    """Union frozen astronomy and existing LOOM asteroids/reference identities."""
    from body_opportunities import build_catalog

    gis = build_catalog(conn)
    by_name_class = {(r["name"].casefold(), r["body_class"]): r for r in gis}
    by_name_bary = {r["name"].casefold(): r for r in gis if r["body_class"] == "SYSTEM_BARYCENTER"}
    if len(by_name_class) != len(gis):
        raise ValueError("Ambiguous GIS name/class mapping")
    records = []
    physical_by_naif = {}

    for source in (*sources["planets"], *sources["dwarf_planets"]):
        name = source["display_name"]
        match = by_name_class.get((name.casefold(), source["body_class"]))
        bary = by_name_bary.get(name.casefold())
        body_id = match["body_id"] if match else f"NAIF_{source['naif_id']}"
        row = {
            "body_id": body_id, "display_name": name,
            "body_class": source["body_class"],
            "physical_subclass": source["physical_subclass"],
            "candidate_role": "PHYSICAL_BODY",
            "naif_id": source["naif_id"],
            "horizons_target_id": source["horizons_target_id"],
            "iau_name": name,
            "parent_body_id": "SOL", "parent_naif_id": "10",
            "reference_body_id": bary["body_id"] if bary else None,
            "loom_entity_id": match["body_id"] if match else None,
            "loom_entity_class": match["body_class"] if match else None,
            "loom_parent_entity_id": match["parent_body_id"] if match else None,
            "conflicting_loom_barycenter_id": bary["body_id"] if bary else None,
            "loom_mapping_status": ("EXACT" if match else
                                    "BARYCENTER_CONFLICT_AVOIDED" if bary else "NOT_CURRENTLY_REGISTERED"),
            "registry_source": source["registry_source"],
            "registry_status": "FROZEN_EXPERIMENTAL_ASTRONOMICAL_IDENTITY",
            "ephemeris_identity_status": source["ephemeris_identity_status"],
        }
        records.append(row)
        physical_by_naif[row["naif_id"]] = row

    for source in sources["moons"]:
        parent = physical_by_naif.get(source["parent_naif_id"])
        if parent is None:
            raise ValueError(f"Moon lacks physical parent: {source['display_name']}")
        match = by_name_class.get((source["display_name"].casefold(), "MOON"))
        records.append({
            "body_id": match["body_id"] if match else f"NAIF_{source['naif_id']}",
            "display_name": source["display_name"], "body_class": "MOON",
            "physical_subclass": "MOON", "candidate_role": "PHYSICAL_BODY",
            "naif_id": source["naif_id"],
            "horizons_target_id": source["horizons_target_id"],
            "iau_name": source["iau_name"],
            "parent_body_id": parent["body_id"],
            "parent_naif_id": parent["naif_id"],
            "reference_body_id": parent["reference_body_id"],
            "loom_entity_id": match["body_id"] if match else None,
            "loom_entity_class": match["body_class"] if match else None,
            "loom_parent_entity_id": match["parent_body_id"] if match else None,
            "conflicting_loom_barycenter_id": None,
            "loom_mapping_status": "EXACT" if match else "NOT_CURRENTLY_REGISTERED",
            "registry_source": source["registry_source"],
            "registry_status": "FROZEN_EXPERIMENTAL_ASTRONOMICAL_IDENTITY",
            "ephemeris_identity_status": "JPL_HORIZONS_MAJOR_BODY_ID",
        })

    for source in gis:
        if source["body_class"] not in ("ASTEROID", "STAR", "SYSTEM_BARYCENTER"):
            continue
        source_command = source["registry_provenance"]["source_command"]
        naif_id = ("10" if source["body_class"] == "STAR" else
                   source_command if source["body_class"] == "SYSTEM_BARYCENTER" else None)
        records.append({
            "body_id": source["body_id"], "display_name": source["name"],
            "body_class": source["body_class"],
            "physical_subclass": source["body_class"],
            "candidate_role": source["candidate_role"],
            "naif_id": naif_id, "horizons_target_id": source_command or naif_id,
            "iau_name": None,
            "parent_body_id": source["parent_body_id"],
            "parent_naif_id": "10" if source["parent_body_id"] == "SOL" else None,
            "reference_body_id": None,
            "loom_entity_id": source["body_id"],
            "loom_entity_class": source["body_class"],
            "loom_parent_entity_id": source["parent_body_id"],
            "conflicting_loom_barycenter_id": None,
            "loom_mapping_status": "REFERENCE_ONLY" if source["candidate_role"] != "PHYSICAL_BODY" else "EXACT",
            "registry_source": "LOOM_SOLAR_GIS_EXPLICIT_ENTITY",
            "registry_status": "FROZEN_EXPERIMENTAL_ASTRONOMICAL_IDENTITY",
            "ephemeris_identity_status": "JPL_HORIZONS_MAJOR_BODY_ID" if naif_id else "LOOM_HORIZONS_COMMAND",
        })
    ids = [r["body_id"] for r in records]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate experiment body ID")
    naif = [r["naif_id"] for r in records if r["naif_id"] is not None]
    if len(naif) != len(set(naif)):
        raise ValueError("Duplicate astronomical identity")
    return sorted(records, key=lambda row: row["body_id"])
