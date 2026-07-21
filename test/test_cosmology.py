"""Cosmological reckoning: span-valued epochs and parameter-set variants."""
from decimal import Decimal

import pytest

from chronologia.astrodate import AstroDate, DateSpan
from chronologia.cosmology import (AGE_OF_UNIVERSE_ERA, BIG_BANG_EPOCH_SPAN,
                                   COSMIC_PERIODS, COSMOLOGIES,
                                   MODEL_UNCERTAINTY_FLOOR_GYR,
                                   UNIVERSE_AGE_GYR,
                                   UNIVERSE_AGE_UNCERTAINTY_GYR, CosmologyParams,
                                   UncertainEra, age_of_universe_gyr,
                                   lookback_gyr, lookback_time, resolve_cosmic)
from chronologia.eras import EraCounting


def _span_center_bp_years(span: DateSpan) -> float:
    """Mean years-before-present of a span's two endpoints (present = 1950)."""
    return (1950 - span.start.year + 1950 - span.end.year) / 2.0


# --------------------------------------------------------------------------
# Constants and cited values
# --------------------------------------------------------------------------
def test_universe_age_cited_value():
    assert UNIVERSE_AGE_GYR == Decimal("13.787")
    assert UNIVERSE_AGE_UNCERTAINTY_GYR == Decimal("0.020")


def test_cosmologies_registered_with_cited_params():
    p = COSMOLOGIES["planck2018"]
    assert (p.H0, p.Omega_m, p.Omega_lambda) == (67.4, 0.315, 0.685)
    assert "1807.06209" in p.citation
    s = COSMOLOGIES["shoes2022"]
    assert s.H0 == 73.04
    assert "2112.04510" in s.citation


def test_flat_lcdm_density_sums_to_one():
    for cosmo in COSMOLOGIES.values():
        assert abs(cosmo.Omega_m + cosmo.Omega_lambda - 1.0) < 1e-9


def test_hubble_time_planck():
    # 1/H0 for 67.4 km/s/Mpc is ~14.5 Gyr
    assert abs(COSMOLOGIES["planck2018"].hubble_time_gyr() - 14.507) < 0.01


# --------------------------------------------------------------------------
# Span-valued epoch: UncertainEra + resolve_cosmic
# --------------------------------------------------------------------------
def test_age_of_universe_era_is_span_valued():
    assert isinstance(AGE_OF_UNIVERSE_ERA, UncertainEra)
    assert isinstance(AGE_OF_UNIVERSE_ERA.epoch_span, DateSpan)
    assert AGE_OF_UNIVERSE_ERA.counting == EraCounting.YEARS_SINCE


def test_big_bang_epoch_span_width_is_40_myr():
    # +/-20 Myr folded outward -> a 40 Myr wide epoch span
    width_years = (BIG_BANG_EPOCH_SPAN.end.year
                   - BIG_BANG_EPOCH_SPAN.start.year)
    assert width_years == 40_000_000
    assert BIG_BANG_EPOCH_SPAN.basis == "reconstructed"


def test_big_bang_epoch_centered_at_age():
    center = _span_center_bp_years(BIG_BANG_EPOCH_SPAN)
    assert abs(center - 13_787_000_000) < 1.0


def test_resolve_cosmic_returns_reconstructed_span():
    span = resolve_cosmic("380", "ka")
    assert isinstance(span, DateSpan)
    assert span.basis == "reconstructed"


def test_resolve_cosmic_center_is_age_minus_since():
    # recombination: 380 kyr after the Big Bang
    span = resolve_cosmic("380", "ka")
    center = _span_center_bp_years(span)
    assert abs(center - (13_787_000_000 - 380_000)) < 1.0


def test_resolve_cosmic_combines_uncertainties_by_addition():
    # half-width = epoch +/-20 Myr + (value sig-fig bin)/2.
    # "380 ka" has a 1-ka bin -> half = 20 Myr + 0.5 kyr = 20_000_500 yr
    span = resolve_cosmic("380", "ka")
    half = (1950 - span.start.year) - _span_center_bp_years(span)
    assert abs(half - 20_000_500) < 2.0


def test_resolve_cosmic_precision_widens_span():
    # a coarser value ("0.4 Ma" = 100-kyr bin) yields a wider span than
    # "380 ka" (1-kyr bin) though both name ~380 kyr
    coarse = resolve_cosmic("0.4", "Ma")
    fine = resolve_cosmic("380", "ka")
    coarse_w = coarse.end.year - coarse.start.year
    fine_w = fine.end.year - fine.start.year
    assert coarse_w > fine_w


def test_resolve_cosmic_epoch_uncertainty_dominates_precise_value():
    # even an exact value carries the +/-20 Myr epoch uncertainty
    span = resolve_cosmic("1", "a")
    half = (1950 - span.start.year) - _span_center_bp_years(span)
    assert abs(half - 20_000_000) < 2.0


def test_resolve_cosmic_string_precision_is_authoritative():
    # "1" Ga (1-Ga bin) is far wider than "1.000" Ga (1-Ma bin)
    coarse = resolve_cosmic("1", "Ga")
    fine = resolve_cosmic("1.000", "Ga")
    assert (coarse.end.year - coarse.start.year) \
        > (fine.end.year - fine.start.year)


def test_resolve_cosmic_rejects_unknown_unit():
    with pytest.raises(ValueError):
        resolve_cosmic("1", "parsec")


# --------------------------------------------------------------------------
# Lookback time: golds, variants, convergence
# --------------------------------------------------------------------------
def test_lookback_z1_planck_gold():
    # z=1 lookback ~ 7.9 Gyr (Planck 2018); our integral gives 7.951
    lb = lookback_gyr(1, "planck2018")
    assert abs(lb - 7.9) < 0.1
    assert abs(lb - 7.9506) < 1e-3   # tight, our stated integration accuracy


def test_lookback_z0_is_zero():
    assert lookback_gyr(0) == 0.0


def test_lookback_monotonic_in_z():
    prev = 0.0
    for z in (0.1, 0.5, 1, 2, 5, 10):
        cur = lookback_gyr(z)
        assert cur > prev
        prev = cur


def test_planck_and_shoes_differ_measurably_at_z1():
    planck = lookback_gyr(1, "planck2018")
    shoes = lookback_gyr(1, "shoes2022")
    assert planck > shoes                    # higher H0 -> shorter lookback
    assert abs(planck - shoes) > 0.5         # ~0.61 Gyr apart


def test_shoes_lookback_scales_roughly_as_inverse_h0():
    # lookback ~ 1/H0 at fixed Omega; ratio tracks the H0 ratio
    ratio = lookback_gyr(1, "shoes2022") / lookback_gyr(1, "planck2018")
    assert abs(ratio - 67.4 / 73.04) < 0.01


def test_analytic_age_matches_planck_within_uncertainty():
    age = age_of_universe_gyr("planck2018")
    # analytic matter+Lambda age ~13.796, agrees with 13.787 to <0.02 Gyr
    assert abs(age - float(UNIVERSE_AGE_GYR)) < 0.02


def test_lookback_z1000_approaches_model_age():
    # z->inf limit: lookback converges to the model's own age.
    lb = lookback_gyr(1000)
    age = age_of_universe_gyr("planck2018")
    # remainder (Big Bang -> z=1000) is ~0.54 Myr in this radiation-free model
    remainder = age - lb
    assert 0.0 < remainder < 0.001           # < 1 Myr
    assert abs(remainder - 0.00054) < 0.0002  # hand-derived ~540 kyr


def test_lookback_z1000_within_epoch_uncertainty_of_planck_age():
    # ~9 Myr above the cited 13.787 Gyr, inside the +/-20 Myr epoch band
    lb = lookback_gyr(1000)
    assert abs(lb - float(UNIVERSE_AGE_GYR)) < float(UNIVERSE_AGE_UNCERTAINTY_GYR)


def test_lookback_radiation_free_remainder_exceeds_true_380kyr():
    # the model's Big-Bang->z=1000 time (~540 kyr) is LARGER than the true
    # ~380 kyr because radiation is neglected -- the documented physics
    lb = lookback_gyr(1000)
    model_remainder_kyr = (age_of_universe_gyr("planck2018") - lb) * 1e6
    assert model_remainder_kyr > 380          # exceeds the true recombination time


def test_lookback_integral_converges():
    # the adaptive quadrature is stable: recomputing agrees to sub-tolerance
    a = lookback_gyr(3)
    b = lookback_gyr(3)
    assert a == b
    # and a high-z value is finite and below the age
    assert 0 < lookback_gyr(6) < age_of_universe_gyr()


def test_lookback_time_returns_bp_span():
    span = lookback_time("1")
    assert isinstance(span, DateSpan)
    assert span.basis == "reconstructed"
    center = _span_center_bp_years(span)
    assert abs(center / 1e9 - 7.9506) < 1e-3


def test_lookback_time_width_has_model_floor():
    # a z with a tiny sig-fig bin still carries the >=50 Myr model floor
    span = lookback_time("1.0000000")
    half_gyr = ((1950 - span.start.year) - _span_center_bp_years(span)) / 1e9
    assert half_gyr >= MODEL_UNCERTAINTY_FLOOR_GYR - 1e-6


def test_lookback_time_coarser_z_widens_span():
    coarse = lookback_time("1")        # +/-1 in z
    fine = lookback_time("1.00")       # +/-0.01 in z
    assert (coarse.end.year - coarse.start.year) \
        > (fine.end.year - fine.start.year)


def test_lookback_time_variant_centers_differ():
    planck = _span_center_bp_years(lookback_time("1", "planck2018"))
    shoes = _span_center_bp_years(lookback_time("1", "shoes2022"))
    assert abs(planck - shoes) / 1e9 > 0.5


def test_lookback_accepts_cosmologyparams_object():
    custom = CosmologyParams("x", 70.0, 0.3, 0.7, "test")
    lb = lookback_gyr(1, custom)
    assert lookback_gyr(1, "shoes2022") < lb < lookback_gyr(1, "planck2018")


# --------------------------------------------------------------------------
# Named cosmological periods
# --------------------------------------------------------------------------
def test_cosmic_periods_present_and_reconstructed():
    assert set(COSMIC_PERIODS) == {"recombination", "reionization"}
    for p in COSMIC_PERIODS.values():
        assert p.span.basis == "reconstructed"
        assert p.region is None
        assert p.level == "cosmic"


def test_recombination_span_first_380kyr():
    p = COSMIC_PERIODS["recombination"]
    # older edge at the Big Bang, younger edge 380 kyr later
    older = 1950 - p.span.start.year
    younger = 1950 - p.span.end.year
    assert abs(older - 13_787_000_000) < 1.0
    assert abs((older - younger) - 380_000) < 1.0


def test_reionization_span_150myr_to_1gyr():
    p = COSMIC_PERIODS["reionization"]
    older = 1950 - p.span.start.year
    younger = 1950 - p.span.end.year
    assert abs(older - (13_787_000_000 - 150_000_000)) < 1.0
    assert abs(younger - (13_787_000_000 - 1_000_000_000)) < 1.0


def test_reionization_is_younger_than_recombination():
    recomb_young = COSMIC_PERIODS["recombination"].span.end
    reion_old = COSMIC_PERIODS["reionization"].span.start
    assert recomb_young < reion_old   # reionization is later (nearer present)


def test_planck_epoch_and_inflation_are_not_registered():
    # skipped for lack of a non-degenerate citable span (documented)
    assert "planck_epoch" not in COSMIC_PERIODS
    assert "inflation" not in COSMIC_PERIODS


# --------------------------------------------------------------------------
# Adversarial
# --------------------------------------------------------------------------
def test_negative_redshift_rejected():
    with pytest.raises(ValueError):
        lookback_gyr(-1)
    with pytest.raises(ValueError):
        lookback_time("-0.5")


def test_unknown_cosmology_rejected():
    with pytest.raises(ValueError):
        lookback_gyr(1, "wmap")
    with pytest.raises(ValueError):
        lookback_time("1", "nonesuch")


def test_resolve_cosmic_after_present_gives_future_dates():
    # a value larger than the age of the universe lands after AD 1950
    span = resolve_cosmic("20", "Ga")   # 20 Gyr since Big Bang > 13.787
    assert span.start <= span.end        # still a valid span
    assert 1950 - span.end.year < 0      # younger edge is in the future


def test_lookback_time_span_endpoints_are_astrodate():
    span = lookback_time("2")
    assert isinstance(span.start, AstroDate)
    assert isinstance(span.end, AstroDate)
    assert span.start <= span.end
