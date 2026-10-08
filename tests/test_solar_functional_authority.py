from pathlib import Path

WEB = Path(__file__).resolve().parents[1] / "web" / "solar-basemap"
FORBIDDEN = (
    "solve_kepler",
    "osculating_orbit",
    "circular_local_fallback",
    "orbital_elements",
    "mean_anomaly",
    "semi_major_axis",
)


def test_progressive_basemap_has_no_independent_orbit_physics():
    """The browser may evaluate published state functions; it may not invent celestial motion."""
    text = "\n".join(path.read_text().lower() for path in WEB.glob("*.js"))
    assert not [term for term in FORBIDDEN if term in text]


def test_reference_curves_are_sampled_from_temporal_state_functions():
    temporal = (WEB / "temporal.js").read_text()
    assert "function referenceCurves" in temporal
    assert "const u=a+(b-a)*i/points,r=relative(o,u)" in temporal
    assert "setTemporalCurves(curves)" in temporal
