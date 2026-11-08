#!/usr/bin/env python3
"""First stop-gate only: full 600-ray S5 storm shelter with measured crown aperture.
No mass, hull, or input source rewrites. New ceramic BReps represented by
their physical profiles, unlike the legacy no_render boxes.
"""
import copy, hashlib, json, math, random
from pathlib import Path
import build_v05 as B
import certify as C

ROOT=Path(__file__).resolve().parents[1]
GEO=ROOT/"results/out/wayfarer_v05_geometry.json"
OUT=ROOT/"results/out/crown_g6_aperture_screen.json"
SOURCE_SHA="88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1"
R=3.5
BASE=3.0431182268263375
SLOPE=math.tan(math.radians(50))
RIM_OUTER=BASE-(BASE+.42)*math.sqrt(1-(R/4.3)**2)
ORIG=B.shape_from_spec
MATERIAL_RHO_CERAMIC=3.75
CUT={"pressure_vessel":(11.356646021343266,9.864411164097419),
     "armor":(81.10303164040482,71.46047942794934)}
CROWN_VOLUME={"outer":1.2713465875234746,"inner":1.257582469558816,
              "panes":50.5041647147952*.01}
GEL_VOLUME=2.4886611982989955

class ShapeWrap(B.Shape):
    def __init__(self,spec):
        self.spec_=spec
        self.kind=spec["k"]
        if self.kind=="cut":
            self.base=ORIG(spec["base"])
        elif self.kind=="dome":
            self.base=B.DomeCyl(spec["apex"],BASE,BASE,4.3,.028)
    def contains(self,x,y,z):
        r=math.hypot(y,z)
        if self.kind=="cut":
            in_aperture=(r<3.5 and x<=BASE+.001)
            in_seat=(3.5<=r<=4.5 and RIM_OUTER<=x<=RIM_OUTER+.22)
            return self.base.contains(x,y,z) and not(in_aperture or in_seat)
        if self.kind=="dome":
            return r<=R and self.base.contains(x,y,z)
        if self.kind=="panes":
            if not r<=R:return False
            front=-1.2+max(0.,r-2.)*SLOPE
            return front<=x<=front+.01*(1+SLOPE*SLOPE)**.5
        raise ValueError(self.kind)
    def bbox(self):
        if self.kind=="cut":return self.base.bbox()
        if self.kind=="dome":return ((self.spec_["apex"], BASE),(-R,R),(-R,R))
        return ((-1.2,0.61),(-R,R),(-R,R))
    def volume(self):return self.spec_["volume"]
    def sample(self,rng,n):
        if self.kind=="cut":
            out=[]
            while len(out)<n:
                out += [v for v in self.base.sample(rng,n) if self.contains(*v)]
            return out[:n]
        return super().sample(rng,n)
def decode(spec):
    if spec["k"] in ("cut","dome","panes"):return ShapeWrap(spec)
    return ORIG(spec)
def part(pid,shape,volume,mass,mat="ceramic"):
    return dict(id=pid,shape=shape,volume_m3=volume,mass_t=mass,
                dry=True,tags=["from_reserve"],mat=mat,name=pid)

def main():
    assert hashlib.sha256(GEO.read_bytes()).hexdigest()==SOURCE_SHA
    G=json.loads(GEO.read_text())
    G["_sha"]=SOURCE_SHA
    I=json.loads((ROOT/"config/wayfarer_v05_inputs.json").read_text())
    crit=json.loads((ROOT/"config/cert_criteria.json").read_text())
    # Matched baseline measurement. Original source geometry/certificate untouched.
    old=C.g6(I,crit,G)
    N=copy.deepcopy(G)
    newparts=[]
    retired=[]
    removed=[]
    for p in N["parts"]:
        name=p["id"]
        if name in CUT:
            before,after=CUT[name]
            # The legacy sandbox analytic dome volume differs slightly from
            # the true 0.13.0 BRep, e.g. 80.823 vs 81.103 m3 armour.
            # kT explicitly makes BRep physical volume the mass authority.
            old_mass=p["mass_t"]
            p["shape"]={"k":"cut","base":p["shape"],"volume":after}
            p["volume_m3"]=after
            p["mass_t"]=old_mass*after/before
            removed.append(dict(id=name,old_t=old_mass,new_t=p["mass_t"],removed_t=old_mass-p["mass_t"]))
        if name in ("crown_dome","crown_backup_pressure_dome","crown_c_additional_strata_gore",
                    "crown_c_outward_retainers","crown_adaptive_optogel"):
            # These are unfitted bookkeeping boxes. No claimed attenuation.
            retired.append(name)
            continue
        newparts.append(p)
    crown=CROWN_VOLUME
    newparts.extend([
      part("crown_outer_pressure_dome",dict(k="dome",apex=-.42,volume=crown["outer"]),
           crown["outer"],crown["outer"]*MATERIAL_RHO_CERAMIC),
      part("crown_inner_pressure_dome",dict(k="dome",apex=-.30,volume=crown["inner"]),
           crown["inner"],crown["inner"]*MATERIAL_RHO_CERAMIC),
      part("crown_panes_37_conservative_no_seams",dict(k="panes",volume=crown["panes"]),
           crown["panes"],crown["panes"]*MATERIAL_RHO_CERAMIC),
    ])
    N["parts"]=newparts
    B.shape_from_spec=decode
    try: new=C.g6(I,crit,N)
    finally: B.shape_from_spec=ORIG
    threshold=crit["G6"]["shelter_min_g_cm2"]
    report=dict(source_sha=SOURCE_SHA,classification="G6_APERTURE_STOP_SCREEN",
      source_geometry_modified=False,
      g6_shelter_state=crit["G6"]["shelter_state"],
      rays_per_point=crit["G6"]["rays"],ray_step_m=crit["G6"]["ray_step_m"],
      old_shelter_min_g_cm2=old["shelter_min_g_cm2"],
      new_shelter_min_g_cm2=new["shelter_min_g_cm2"],
      delta_g_cm2=new["shelter_min_g_cm2"]-old["shelter_min_g_cm2"],
      required_min_g_cm2=threshold,
      storm_shelter_pass=new["shelter_min_g_cm2"]>=threshold,
      retired_unfitted_source_boxes=retired,material_debits=removed,
      physical_new_credited_g6_ceramic_mass_t=sum(q["mass_t"] for q in newparts if q["id"] in
           ("crown_outer_pressure_dome","crown_inner_pressure_dome","crown_panes_37_conservative_no_seams")),
      simplification="Pane seam gaps absent from this optimistic upper-bound crown G6 screen; will not justify qualification if threshold threatened.",
      result="PASS_FOR_SOURCE_BUILD_ONLY" if new["shelter_min_g_cm2"]>=threshold else "STOP_G6_FAIL",
    )
    OUT.write_text(json.dumps(report,indent=2)+"\n")
    print("CROWN_G6_APERTURE",json.dumps(report),flush=True)
    if not report["storm_shelter_pass"]:raise SystemExit(1)

if __name__=="__main__":main()
