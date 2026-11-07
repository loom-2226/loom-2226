#!/usr/bin/env python3
"""Reproducible 409-hit Wayfarer B-rep triage. Research, credit zero."""
import argparse
import collections
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parent
HASH="274e94fb43cfe549a3d2087abbdff4d65499ce6f5055ad2d7ade790414fbaaf9"
DISPLAY=re.compile(r"^(room_|outfit_|i4_|crown_|viewport_band_|wws1_|window_|bow_sensors|command_terrace|navigator_platform|node_mount_allowance)")
STRUCT=re.compile(r"^(armor|pressure_vessel|frame_|floor_|longeron_|skin_|tank_shell_|bay_liner|bay_corner_|door_|thrust_cone|docking_collar|tunnel_|hatch_|trunk_plug_)")
CHILD=re.compile(r"^(house_reactor_|house_peak_store|house_energy_battery|c_lite_dry)")

def name(x):
    if x.startswith("dry:"):return x[4:]
    if x.startswith("CORE_FULL:"):return x[10:]
    if x.startswith("S1:"):return x.split(":")[1]
    raise ValueError(x)

def classify(h):
    ids=(h["a"],h["b"])
    names=tuple(map(name,ids))
    both=all(x.startswith("dry:") for x in ids)
    if "dry:house_fuel_tank" in ids and any(x.startswith("S1:house_fuel:") for x in ids):
        return "a","S1 D-He3 fuel inside its named dry storage-envelope"
    if "dry:c_lite_dry" in ids and any(x.startswith("S1:c_lite_monoprop:") for x in ids):
        return "a","S1 C-lite monoprop inside named dry storage-envelope"
    if any(x.startswith("CORE_FULL:water_") for x in ids) and any(x.startswith("S1:water_") for x in ids) and names[0]==names[1]:
        return "b","same water core cell represented as filled S1 and full analytical envelope"
    if "node_mount_allowance" in names:
        return "c","node mount full-ring no_render allocation; actual attachment location explicitly OPEN"
    if any(DISPLAY.match(x) for x in names):
        return "c","authored room/fixture/window/crown/layer representation or allocation proxy"
    if both and all(STRUCT.match(x) for x in names):
        return "c","source structural connection or attachment envelope"
    if both and any(x.startswith("strake_") for x in names) and any(re.match(r"^(skin_|tank_shell_|frame_|bay_corner_)",x) for x in names):
        return "c","strake root intersects authored skin/groove/support envelope"
    if both and all(re.match(r"^hotfin(_root)?_",x) for x in names):
        return "c","hot-fin folded panel and corresponding root-assembly proxy"
    if "dry:electrical_fwd" in ids and any(x.startswith("S1:c_lite_monoprop:") for x in ids):
        return "c","source C-lite fluid explicitly hosted inside the broad forward electrical allocation sector"
    if both and any(x in ("electrical","electrical_fwd") for x in names) and any(CHILD.match(x) for x in names):
        return "c","component within broad electrical allocation sector"
    if both and set(names)=={"core_trunk","trunk_plug_L4L5"}:
        return "c","trunk isolation plug intentionally closes trunk"
    if both and set(names)=={"tunnel_1","tunnel_2"}:
        return "c","connected service tunnel segments intentionally meet"
    if both and set(names)=={"thrust_cone","shield"}:
        return "c","thrust-cone and shield authored mechanical interface"
    if both and any(x in ("armor","pressure_vessel") for x in names) and any(x.startswith("rcs_") for x in names):
        return "c","RCS thruster hull-mounted footprint"
    if both and any(x.startswith("ext_") for x in names) and any(STRUCT.match(x) for x in names):
        return "c","external hardware mounted on structure; unqualified local attachment"
    if set(names)=={"courier_systems","service_arm"}:
        return "d","two independently booked systems share IDENTICAL sector without fit design"
    if all(x.startswith("S1:jacket_") for x in ids):
        return "d","separately mass-booked water jacket segments intrude; check double-count"
    if any(x in ("house_fuel","house_fuel_tank") for x in names) and any(x.startswith("water_") for x in names):
        return "d","independent fuel and remass water occupy the same envelope (G1)"
    if any(x.startswith("strake_") for x in names):
        return "d","stowed radiator intersects separately allocated hardware/fluid"
    return "d","independent components intersect without evidence of permissible installed co-location"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--report",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    raw=(ROOT/"geometry_base.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==HASH
    source=json.loads(raw)
    parent=args.report.read_bytes()
    fit=json.loads(parent)
    hits=fit["ALL_CLASH_HITS_GT_0p01_M3"]
    assert len(hits)==fit["acceptance"]["A3_all_clashes"]["hits_gt_0p01_m3"]==409
    assert fit["acceptance"]["A3_all_clashes"]["pass"]
    records=[]
    for i,h in enumerate(hits):
        assert h["m3"]>0.01
        cat,reason=classify(h)
        records.append({"original_hit":i+1,"category":cat,"a":h["a"],"b":h["b"],"m3":h["m3"],"why":reason})
    counts=collections.Counter(x["category"] for x in records)
    assert sum(counts.values())==409 and set(counts)==set("abcd")
    byid={p["id"]:p for p in source["parts"]}
    courier=next(x for x in records if set((x["a"],x["b"]))=={"dry:courier_systems","dry:service_arm"})
    assert courier["category"]=="d" and abs(courier["m3"]-34.14125816)<1e-5
    assert byid["courier_systems"]["shape"]==byid["service_arm"]["shape"]
    zero=[x for x in fit["g8"]["source_proxy_checks"] if abs(x["measured_m"]-x["threshold_m"])<1e-9]
    assert {x["test"] for x in zero}=={"forward axial","aft axial","exit slot edge","exit open doors"}
    I=json.loads((ROOT/"inputs_base.json").read_bytes())
    fin=I["hot_fins"]
    fins=[p for p in source["parts"] if re.fullmatch(r"hotfin_\d+",p["id"])]
    roots=[p for p in source["parts"] if re.fullmatch(r"hotfin_root_\d+",p["id"])]
    assert len(fins)==len(roots)==4
    assert all(p["shape"]["span"]==fin["pleat_m"]==2 for p in fins)
    deployed=fin["pleat_m"]*fin["pleats"]
    chord=fin["x_m"][1]-fin["x_m"][0]
    area=2*len(fins)*chord*deployed
    panels_t=area*fin["kg_per_m2_face"]/1000
    roots_t=sum(p["mass_t"] for p in roots)
    assert abs(panels_t-sum(p["mass_t"] for p in fins))<1e-6
    assert abs(roots_t-fin["allowance_t"])<1e-6
    out={
        "scope":"LOOM 2026-2226 NON-GOVERNING RESEARCH; CREDIT ZERO",
        "source_geometry_sha256":HASH,
        "source_fit_report_sha256":hashlib.sha256(parent).hexdigest(),
        "categories":{"a":"source fluid in named dry container","b":"S1 vs CORE_FULL duplicate cell envelope",
                      "c":"authored intentional co-location, layer or allocation proxy",
                      "d":"unresolved installed-fit conflict; not proof of impossible physical design"},
        "counts":{x:counts[x] for x in "abcd"},"all_hits":records,
        "conflicts_d":[x for x in records if x["category"]=="d"],
        "courier_systems_service_arm":{
            "m3":courier["m3"],"source_exact_same_sector":byid["courier_systems"]["shape"],
            "courier_mass_t":byid["courier_systems"]["mass_t"],
            "service_arm_mass_t":byid["service_arm"]["mass_t"],
            "disposition":"d: two independently booked systems, no physical fit allocation"},
        "G8_0p000_margin_checks":zero,
        "hot_fins_finding_6":{"source_folded_BRep_radial_span_m":2,
            "deployed_pleats":fin["pleats"],"pleat_m":fin["pleat_m"],
            "deployed_radial_span_m":deployed,"axial_chord_m":chord,
            "two_sided_total_area_m2":area,"source_panels_t":panels_t,
            "root_and_hot_loop_allowance_t":roots_t,"full_assembly_t":panels_t+roots_t,
            "deployed_solids_present":False,
            "status":"UPSTREAM FINDING #6; deployed geometry/clearance not tested; zero credit"},
        "qualification":"not passed for complete installed fit",
        "credits":{"tonnes":0,"performance":0,"canon":False}}
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/"clash_triage.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    table=[
        "# #156 409-hit clash triage: complete category (d) table",
        "",
        "ALL bodies. ALL sponsors. 2026-2226. RESEARCH ONLY; CREDIT ZERO.",
        "",
        "All 409 hits are individually classified in clash_triage.json. "
        "Category (d) flags separate source geometry volumes that overlap without documented fit permission. "
        "Many are coarse allocation proxies, so (d) is a HOLD, not a claim of impossible real hardware.",
        "",
        "| Category | Hits |",
        "|---|---:|",
    ]
    for cat in "abcd":table.append(f"| ({cat}) | {counts[cat]} |")
    table.extend(["| TOTAL | 409 |","","## All (d) entries","","| Source hit # | Part A | Part B | m3 | Classification reason |","|---:|---|---|---:|---|"])
    for x in out["conflicts_d"]:
        table.append(f"| {x['original_hit']} | {x['a']} | {x['b']} | {x['m3']:.8f} | {x['why']} |")
    table.extend([
        "",
        "Pair volumes must NOT be summed as distinct lost tank volume: dry fuel proxy, S1 fluids "
        "and CORE_FULL analytical cells repeatedly show the same spatial intrusion.",
        "",
        f"COURIER/SERVICE ARM: {courier['m3']:.8f}m3, identical sectors, distinct masses "
        f"{byid['courier_systems']['mass_t']:.6f}t and {byid['service_arm']['mass_t']:.6f}t. "
        "This is class (d), not duplicate S1/CORE_FULL data.",
        "",
        "G8 ZERO MARGIN: forward axial, aft axial, slot edge, open door edge; each exactly 0.50m "
        "against 0.50m threshold. The docked shuttle/bay G8 pass proves no tolerance.",
        "",
        f"HOT FINS / UPSTREAM FINDING #6: {len(fins)} fins, source folded panel radial span 2m, "
        f"deployed {fin['pleats']} x {fin['pleat_m']}m = {deployed}m; "
        f"{area:.0f}m2 two-sided emissive face area, {panels_t:.3f}t panels and "
        f"{roots_t:.3f}t root/hot-loop allowance (total {panels_t+roots_t:.3f}t). "
        "Source geometry intentionally renders folded-only; no deployed B-rep installed-fit screen.",
        "",
        "FROZEN #152/#153/#155, upstream canon/main unchanged; credit zero."
    ])
    (args.out/"REAL_CONFLICTS.md").write_text("\n".join(table)+"\n")
    print("TRIAGE_RESULT",dict(counts),"TOTAL",len(records),
          "D",len(out["conflicts_d"]),"COURIER",courier["m3"],
          "ZERO_G8",len(zero),"DEPLOYED_FIN_M",deployed,flush=True)

if __name__=="__main__":main()
