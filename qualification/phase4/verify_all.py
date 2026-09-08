from __future__ import annotations
import hashlib,json,platform,sqlite3,sys,unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
P3=HERE.parent/"phase3"
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(P3))

from minimal_3d import build_scene,scene_bounds,write_outputs
from shipclasses_resolver import compute_mass_properties

SCHEMA=P3/"LOOM_2226_SHIPCLASSES_PROTOTYPE_SCHEMA_v0.1.sql"
SEED=P3/"LOOM_2226_SHIPCLASSES_WAYFARER_SEED_v0.1.sql"
P3G=P3/"LOOM_2226_SHIPCLASSES_WAYFARER_GEOMETRY_COUPLING_v0.1.sql"
P4G=HERE/"LOOM_2226_SHIPCLASSES_WAYFARER_PHASE4_GEOMETRY_v0.1.sql"
OUT=HERE/"output"
RESULT=OUT/"phase4_verification_result.json"

REQ=[SCHEMA,SEED,P3G,P4G,HERE/"minimal_3d.py",HERE/"test_phase4_wayfarer_3d.py"]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def db():
    c=sqlite3.connect(":memory:"); c.row_factory=sqlite3.Row
    for p in (SCHEMA,SEED,P3G,P4G): c.executescript(p.read_text(encoding="utf-8"))
    return c

def run_tests():
    loader=unittest.TestLoader()
    suite=loader.discover(str(HERE),pattern="test_phase4_*.py")
    result=unittest.TestResult(); suite.run(result)
    return {
        "passed":result.wasSuccessful(),"tests_run":result.testsRun,
        "failures":[str(x[0]) for x in result.failures],
        "errors":[str(x[0]) for x in result.errors],
        "skipped":[str(x[0]) for x in result.skipped],
    }

def primitive(scene,pid):
    return next(p for p in scene["primitives"] if p["primitive_id"]==pid)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    checks={}; errors={}
    checks["required_files"]=all(p.exists() for p in REQ)
    tests=run_tests() if checks["required_files"] else {"passed":False,"tests_run":0,"failures":[],"errors":["missing files"],"skipped":[]}
    checks["unit_suite"]=tests["passed"]

    c=db()
    integ=c.execute("PRAGMA integrity_check").fetchone()[0]
    fk=c.execute("PRAGMA foreign_key_check").fetchall()
    checks["sqlite_integrity"]=integ=="ok"
    checks["foreign_keys"]=len(fk)==0

    state={"launch_state":"DOCKED","radiator_state":"STOWED"}
    mass=compute_mass_properties(c,state)
    outputs=write_outputs(c,OUT,state)
    scene=outputs["scene"]; bounds=scene["bounds"]

    checks["overall_length"]=abs(bounds["min_m"][0])<=1e-12 and abs(bounds["max_m"][0]-57.0)<=1e-12
    ref=primitive(scene,"p_reference_envelope")
    checks["main_body_reference"]=ref["dimensions"]=={"length_m":57.0,"diameter_m":9.0} and ref["authority_status"]=="CANON"
    checks["docked_mass_com"]=abs(mass["mass_kg"]-1158500.0)<=1e-6 and max(abs(a-b) for a,b in zip(mass["center_of_mass_B_m"],[26.676650841605525,0.0,0.14812257229175657]))<=1e-12

    roots=[p for p in scene["primitives"] if p["primitive_id"].startswith("p_radiator_root_")]
    checks["radiators_open"]=len(roots)==4 and all(p["authority_status"]=="OPEN" and "RENDER" not in p["physical_roles"] for p in roots)
    dock=primitive(scene,"p_docking_marker")
    checks["side_semantics"]=primitive(scene,"g_planetary_launch")["pose_B"]["translation_m"][2]>0 and dock["pose_B"]["translation_m"][2]<0 and dock["dimensions"]["side"]=="-Z"

    before_z=mass["center_of_mass_B_m"][2]
    c.execute("UPDATE component_transform SET tz_m=6.25 WHERE component_id='planetary_launch'")
    mass2=compute_mass_properties(c,state)
    scene2=build_scene(c,state)
    launch_z=primitive(scene2,"g_planetary_launch")["pose_B"]["translation_m"][2]
    expected_dz=33000.0*(6.25-5.2)/1158500.0
    actual_dz=mass2["center_of_mass_B_m"][2]-before_z
    checks["critical_same_source_coupling"]=abs(launch_z-6.25)<=1e-12 and abs(actual_dz-expected_dz)<=1e-12
    errors["coupled_com_delta_error_m"]=abs(actual_dz-expected_dz)

    status="PASS" if all(checks.values()) else "FAIL"
    payload={
        "schema":"loom.phase4_minimal3d_verification.v0.1",
        "status":status,
        "environment":{"python":platform.python_version(),"platform":platform.platform(),"machine":platform.machine(),"offline_required":True},
        "checks":checks,"errors":errors,"unit_suite":tests,
        "numerics":{"docked_wet_mass_kg":mass["mass_kg"],"docked_wet_com_B_m":mass["center_of_mass_B_m"],
                    "scene_bounds_m":bounds,"mutated_launch_z_m":launch_z,"mutated_com_delta_z_m":actual_dz},
        "artifacts":{"scene_sha256":outputs["scene_sha256"],"obj_sha256":outputs["obj_sha256"]},
        "input_sha256":{p.name:sha(p) for p in REQ if p.exists()},
        "sqlite":{"integrity_check":integ,"foreign_key_violations":[list(r) for r in fk]},
    }
    raw=(json.dumps(payload,sort_keys=True,indent=2)+"\n").encode()
    RESULT.write_bytes(raw)
    print("SHA256 phase4_verification_result.json",hashlib.sha256(raw).hexdigest())
    print("SHA256 wayfarer_minimal3d.json",outputs["scene_sha256"])
    print("SHA256 wayfarer_minimal3d.obj",outputs["obj_sha256"])
    print(json.dumps(payload,sort_keys=True,indent=2))
    print("LOOM_PHASE4_VERIFY:",status)
    return 0 if status=="PASS" else 1

if __name__=="__main__":
    raise SystemExit(main())
