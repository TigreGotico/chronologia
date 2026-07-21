"""Islamic prayer times over the solar hour-angle engine.

Gold values come from a downloadable published timetable: the AlAdhan prayer
times API (https://api.aladhan.com/v1/timings/15-02-2024, which implements the
PrayTimes methodology, https://praytimes.org/calculation), queried per city
with the matching method code and Asr school.  15 February 2024 is deliberately
outside Ramadan (so Umm al-Qura's 90-minute interval applies, not the 120) and
in northern-hemisphere winter (so none of the sampled cities observes DST and
the UTC offset is the constant standard offset).  Times are compared in local
civil time (our UTC result + the city's standard offset) within a three-minute
tolerance -- SOLAR_ACCURACY is +/-1 minute and both sides round to the minute.
"""
from datetime import date, datetime, timedelta

import pytest

from chronologia.astrodate import AstroDate
from chronologia.prayer_times import (ASR_METHODS, CONVENTIONS, AsrMethod,
                                      PrayerConvention, PrayerTimes,
                                      prayer_times)
from chronologia.solar import NoSunEvent, sun_events

DAY = AstroDate(2024, 2, 15)
TOLERANCE = timedelta(minutes=3)

# name, lat, lon(E+), convention, asr, utc_offset_hours, {field: "HH:MM" local}
GOLD = [
    ("cairo", 30.0444, 31.2357, "egyptian_gas", "standard", 2,
     {"fajr": "05:08", "sunrise": "06:36", "dhuhr": "12:09",
      "asr_time": "15:18", "maghrib": "17:43", "isha": "19:01"}),
    ("mecca", 21.4225, 39.8262, "umm_al_qura_makkah", "standard", 3,
     {"fajr": "05:35", "sunrise": "06:52", "dhuhr": "12:35",
      "asr_time": "15:51", "maghrib": "18:18", "isha": "19:48"}),
    ("karachi", 24.8607, 67.0011, "karachi", "standard", 5,
     {"fajr": "05:50", "sunrise": "07:07", "dhuhr": "12:46",
      "asr_time": "16:00", "maghrib": "18:26", "isha": "19:43"}),
    ("new_york", 40.7128, -74.0060, "isna", "standard", -5,
     {"fajr": "05:35", "sunrise": "06:51", "dhuhr": "12:10",
      "asr_time": "15:04", "maghrib": "17:30", "isha": "18:46"}),
    ("london", 51.5074, -0.1278, "mwl", "standard", 0,
     {"fajr": "05:23", "sunrise": "07:16", "dhuhr": "12:15",
      "asr_time": "14:43", "maghrib": "17:15", "isha": "19:01"}),
]


def _local(event, offset_hours):
    return event + timedelta(hours=offset_hours)


def _expected(day_utc, hhmm):
    h, m = (int(x) for x in hhmm.split(":"))
    return AstroDate(day_utc.year, day_utc.month, day_utc.day, h, m)


@pytest.mark.parametrize("name,lat,lon,conv,asr,off,fields", GOLD,
                         ids=[g[0] for g in GOLD])
def test_gold_timetable_within_tolerance(name, lat, lon, conv, asr, off, fields):
    """Every field of every gold city lands within three minutes."""
    pt = prayer_times(DAY, lat, lon, conv, asr)
    for field, hhmm in fields.items():
        got = _local(getattr(pt, field), off)
        want = _expected(pt.date, hhmm)
        delta = (got - want) if got >= want else (want - got)
        assert delta <= TOLERANCE, (
            f"{name}.{field}: {got.strftime('%H:%M')} vs gold {hhmm} "
            f"(delta {delta})")


def test_hanafi_asr_gold():
    """Cairo Hanafi Asr (factor 2) matches the published 16:05 within tolerance."""
    pt = prayer_times(DAY, 30.0444, 31.2357, "egyptian_gas", "hanafi")
    got = _local(pt.asr_time, 2)
    want = _expected(pt.date, "16:05")
    delta = (got - want) if got >= want else (want - got)
    assert delta <= TOLERANCE


# --- cross-convention and cross-school divergence -------------------------

def test_fajr_differs_across_conventions():
    """A shallower Fajr angle (ISNA 15) means a later Fajr than MWL 18."""
    mwl = prayer_times(DAY, 30.0444, 31.2357, "mwl").fajr
    isna = prayer_times(DAY, 30.0444, 31.2357, "isna").fajr
    assert isna > mwl
    assert abs(isna - mwl) >= timedelta(minutes=5)


def test_isha_differs_across_conventions():
    """Egyptian Isha (17.5) is not the same instant as MWL Isha (17)."""
    mwl = prayer_times(DAY, 30.0444, 31.2357, "mwl").isha
    egy = prayer_times(DAY, 30.0444, 31.2357, "egyptian_gas").isha
    assert egy != mwl
    assert egy > mwl  # deeper angle -> later


def test_asr_standard_earlier_than_hanafi():
    """Hanafi Asr (shadow factor 2) always falls after standard (factor 1)."""
    std = prayer_times(DAY, 30.0444, 31.2357, "egyptian_gas", "standard")
    han = prayer_times(DAY, 30.0444, 31.2357, "egyptian_gas", "hanafi")
    assert han.asr_time > std.asr_time
    assert abs(han.asr_time - std.asr_time) >= timedelta(minutes=20)


# --- Umm al-Qura fixed interval -------------------------------------------

def test_umm_al_qura_isha_is_maghrib_plus_90_exactly():
    """The Makkah convention fixes Isha at exactly Maghrib + 90 minutes."""
    pt = prayer_times(DAY, 21.4225, 39.8262, "umm_al_qura_makkah")
    assert pt.isha == pt.maghrib + timedelta(minutes=90)


def test_umm_al_qura_isha_ignores_depression_angle():
    """Its Isha depends only on Maghrib, not on how dark the sky gets."""
    makkah = prayer_times(DAY, 21.4225, 39.8262, "umm_al_qura_makkah")
    karachi = prayer_times(DAY, 21.4225, 39.8262, "karachi")
    assert makkah.isha == makkah.maghrib + timedelta(minutes=90)
    assert karachi.isha != karachi.maghrib + timedelta(minutes=90)


# --- ordering invariant ---------------------------------------------------

@pytest.mark.parametrize("lat,lon,conv", [
    (30.0444, 31.2357, "mwl"),
    (21.4225, 39.8262, "umm_al_qura_makkah"),
    (40.7128, -74.0060, "isna"),
    (24.8607, 67.0011, "karachi"),
    (-33.8688, 151.2093, "mwl"),   # Sydney, southern hemisphere
])
def test_ordering_invariant(lat, lon, conv):
    """fajr < sunrise < dhuhr < asr < maghrib < isha, everywhere defined."""
    pt = prayer_times(DAY, lat, lon, conv, "hanafi")
    order = [pt.fajr, pt.sunrise, pt.dhuhr, pt.asr_time, pt.maghrib, pt.isha]
    assert all(not isinstance(e, NoSunEvent) for e in order)
    assert order == sorted(order)
    assert all(a < b for a, b in zip(order, order[1:]))


# --- consistency with the underlying solar engine -------------------------

def test_dhuhr_is_solar_noon():
    """Dhuhr is the solar noon, unmodified (no precautionary margin added)."""
    pt = prayer_times(DAY, 30.0444, 31.2357, "mwl")
    assert pt.dhuhr == sun_events(DAY, 30.0444, 31.2357).solar_noon


def test_maghrib_is_sunset_and_sunrise_is_sunrise():
    """Maghrib and sunrise come straight from the solar engine."""
    ev = sun_events(DAY, 30.0444, 31.2357)
    pt = prayer_times(DAY, 30.0444, 31.2357, "mwl")
    assert pt.maghrib == ev.sunset
    assert pt.sunrise == ev.sunrise


def test_results_are_utc_astrodate():
    """Defined fields are AstroDate instants (UTC), like the solar engine."""
    pt = prayer_times(DAY, 30.0444, 31.2357, "mwl")
    for field in ("fajr", "sunrise", "dhuhr", "asr_time", "maghrib", "isha"):
        assert isinstance(getattr(pt, field), AstroDate)


# --- high-latitude honesty (white nights) ---------------------------------

def test_white_night_fajr_isha_undefined_angle_conventions():
    """At 60N midsummer the 18/17 depression is never reached: typed absence."""
    pt = prayer_times(AstroDate(2024, 6, 21), 60.0, 10.0, "mwl")
    assert isinstance(pt.fajr, NoSunEvent)
    assert isinstance(pt.isha, NoSunEvent)
    # sunrise/sunset/asr still occur that day
    assert isinstance(pt.sunrise, AstroDate)
    assert isinstance(pt.maghrib, AstroDate)
    assert isinstance(pt.asr_time, AstroDate)


def test_white_night_returns_no_estimation_rule():
    """We do not substitute a middle-of-night/one-seventh time: absence stays."""
    pt = prayer_times(AstroDate(2024, 6, 21), 65.0, 25.0, "isna")
    assert isinstance(pt.fajr, NoSunEvent)
    assert isinstance(pt.isha, NoSunEvent)


def test_white_night_umm_al_qura_isha_still_defined():
    """The fixed-interval Isha survives a white night: it needs only Maghrib."""
    pt = prayer_times(AstroDate(2024, 6, 21), 60.0, 10.0, "umm_al_qura_makkah")
    assert isinstance(pt.maghrib, AstroDate)
    assert pt.isha == pt.maghrib + timedelta(minutes=90)
    # but its Fajr, still angle-based, is undefined
    assert isinstance(pt.fajr, NoSunEvent)


def test_polar_night_all_undefined():
    """Near the pole in midwinter the sun never even reaches -18: all absent.

    (At 78N the sun still climbs to about -11 at local noon, so Fajr/Isha there
    are actually defined while sunrise is not -- the honest, field-by-field
    result.  At 88N it peaks near -21, below every line, so nothing is defined.)
    """
    pt = prayer_times(AstroDate(2024, 12, 21), 88.0, 15.0, "mwl")
    assert isinstance(pt.sunrise, NoSunEvent)
    assert isinstance(pt.maghrib, NoSunEvent)
    assert isinstance(pt.fajr, NoSunEvent)
    assert isinstance(pt.isha, NoSunEvent)


def test_polar_night_umm_al_qura_isha_absent_when_maghrib_absent():
    """The interval Isha propagates a missing Maghrib as a typed absence."""
    pt = prayer_times(AstroDate(2024, 12, 21), 78.0, 15.0, "umm_al_qura_makkah")
    assert isinstance(pt.maghrib, NoSunEvent)
    assert isinstance(pt.isha, NoSunEvent)


# --- adversarial / validation ---------------------------------------------

def test_unknown_convention_raises():
    with pytest.raises(ValueError, match="unknown convention"):
        prayer_times(DAY, 0.0, 0.0, "diyanet")


def test_unknown_asr_raises():
    with pytest.raises(ValueError, match="unknown asr"):
        prayer_times(DAY, 0.0, 0.0, "mwl", "shafii")


@pytest.mark.parametrize("lat,lon", [(91.0, 0.0), (-90.1, 0.0),
                                     (0.0, 181.0), (0.0, -180.1)])
def test_out_of_range_coordinates_raise(lat, lon):
    with pytest.raises(ValueError):
        prayer_times(DAY, lat, lon, "mwl")


def test_empty_and_case_sensitive_keys_rejected():
    with pytest.raises(ValueError):
        prayer_times(DAY, 0.0, 0.0, "")
    with pytest.raises(ValueError):
        prayer_times(DAY, 0.0, 0.0, "MWL")  # keys are lowercase


# --- input types and immutability -----------------------------------------

def test_accepts_date_and_datetime():
    """A date or datetime is accepted; only the calendar date is used."""
    ref = prayer_times(DAY, 30.0444, 31.2357, "mwl")
    assert prayer_times(date(2024, 2, 15), 30.0444, 31.2357, "mwl") == ref
    assert prayer_times(datetime(2024, 2, 15, 9, 30),
                        30.0444, 31.2357, "mwl") == ref


def test_prayer_times_is_frozen():
    pt = prayer_times(DAY, 30.0444, 31.2357, "mwl")
    with pytest.raises(Exception):
        pt.fajr = pt.dhuhr  # type: ignore[misc]


def test_records_convention_and_asr_used():
    pt = prayer_times(DAY, 30.0444, 31.2357, "karachi", "hanafi")
    assert pt.convention == "karachi"
    assert pt.asr == "hanafi"


# --- registry integrity ---------------------------------------------------

def test_all_five_conventions_shipped_with_citations():
    assert set(CONVENTIONS) == {
        "mwl", "isna", "egyptian_gas", "umm_al_qura_makkah", "karachi"}
    for conv in CONVENTIONS.values():
        assert isinstance(conv, PrayerConvention)
        assert conv.citation.strip()
        assert "praytimes.org" in conv.citation


def test_convention_angles_match_published_table():
    assert CONVENTIONS["mwl"].fajr_angle == 18.0
    assert CONVENTIONS["mwl"].isha.kind == "angle"
    assert CONVENTIONS["mwl"].isha.value == 17.0
    assert CONVENTIONS["egyptian_gas"].fajr_angle == 19.5
    assert CONVENTIONS["egyptian_gas"].isha.value == 17.5
    assert CONVENTIONS["umm_al_qura_makkah"].isha.kind == "interval"
    assert CONVENTIONS["umm_al_qura_makkah"].isha.value == 90.0
    assert CONVENTIONS["karachi"].fajr_angle == 18.0


def test_asr_methods_shipped_with_factors_and_citations():
    assert ASR_METHODS["standard"].shadow_factor == 1
    assert ASR_METHODS["hanafi"].shadow_factor == 2
    for m in ASR_METHODS.values():
        assert isinstance(m, AsrMethod)
        assert m.citation.strip()


def test_public_api_exports_prayer_times():
    import chronologia
    assert chronologia.prayer_times is prayer_times
    assert chronologia.CONVENTIONS is CONVENTIONS
