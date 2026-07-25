"""Cosmological reckoning: span-valued epochs and parameter-set variants.

Deep-time on Earth (:mod:`chronologia.periods`, :func:`chronologia.eras.resolve_bp`)
already places million- and billion-year dates on the Before-Present axis with
their uncertainty carried as span *width*.  Cosmology pushes two things past
what that machinery assumed, and this module adds exactly those two mechanisms:

1. **Span-valued era epochs** (:class:`UncertainEra`).  Every earthly epoch is a
   fixed instant; the Big Bang is not.  Its position — 13.787 ± 0.020 Gyr
   before present (Planck 2018) — is *itself* an interval, so an era counted
   from it must propagate the epoch's own uncertainty into every date it
   resolves.  :func:`resolve_cosmic` does this by **interval arithmetic**: the
   epoch's ±20 Myr and the value's significant-figure width simply **add**
   (Section "combination rule" below).

2. **Cosmology parameter-set variants** (:class:`CosmologyParams`).  Converting
   a redshift to a lookback time is not a single computation — it depends on the
   Hubble constant, which two careful measurements disagree about (the *Hubble
   tension*): Planck's CMB value 67.4 and the SH0ES local distance-ladder value
   73.04 km/s/Mpc.  Rather than pick a winner, the library **ships both as named
   variants** and makes :func:`lookback_time` take a ``cosmology=`` argument, so
   the disagreement is expressed by calling it twice.

Sources (downloaded, cited; see ``papers/standards/INDEX.md``):

* ``planck2018_parameters_arxiv_1807.06209.html`` — Planck 2018 (arXiv:1807.06209):
  H0 = 67.4 ± 0.5 km/s/Mpc, Ωm = 0.315 ± 0.007 (flat ⇒ ΩΛ = 0.685).
* ``age_of_the_universe_wikipedia.html`` — the Planck 2018 age 13.787 ± 0.020 Gyr.
* ``shoes_riess2022_arxiv_2112.04510.html`` — Riess et al. 2022 (SH0ES):
  H0 = 73.04 ± 1.04 km/s/Mpc, a 5σ tension with Planck.
* ``recombination_cosmology_wikipedia.html`` — recombination at ~380,000 yr.
* ``chronology_of_the_universe_wikipedia.html`` — Planck-epoch and reionization
  boundary times.

The lookback integral is flat-ΛCDM only and neglects radiation; that limit is
stated where it bites (the z→∞ gold, below).  Sagan's Cosmic Calendar is a
*presentation* affine map and lives in ``docs/mars-and-beyond.md`` as a runnable
example, not in this core.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Union

from chronologia.astrodate import AstroDate, DateSpan
from chronologia.eras import (EraCounting, HEAT_DEATH_YEAR, _BP_UNITS,
                              _astrodate_years_before_present)
from chronologia.periods import NamedPeriod

__all__ = [
    "UNIVERSE_AGE_GYR",
    "UNIVERSE_AGE_UNCERTAINTY_GYR",
    "UncertainEra",
    "AGE_OF_UNIVERSE_ERA",
    "resolve_cosmic",
    "CosmologyParams",
    "COSMOLOGIES",
    "lookback_gyr",
    "lookback_time",
    "age_of_universe_gyr",
    "COSMIC_PERIODS",
    "HUBBLE_TIME_GYR",
    "HEAT_DEATH_YEAR",
]

# The heat death of the universe — the physics-imposed upper bound on a
# meaningful date — is defined at the date-resolution chokepoint in
# :mod:`chronologia.eras` (where the warning fires) and re-exported here so it
# sits alongside the other cosmological constants.  ~10^100 years after the Big
# Bang, the Dark-Era evaporation of the largest supermassive black holes (Adams
# & Laughlin 1997, Rev. Mod. Phys. 69, 337).  Imported above; listed in
# ``__all__`` so ``from chronologia.cosmology import HEAT_DEATH_YEAR`` works.

# --------------------------------------------------------------------------
# The age of the universe as a span-valued epoch (Planck 2018)
# --------------------------------------------------------------------------

#: Age of the universe, Planck 2018 base-ΛCDM: **13.787 Gyr**
#: (``age_of_the_universe_wikipedia.html``; Planck 2018 Table 2).
UNIVERSE_AGE_GYR = Decimal("13.787")

#: 1σ uncertainty on the age: **±0.020 Gyr** (20 Myr), same source.  This is the
#: epoch-position interval that :func:`resolve_cosmic` propagates into every
#: cosmic date.
UNIVERSE_AGE_UNCERTAINTY_GYR = Decimal("0.020")

_GYR = Decimal(1_000_000_000)
#: Age in years and its ± half-width in years, on the Before-Present axis.
_UNIVERSE_AGE_YEARS = UNIVERSE_AGE_GYR * _GYR
_UNIVERSE_AGE_UNC_YEARS = UNIVERSE_AGE_UNCERTAINTY_GYR * _GYR


@dataclass(frozen=True)
class UncertainEra:
    """An era whose **epoch is a span**, not a fixed instant.

    The age-of-universe era counts forward from the Big Bang, but the Big Bang's
    position is only known to ±20 Myr, so the epoch is a :class:`DateSpan`
    (:attr:`epoch_span`) rather than an :class:`AstroDate`.  Resolving a value
    in the era therefore yields a span whose width already contains the epoch's
    own uncertainty — see :func:`resolve_cosmic`.

    :param key: registry key (``"age_of_universe"``).
    :param epoch_span: the epoch's position as a span (Big Bang ± 20 Myr, on the
        Before-Present axis, ``basis="reconstructed"``).
    :param counting: how values count within the era
        (:data:`~chronologia.eras.EraCounting.YEARS_SINCE` — "N years since the
        Big Bang").
    """
    key: str
    epoch_span: DateSpan
    counting: str = EraCounting.YEARS_SINCE


#: The Big Bang's position on the Before-Present axis, as a span: 13.787 Gyr
#: before AD 1950, ± 20 Myr folded outward into the two endpoints.  Older edge
#: (start) is ``age + unc`` years before present, younger edge ``age - unc``.
BIG_BANG_EPOCH_SPAN = DateSpan(
    _astrodate_years_before_present(_UNIVERSE_AGE_YEARS + _UNIVERSE_AGE_UNC_YEARS),
    _astrodate_years_before_present(_UNIVERSE_AGE_YEARS - _UNIVERSE_AGE_UNC_YEARS),
    basis="reconstructed")

#: The age-of-universe era: forward count from the (span-valued) Big Bang epoch.
AGE_OF_UNIVERSE_ERA = UncertainEra(
    "age_of_universe", BIG_BANG_EPOCH_SPAN, EraCounting.YEARS_SINCE)


def resolve_cosmic(years_since_big_bang: Union[int, float, str, Decimal],
                   unit: str = "a") -> DateSpan:
    """Resolve "N years since the Big Bang" into a Before-Present :class:`DateSpan`.

    ``unit`` is one of ``a``/``ka``/``Ma``/``Ga`` (10⁰/10³/10⁶/10⁹ years),
    reusing the scaled-BP units.  Pass ``years_since_big_bang`` as a **string**
    or :class:`~decimal.Decimal` when precision matters — ``"1"`` and ``"1.0"``
    Ga denote different precisions but the floats do not (the same rule
    :func:`~chronologia.eras.resolve_bp` documents).  ``basis`` is
    ``"reconstructed"``.

    **Combination rule (interval, not statistical).** The result's half-width is

        half = (epoch ± uncertainty)  +  (value significant-figure bin)/2

    the two uncertainties **added**, not combined in quadrature.  Justification:
    these are *interval bounds*, not independent random errors — the epoch's
    ±20 Myr is a stated confidence interval on a single fixed (if unknown)
    number, and the value's sig-fig bin is the range its written precision
    admits.  Quadrature would claim a statistical independence we do not have
    and would *shrink* the guaranteed-containment interval; addition keeps the
    span a true bound (Allen-interval endpoints, the stance the whole package
    takes toward width).

    Example: ``resolve_cosmic("380", "ka")`` (recombination) is centred 13.787
    Gyr − 380 kyr before present, with a half-width of 20 Myr + 0.5 kyr.
    """
    if unit not in _BP_UNITS:
        raise ValueError(f"unknown cosmic unit {unit!r}; expected one of "
                         f"{sorted(_BP_UNITS)}")
    dval = Decimal(str(years_since_big_bang))
    mult = _BP_UNITS[unit]
    since_years = dval * mult
    value_bin = Decimal(1).scaleb(int(dval.as_tuple().exponent)) * mult
    half = _UNIVERSE_AGE_UNC_YEARS + value_bin / 2      # uncertainties ADD
    center_bp = _UNIVERSE_AGE_YEARS - since_years        # years before present
    start = _astrodate_years_before_present(center_bp + half)   # older edge
    end = _astrodate_years_before_present(center_bp - half)     # younger edge
    return DateSpan(start, end, basis="reconstructed")


# --------------------------------------------------------------------------
# Cosmology parameter-set variants and the lookback-time integral
# --------------------------------------------------------------------------

#: Kilometres in a megaparsec (IAU 2015 astronomical constants): the unit
#: conversion that turns H0 [km/s/Mpc] into an inverse time.
_MPC_KM = 3.0856775814913673e19
#: Seconds in a gigayear (Julian year of 365.25 days): 10⁹ · 365.25 · 86400.
_GYR_SECONDS = 365.25 * 86400.0 * 1e9


@dataclass(frozen=True)
class CosmologyParams:
    """A named flat-ΛCDM parameter set.

    Two ship (:data:`COSMOLOGIES`): the early-universe CMB fit (``planck2018``)
    and the late-universe local distance-ladder measurement (``shoes2022``).
    They differ chiefly in :attr:`H0` — the Hubble tension — which is exactly why
    they are *named variants* a caller selects, not a single hard-coded cosmology.

    :param key: registry key.
    :param H0: Hubble constant, km/s/Mpc.
    :param Omega_m: present matter density parameter Ωm.
    :param Omega_lambda: dark-energy density parameter ΩΛ (flat ⇒ Ωm+ΩΛ ≈ 1).
    :param citation: the downloaded source backing the numbers.
    """
    key: str
    H0: float
    Omega_m: float
    Omega_lambda: float
    citation: str

    def hubble_time_gyr(self) -> float:
        """The Hubble time 1/H0 expressed in gigayears."""
        return _MPC_KM / self.H0 / _GYR_SECONDS


#: The parameter-set registry.  ``planck2018`` is the Planck CMB fit;
#: ``shoes2022`` is the SH0ES local measurement — which constrains H0 only, so
#: it borrows the flat-ΛCDM concordance Ωm/ΩΛ and differs *purely* in H0,
#: isolating the Hubble tension as the one axis of disagreement.
COSMOLOGIES: Dict[str, CosmologyParams] = {
    "planck2018": CosmologyParams(
        "planck2018", 67.4, 0.315, 0.685,
        "Planck 2018 (arXiv:1807.06209); "
        "papers/standards/planck2018_parameters_arxiv_1807.06209.html"),
    "shoes2022": CosmologyParams(
        "shoes2022", 73.04, 0.315, 0.685,
        "Riess et al. 2022 SH0ES (arXiv:2112.04510), H0 only; Ωm/ΩΛ from the "
        "flat-ΛCDM concordance; "
        "papers/standards/shoes_riess2022_arxiv_2112.04510.html"),
}

#: The Hubble time (Gyr) of the default cosmology, exposed for docs/examples.
HUBBLE_TIME_GYR = COSMOLOGIES["planck2018"].hubble_time_gyr()


def _E(z: float, Om: float, Ol: float) -> float:
    """The dimensionless Hubble parameter E(z)=H(z)/H0 for flat ΛCDM."""
    return math.sqrt(Om * (1.0 + z) ** 3 + Ol)


def _simpson_lookback_integral(z: float, Om: float, Ol: float, n: int) -> float:
    """Composite-Simpson estimate of ∫₀^z dz'/((1+z')E(z')) with ``n`` panels.

    Integrated in the substitution u = ln(1+z) (du = dz/(1+z)), so the integrand
    becomes the smooth, bounded 1/E(z(u)) over ``[0, ln(1+z)]`` — this keeps the
    quadrature well-conditioned even to z = 1000 (a linear-z grid would need
    absurd resolution near z=0).  ``n`` must be even.
    """
    u_max = math.log1p(z)
    h = u_max / n
    total = 0.0
    for i in range(n + 1):
        u = i * h
        zz = math.expm1(u)                 # e^u - 1
        f = 1.0 / _E(zz, Om, Ol)
        if i == 0 or i == n:
            total += f
        elif i % 2:
            total += 4.0 * f
        else:
            total += 2.0 * f
    return total * h / 3.0


#: Convergence tolerance for the adaptive lookback quadrature, in Gyr.
_INTEGRAL_TOL_GYR = 1e-6


def _get_cosmology(cosmology: Union[str, CosmologyParams]) -> CosmologyParams:
    if isinstance(cosmology, CosmologyParams):
        return cosmology
    if cosmology not in COSMOLOGIES:
        raise ValueError(f"unknown cosmology {cosmology!r}; expected one of "
                         f"{sorted(COSMOLOGIES)}")
    return COSMOLOGIES[cosmology]


def lookback_gyr(z: float, cosmology: Union[str, CosmologyParams] = "planck2018"
                 ) -> float:
    """Lookback time to redshift ``z``, in gigayears (flat ΛCDM).

    ``t_L(z) = (1/H0) ∫₀^z dz'/((1+z') E(z'))`` with
    ``E(z)=√(Ωm(1+z)³+ΩΛ)``, evaluated by adaptive composite Simpson (panels
    doubled until the estimate moves < :data:`_INTEGRAL_TOL_GYR`).  Radiation is
    neglected, so at very high z the model over-counts the early universe (see
    the z→∞ note on :func:`lookback_time`).

    :raises ValueError: ``z`` is negative, or ``cosmology`` is unknown.
    """
    if z < 0:
        raise ValueError(f"redshift z must be >= 0, got {z}")
    cosmo = _get_cosmology(cosmology)
    if z == 0:
        return 0.0
    tH = cosmo.hubble_time_gyr()
    n = 256
    prev = tH * _simpson_lookback_integral(z, cosmo.Omega_m, cosmo.Omega_lambda, n)
    while n < 1 << 22:
        n *= 2
        cur = tH * _simpson_lookback_integral(
            z, cosmo.Omega_m, cosmo.Omega_lambda, n)
        if abs(cur - prev) < _INTEGRAL_TOL_GYR:
            return cur
        prev = cur
    return prev


def age_of_universe_gyr(cosmology: Union[str, CosmologyParams] = "planck2018"
                        ) -> float:
    """Closed-form flat-ΛCDM age of the universe, in Gyr.

    ``t0 = (1/H0)·(2/(3√ΩΛ))·asinh(√(ΩΛ/Ωm))`` — the analytic matter+Λ age, the
    z→∞ limit the :func:`lookback_gyr` integral converges to.  For ``planck2018``
    this gives ~13.80 Gyr, agreeing with the cited 13.787 Gyr to well within the
    ±0.020 Gyr uncertainty (the small excess is the neglected-radiation and
    rounded-parameter residual).
    """
    cosmo = _get_cosmology(cosmology)
    tH = cosmo.hubble_time_gyr()
    return tH * (2.0 / (3.0 * math.sqrt(cosmo.Omega_lambda))) \
        * math.asinh(math.sqrt(cosmo.Omega_lambda / cosmo.Omega_m))


#: Documented model-uncertainty floor (Gyr) on a lookback span: 50 Myr,
#: standing for the flat-ΛCDM modelling error (neglected radiation, parameter
#: rounding) that no amount of z precision removes.
MODEL_UNCERTAINTY_FLOOR_GYR = 0.05


def lookback_time(z: Union[int, float, str, Decimal],
                  cosmology: Union[str, CosmologyParams] = "planck2018"
                  ) -> DateSpan:
    """Lookback time to redshift ``z`` as a Before-Present :class:`DateSpan`.

    "Looking at the sky is looking at the past": the light from redshift ``z``
    was emitted :func:`lookback_gyr` years ago, so the span is placed that many
    years before present (AD 1950), ``basis="reconstructed"``.

    **Width** reflects (a) the significant-figure precision of ``z`` propagated
    through the local sensitivity ``dt/dz = t_H · 1/((1+z)E(z))``, plus (b) a
    documented model-uncertainty floor (:data:`MODEL_UNCERTAINTY_FLOOR_GYR`,
    50 Myr) — the two added (interval arithmetic, as in :func:`resolve_cosmic`).
    Cross-*variant* divergence is **not** folded into the width; it is shown by
    calling with a different ``cosmology=`` (Planck vs SH0ES differ by ~0.6 Gyr
    at z=1).  Pass ``z`` as a string to control its precision.

    **z→∞ limit (the physics).** As z grows the span approaches the model's own
    age (:func:`age_of_universe_gyr`, ~13.80 Gyr for Planck), *not* exactly the
    cited 13.787 Gyr: this integral neglects radiation, so its time from the Big
    Bang to recombination (z≈1000) is ~0.54 Myr rather than the true ~380 kyr,
    leaving the z=1000 lookback ~0.5 Myr short of the model age and ~9 Myr above
    the Planck age — both inside the ±20 Myr epoch uncertainty.

    :raises ValueError: ``z`` is negative, or ``cosmology`` is unknown.
    """
    dz = Decimal(str(z))
    zf = float(dz)
    cosmo = _get_cosmology(cosmology)
    lb = lookback_gyr(zf, cosmo)
    # sensitivity dt/dz [Gyr per unit z] at this z (0 at z=0)
    dt_dz = cosmo.hubble_time_gyr() / ((1.0 + zf) * _E(zf, cosmo.Omega_m,
                                                       cosmo.Omega_lambda))
    z_bin = float(Decimal(1).scaleb(int(dz.as_tuple().exponent)))
    half_gyr = MODEL_UNCERTAINTY_FLOOR_GYR + dt_dz * z_bin / 2.0  # add
    center_bp = Decimal(str(lb)) * _GYR
    half_years = Decimal(str(half_gyr)) * _GYR
    start = _astrodate_years_before_present(center_bp + half_years)  # older
    end = _astrodate_years_before_present(center_bp - half_years)    # younger
    return DateSpan(start, end, basis="reconstructed")


# --------------------------------------------------------------------------
# Named cosmological periods on the Before-Present axis
# --------------------------------------------------------------------------
_COSMO_SOURCE = ("Wikipedia cosmology chronology "
                 "(papers/standards/chronology_of_the_universe_wikipedia.html, "
                 "recombination_cosmology_wikipedia.html)")


def _cosmic_period(key: str, name: str, since_start, since_end,
                   unit: str, source: str) -> NamedPeriod:
    """A named period spanning ``[since_start, since_end]`` years-since-Big-Bang.

    Placed on the Before-Present axis via the age-of-universe epoch;
    ``basis="reconstructed"``.  Endpoints are the era boundaries only — the
    epoch's ±20 Myr is not folded in here (that is :func:`resolve_cosmic`'s job
    for a *value*; a named period reports its cited boundary ages).
    """
    mult = _BP_UNITS[unit]
    bp_start = _UNIVERSE_AGE_YEARS - Decimal(str(since_start)) * mult  # older
    bp_end = _UNIVERSE_AGE_YEARS - Decimal(str(since_end)) * mult      # younger
    span = DateSpan(_astrodate_years_before_present(bp_start),
                    _astrodate_years_before_present(bp_end),
                    basis="reconstructed")
    return NamedPeriod(key, name, span, level="cosmic", region=None,
                       source=source, parent=None)


#: Named cosmological periods with citable, representable boundaries, on the
#: Before-Present axis.  **Skipped** (no non-degenerate citable span):
#:
#: * ``planck_epoch`` — its end boundary, the Planck time ~10⁻⁴³ s after the Big
#:   Bang, is ~50 orders of magnitude below the microsecond floor of the axis
#:   (and below the ±20 Myr epoch uncertainty), so it cannot be given a
#:   non-degenerate span here; only its *name* and boundary would survive, not a
#:   span.
#: * ``inflation`` — its start/end times are model-dependent and not established
#:   as fixed, citable boundaries, so it is deliberately not asserted.
COSMIC_PERIODS: Dict[str, NamedPeriod] = {
    # The first 380,000 years, ending at recombination / photon decoupling.
    "recombination": _cosmic_period(
        "recombination", "Recombination era", 0, 380, "ka",
        "Wikipedia, 'Recombination (cosmology)' "
        "(papers/standards/recombination_cosmology_wikipedia.html): "
        "t_rec ~= 380,000 yr after the Big Bang"),
    # Reionization: ~150 Myr to 1 Gyr after the Big Bang.
    "reionization": _cosmic_period(
        "reionization", "Reionization era", 150, 1000, "Ma", _COSMO_SOURCE),
}
