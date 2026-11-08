"""Read-only OpenCascade diagnosis of #471 protected-primary STEP integrity.

The user-approved fallback is applicable ONLY when ordinary AND fuzzy Boolean
intersections are numerically invalid (e.g. symmetric difference > V1+V2).
No geometry changes, no tuning, no tolerance weakening.
"""
import math

from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.ShapeFix import ShapeFix_Shape
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_SOLID, TopAbs_FORWARD, TopAbs_REVERSED, TopAbs_IN, TopAbs_ON
from OCP.BRepTools import BRepTools
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepClass import BRepClass_FaceClassifier
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.gp import gp_Pnt, gp_Pnt2d
from build123d import Compound

FUZZY_M = 1e-6
MIN_SURFACE_SAMPLES_EACH_WAY = 256
NUMERIC_VOLUME_MARGIN_M3 = 1e-7


def _signed_volume(shape):
    g = GProp_GProps()
    # OCC integrates oriented shells; negative values expose inverted solids.
    BRepGProp.VolumeProperties_s(shape.wrapped, g, True, False)
    return float(g.Mass())


def _orientation(shape, shape_type):
    e = TopExp_Explorer(shape.wrapped, shape_type)
    result = dict(forward=0, reversed=0, other=0)
    while e.More():
        o = e.Current().Orientation()
        key = "forward" if o == TopAbs_FORWARD else "reversed" if o == TopAbs_REVERSED else "other"
        result[key] += 1
        e.Next()
    return result


def _validity(shape):
    result = dict(
        brepcheck_valid=bool(BRepCheck_Analyzer(shape.wrapped).IsValid()),
        signed_volume_m3=_signed_volume(shape),
        face_orientation_counts=_orientation(shape, TopAbs_FACE),
        solid_orientation_counts=_orientation(shape, TopAbs_SOLID),
        is_valid_wrapper=bool(shape.is_valid),
    )
    if not result["brepcheck_valid"]:
        before = result["signed_volume_m3"]
        fix = ShapeFix_Shape(shape.wrapped)
        did = bool(fix.Perform())
        fixed = fix.Shape()
        g = GProp_GProps()
        BRepGProp.VolumeProperties_s(fixed, g, True, False)
        result["shapefix"] = dict(
            performed=did,
            valid_after=bool(BRepCheck_Analyzer(fixed).IsValid()),
            signed_volume_before_m3=before,
            signed_volume_after_m3=float(g.Mass()),
            signed_volume_change_m3=float(g.Mass())-before,
            face_count_after=_orientation_wrapped(fixed, TopAbs_FACE),
            solid_count_after=_orientation_wrapped(fixed, TopAbs_SOLID),
            used_to_mutate_or_replace_primary=False,
        )
    else:
        result["shapefix"] = dict(attempted=False, reason="BRepCheck valid")
    return result


def _orientation_wrapped(shape, shape_type):
    e=TopExp_Explorer(shape,shape_type)
    n=0
    while e.More():n+=1;e.Next()
    return n


def _fuzzy_common(a, b):
    op = BRepAlgoAPI_Common(a.wrapped,b.wrapped)
    op.SetFuzzyValue(FUZZY_M)
    op.Build()
    if not op.IsDone():
        return dict(fuzzy_value_m=FUZZY_M,is_done=False, error="BRepAlgoAPI_Common not done")
    result=op.Shape()
    g=GProp_GProps()
    if result.IsNull():
        return dict(fuzzy_value_m=FUZZY_M,is_done=True, common_volume_m3=0.)
    BRepGProp.VolumeProperties_s(result,g,True,False)
    return dict(fuzzy_value_m=FUZZY_M,is_done=True,
        common_volume_m3=float(g.Mass()),
        brepcheck_valid=bool(BRepCheck_Analyzer(result).IsValid()))


def _surface_sample_points(shape):
    """Deterministic UV interior and vertex samples on each actual trimmed face.

    Points are on BRep surfaces, never inside-volume samples. A grid on each
    face is filtered by the trimmed-face classifier; each counted sample is
    evaluated against the opposing collection of boundary faces.
    """
    faces=list(shape.faces())
    if not faces:
        raise RuntimeError("no BRep faces for surface comparison")
    target=max(4,math.ceil(MIN_SURFACE_SAMPLES_EACH_WAY/len(faces)))
    points={}
    face_counts=[]
    for face in faces:
        selected=[]
        # Every topological corner or endpoint is a surface sample.
        for v in face.vertices():
            x=v.center()
            selected.append(gp_Pnt(float(x.X),float(x.Y),float(x.Z)))
        u0,u1,v0,v1=BRepTools.UVBounds_s(face.wrapped)
        if not all(math.isfinite(t) for t in (u0,u1,v0,v1)):
            raise RuntimeError("unbounded or nonfinite UV face: cannot certify surface distance")
        adaptor=BRepAdaptor_Surface(face.wrapped)
        grid=max(8,math.ceil(math.sqrt(target*4)))
        for i in range(grid):
            if len(selected)>=target:break
            u=u0+(u1-u0)*(i+.5)/grid
            for j in range(grid):
                v=v0+(v1-v0)*(j+.5)/grid
                classifier=BRepClass_FaceClassifier(face.wrapped,gp_Pnt2d(u,v),1e-9)
                if classifier.State() not in (TopAbs_IN,TopAbs_ON):continue
                selected.append(adaptor.Value(u,v))
                if len(selected)>=target:break
        # Do not pretend to have sampled a trimmed face when only exterior
        # projected UV positions exist; vertices are valid boundary samples.
        if not selected:
            raise RuntimeError("face without valid surface sample")
        face_counts.append(len(selected))
        for p in selected:
            key=(round(p.X(),12),round(p.Y(),12),round(p.Z(),12))
            points.setdefault(key,p)
    if len(points)<MIN_SURFACE_SAMPLES_EACH_WAY:
        raise RuntimeError("insufficient distinct BRep surface samples: "+str(len(points)))
    return list(points.values()),len(faces),face_counts


def _directed_distance(a,b):
    samples,face_count,face_counts=_surface_sample_points(a)
    # Compound OF FACES avoids returning zero for an interior point inside
    # the opposite SOLID. Distance must go to its boundary, not its volume.
    target=Compound(children=list(b.faces()))
    maximum=-1.0
    worst=None
    for p in samples:
        v=BRepBuilderAPI_MakeVertex(p).Vertex()
        distance=BRepExtrema_DistShapeShape(v,target.wrapped)
        distance.Perform()
        if not distance.IsDone():
            raise RuntimeError("BRepExtrema distance failed")
        d=float(distance.Value())
        if not math.isfinite(d) or d<0:
            raise RuntimeError("invalid BRepExtrema distance "+str(d))
        if d>maximum:
            maximum=d
            worst=[float(p.X()),float(p.Y()),float(p.Z())]
    return dict(samples=len(samples),faces=face_count,
                min_samples_each_way=MIN_SURFACE_SAMPLES_EACH_WAY,
                face_sample_counts=face_counts,
                max_deviation_m=maximum,
                worst_sample_m=worst)


def audit(name, native, imported, volume_tolerance_m3, bbox_tolerance_m,
          symmetric_tolerance_m3, bounds):
    v1,v2=float(native.volume),float(imported.volume)
    delta=abs(v1-v2)
    bbox_delta=max(abs(x-y) for x,y in zip(bounds(native),bounds(imported)))
    result=dict(name=name,vol_native_m3=round(v1,8),
                vol_approved_m3=round(v2,8),
                volume_delta_m3=round(delta,9),
                bbox_delta_m=round(bbox_delta,9),
                diagnostics=dict(native=_validity(native), imported=_validity(imported)))
    # Run the native kernel common operation exactly as the original D9 did.
    try:
        common=native & imported
        commonv=0.0 if common is None else float(common.volume)
        sym=v1+v2-2*commonv
        result["raw_boolean"]=dict(common_volume_m3=commonv,
                                   symmetric_difference_m3=sym)
    except Exception as exc:
        commonv=None
        sym=None
        result["raw_boolean"]=dict(error=str(exc))
    # V1+V2 is the strict physical ceiling; additionally, COMMON must have
    # volume between zero and the smaller solid's volume.
    def numeric_invalid(cv, sv):
        return (cv is None or sv is None or not math.isfinite(cv) or
                not math.isfinite(sv) or
                cv < -NUMERIC_VOLUME_MARGIN_M3 or
                cv > min(v1,v2)+NUMERIC_VOLUME_MARGIN_M3 or
                sv > v1+v2+NUMERIC_VOLUME_MARGIN_M3 or
                sv < -NUMERIC_VOLUME_MARGIN_M3)
    invalid=numeric_invalid(commonv,sym)
    result["raw_boolean_numerically_invalid"]=invalid
    if invalid or sym>symmetric_tolerance_m3:
        try:
            fuzzy=_fuzzy_common(native,imported)
            if fuzzy.get("is_done"):
                fv=fuzzy["common_volume_m3"]
                fuzzy["symmetric_difference_m3"]=v1+v2-2*fv
                fuzzy["numerically_invalid"]=numeric_invalid(fv,fuzzy["symmetric_difference_m3"])
            result["fuzzy_boolean"]=fuzzy
        except Exception as exc:
            result["fuzzy_boolean"]=dict(fuzzy_value_m=FUZZY_M,error=str(exc),numerically_invalid=True)
    fuzzy=result.get("fuzzy_boolean",{})
    # If the ordinary kernel is valid, honour the ORIGINAL symdiff criterion.
    # Else accept a valid <=1e-6m fuzzy Boolean if it clears the same limit.
    ordinary_pass=not invalid and sym<=symmetric_tolerance_m3
    fuzzy_valid=fuzzy and not fuzzy.get("numerically_invalid",True) and "symmetric_difference_m3" in fuzzy
    fuzzy_pass=bool(invalid and fuzzy_valid and
                    fuzzy["symmetric_difference_m3"]<=symmetric_tolerance_m3)
    fallback_permitted=bool(invalid and not fuzzy_valid)
    if fallback_permitted:
        try:
            fwd=_directed_distance(native,imported)
            rev=_directed_distance(imported,native)
            result["surface_distance"]=dict(native_to_imported=fwd,
                     imported_to_native=rev, two_way_max_deviation_m=max(
                         fwd["max_deviation_m"],rev["max_deviation_m"]),
                     bounded_sample_not_global_hausdorff=True,
                     tolerance_m=bbox_tolerance_m,
                     pass_distance=(max(fwd["max_deviation_m"],rev["max_deviation_m"])<=bbox_tolerance_m))
        except Exception as exc:
            result["surface_distance"]=dict(error=str(exc),pass_distance=False)
    # A ShapeFix attempt is diagnostic only; no repaired primary silently
    # changes installed geometry or proof of source identity.
    valid_sides=all(result["diagnostics"][key]["brepcheck_valid"] for key in ("native","imported"))
    any_fix=any("valid_after" in result["diagnostics"][key]["shapefix"] for key in ("native","imported"))
    geometry_pass=(delta<=volume_tolerance_m3 and bbox_delta<=bbox_tolerance_m)
    surface_pass=bool(fallback_permitted and result.get("surface_distance",{}).get("pass_distance"))
    result["integrity_method"]=(
        "ordinary_symmetric_difference" if ordinary_pass else
        "OCCT_fuzzy_symmetric_difference" if fuzzy_pass else
        "two_way_BRep_surface_sample_distance" if surface_pass else "FAIL")
    result["pass"]=bool(geometry_pass and valid_sides and not any_fix and
                        (ordinary_pass or fuzzy_pass or surface_pass))
    result["fallback_authority_applied"]=surface_pass
    result["symmetric_difference_m3"]=round(sym,9) if sym is not None else None
    return result
