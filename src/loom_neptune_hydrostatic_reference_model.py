from __future__ import annotations

from dataclasses import dataclass
import math


R_UNIVERSAL_J_MOL_K = 8.314462618
NEPTUNE_GM_M3_S2 = 6.836529e15
NEPTUNE_ONE_BAR_EQUATORIAL_RADIUS_M = 24_766_000.0
H2_MOLAR_MASS_KG_MOL = 2.01588e-3
HE_MOLAR_MASS_KG_MOL = 4.002602e-3


@dataclass(frozen=True)
class PressureEnvelope:
    minimum_pa: float
    maximum_pa: float
    observed_reference_pa: float | None
    minimum_relative_error: float | None
    maximum_relative_error: float | None
    authority: str = "HISTORICAL_REFERENCE_MODEL_ONLY"


@dataclass(frozen=True)
class DensityEnvelope:
    minimum: float
    maximum: float
    authority: str
    observed: bool
    qualified_for_2226_endpoint: bool


class NeptuneHydrostaticReferenceModel:
    """Bounded historical reference model for the 1-bar-to-tropopause layer.

    This is not a reconstruction of the Voyager reduced profile and is not a
    2226 endpoint model. Temperature is linearly interpolated between the two
    qualified historical anchors. Pressure follows hydrostatic ideal-gas
    balance using constant spherical gravity evaluated at the Voyager 1-bar
    equatorial radius. Composition uncertainty is represented by the published
    tropopause H2 number-fraction range 0.78..0.84, with the remainder treated
    as helium.
    """

    altitude_min_km = 0.0
    altitude_max_km = 40.0
    temperature_at_one_bar_k = 72.0
    temperature_at_tropopause_k = 52.0
    pressure_at_one_bar_pa = 100_000.0
    observed_tropopause_pressure_pa = 10_000.0
    h2_fraction_min = 0.78
    h2_fraction_max = 0.84
    source_epoch_class = "VOYAGER2_1989_HISTORICAL_REFERENCE"
    qualified_for_2226_endpoint = False
    admissibility_authority = "ZERO"
    loom_coherence_authority = "ZERO"
    interpolation_authority = "PHYSICAL_REFERENCE_MODEL_ONLY"
    extrapolation_authority = "ZERO"

    @property
    def reference_gravity_m_s2(self) -> float:
        return NEPTUNE_GM_M3_S2 / (NEPTUNE_ONE_BAR_EQUATORIAL_RADIUS_M ** 2)

    @staticmethod
    def _molar_mass(h2_fraction: float) -> float:
        return (
            h2_fraction * H2_MOLAR_MASS_KG_MOL
            + (1.0 - h2_fraction) * HE_MOLAR_MASS_KG_MOL
        )

    def _validate_altitude(self, altitude_km: float) -> float:
        altitude_km = float(altitude_km)
        if not math.isfinite(altitude_km):
            raise ValueError("altitude must be finite")
        if not self.altitude_min_km <= altitude_km <= self.altitude_max_km:
            raise ValueError("altitude outside qualified reference-model domain")
        return altitude_km

    def temperature_k(self, altitude_km: float) -> float:
        altitude_km = self._validate_altitude(altitude_km)
        f = altitude_km / self.altitude_max_km
        return self.temperature_at_one_bar_k + f * (
            self.temperature_at_tropopause_k - self.temperature_at_one_bar_k
        )

    def _pressure_for_fraction(self, altitude_km: float, h2_fraction: float) -> float:
        altitude_km = self._validate_altitude(altitude_km)
        if altitude_km == 0.0:
            return self.pressure_at_one_bar_pa

        z_m = altitude_km * 1000.0
        t0 = self.temperature_at_one_bar_k
        tz = self.temperature_k(altitude_km)
        lapse_k_per_m = (
            self.temperature_at_tropopause_k - self.temperature_at_one_bar_k
        ) / (self.altitude_max_km * 1000.0)
        integral_dz_over_t = math.log(tz / t0) / lapse_k_per_m
        molar_mass = self._molar_mass(h2_fraction)
        exponent = -(
            molar_mass
            * self.reference_gravity_m_s2
            / R_UNIVERSAL_J_MOL_K
        ) * integral_dz_over_t
        return self.pressure_at_one_bar_pa * math.exp(exponent)

    def pressure_envelope_pa(self, altitude_km: float) -> PressureEnvelope:
        altitude_km = self._validate_altitude(altitude_km)
        # More helium => larger mean molecular mass => lower pressure aloft.
        p_low = self._pressure_for_fraction(altitude_km, self.h2_fraction_min)
        p_high = self._pressure_for_fraction(altitude_km, self.h2_fraction_max)
        minimum_pa = min(p_low, p_high)
        maximum_pa = max(p_low, p_high)

        observed = None
        min_error = None
        max_error = None
        if altitude_km == self.altitude_max_km:
            observed = self.observed_tropopause_pressure_pa
            min_error = abs(minimum_pa - observed) / observed
            max_error = abs(maximum_pa - observed) / observed

        return PressureEnvelope(
            minimum_pa=minimum_pa,
            maximum_pa=maximum_pa,
            observed_reference_pa=observed,
            minimum_relative_error=min_error,
            maximum_relative_error=max_error,
        )

    def density_envelope_kg_m3(self, altitude_km: float) -> DensityEnvelope:
        altitude_km = self._validate_altitude(altitude_km)
        temperature = self.temperature_k(altitude_km)
        values = []
        for h2_fraction in (self.h2_fraction_min, self.h2_fraction_max):
            pressure = self._pressure_for_fraction(altitude_km, h2_fraction)
            molar_mass = self._molar_mass(h2_fraction)
            values.append(pressure * molar_mass / (R_UNIVERSAL_J_MOL_K * temperature))
        return DensityEnvelope(
            minimum=min(values),
            maximum=max(values),
            authority="HISTORICAL_REFERENCE_MODEL_ONLY",
            observed=False,
            qualified_for_2226_endpoint=False,
        )
