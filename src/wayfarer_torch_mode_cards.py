"""Exact Wayfarer E1 torch working-card inputs.

Engineering verification/requirements data only; not canon promotion or hardware certification.
Derived thrust and jet power MUST be calculated from mdot and ve rather than stored as
rounded independent truths.
"""
from fractions import Fraction

NORMAL_REMASS_KG = Fraction(250_000)
PROTECTED_WATER_KG = Fraction(50_000)

MODE_CARDS = {
    "ECON": (Fraction(11361004025, 10_000_000_000), Fraction(3_000_000)),
    "CRUISE": (Fraction(56805020125, 10_000_000_000), Fraction(2_000_000)),
    "EXPEDITE": (Fraction(2272200805, 100_000_000), Fraction(1_000_000)),
    "FAST": (Fraction(4869001725, 100_000_000), Fraction(700_000)),
    "HARD": (Fraction(2272200805, 18_000_000), Fraction(450_000)),
    "LIMIT": (Fraction(2272200805, 8_000_000), Fraction(300_000)),
}


def mode_outputs(mode):
    mdot, ve = MODE_CARDS[mode]
    thrust = mdot * ve
    jet_power = Fraction(1, 2) * mdot * ve * ve
    return mdot, ve, thrust, jet_power
