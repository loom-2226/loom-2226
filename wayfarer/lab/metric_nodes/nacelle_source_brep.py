"""Exact BRep for approved nacelle ring-lock receivers and eight 45-degree tail arms.

Keep the seven legacy shape constructors unmodified. The receiver void is cut
ONLY from the new nacelle, never the existing ship. D9 thresholds unchanged.
"""
from build123d import Axis, Solid
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"packing_phase1b"))
import source_brep_pilot as P


def make(s):
    kind=s["k"]
    if kind=="torus_arc":
        span=s["a1"]-s["a0"]
        assert abs(span-45.)<1e-9
        c=(s["x"],0,s["zc"])
        arc=Solid.make_torus(s["R"],s["r"],plane=P.plane_x(*c),
                             major_angle=span)
        return arc.rotate(Axis(c,(1,0,0)),s["a0"])
    if kind=="ring_notched_tube":
        outer=P.tube(s)
        receiver=Solid.make_torus(s["hR"],s["hr"],
                                  plane=P.plane_x(s["hx"],0,s["zc"]))
        result=outer-receiver
        if result is None or result.volume<=0:
            raise RuntimeError("invalid nacelle ring-lock receiver")
        return result
    return P.make(s)
