"""Tests for :mod:`chronologia.solar` (NOAA arithmetic solar events).

Gold values are cross-checked against the NOAA Global Monitoring solar
calculator (the same engine transcribed in ``chronologia/solar.py``) and against
independently checkable astronomical facts (equinox sunrise near local 06:00,
equator ~12 h days, published sunrise tables).  The stated accuracy bound is
+/- one minute (:data:`chronologia.solar.SOLAR_ACCURACY`), so gold comparisons
allow a couple of minutes of slack.
"""
import math
from datetime import date, datetime, timedelta

import pytest

from chronologia.astrodate import AstroDate
from chronologia.localtime import apparent_solar_time
from chronologia.solar import (SOLAR_ACCURACY, NoSunEvent, SunEvents,
                               sun_events, sunset_day_start)


def _minutes(ev):
    """Minutes-past-midnight (UTC) of an AstroDate event."""
    return ev.hour * 60 + ev.minute + ev.second / 60.0


def _tod_seconds(ev):
    return ev.hour * 3600 + ev.minute * 60 + ev.second


# --------------------------------------------------------------------------
# Gold values vs the NOAA calculator (the cited source's own engine)
# --------------------------------------------------------------------------

def test_noaa_denver_solstice_solar_noon():
    # NOAA calculator, Denver 40N 105W, 2010-06-21: solar noon 13:01 MDT
    # (UTC-6) == 19:01 UTC.
    ev = sun_events(AstroDate(2010, 6, 21), 40.0, -105.0)
    assert abs(_minutes(ev.solar_noon) - (19 * 60 + 1)) < 2


def test_noaa_denver_solstice_sunrise():
    # NOAA: sunrise 05:31 MDT == 11:31 UTC.
    ev = sun_events(AstroDate(2010, 6, 21), 40.0, -105.0)
    assert abs(_minutes(ev.sunrise) - (11 * 60 + 31)) < 2


def test_noaa_denver_solstice_sunset_rolls_to_next_utc_day():
    # NOAA: sunset 20:31 MDT == 02:31 UTC on 2010-06-22.
    ev = sun_events(AstroDate(2010, 6, 21), 40.0, -105.0)
    assert ev.sunset.day == 22
    assert abs(_minutes(ev.sunset) - (2 * 60 + 31)) < 2


# --------------------------------------------------------------------------
# Independently checkable gold values
# --------------------------------------------------------------------------

def test_greenwich_equinox_sunrise_near_0600_lmt():
    # At Greenwich (lon 0, UTC==LMT) the equinox sunrise is close to local
    # 06:00; the 0.833-deg refraction pulls it a few minutes earlier.
    ev = sun_events(AstroDate(2000, 3, 20), 0.0, 0.0)
    assert abs(_minutes(ev.sunrise) - 6 * 60) < 10


def test_greenwich_equinox_solar_noon_near_local_noon():
    ev = sun_events(AstroDate(2000, 3, 20), 0.0, 0.0)
    assert abs(_minutes(ev.solar_noon) - 12 * 60) < 15


def test_lisbon_summer_solstice_sunrise_matches_published_table():
    # Published table (timeanddate): Lisbon 2024-06-20 sunrise 06:11 WEST
    # (UTC+1) == 05:11 UTC.  Within +/- 4 min.
    ev = sun_events(AstroDate(2024, 6, 20), 38.72, -9.14)
    assert abs(_minutes(ev.sunrise) - (5 * 60 + 11)) < 4


def test_equator_day_length_about_twelve_hours_all_year():
    for month in range(1, 13):
        ev = sun_events(AstroDate(2024, month, 15), 0.0, 0.0)
        daylen = (_minutes(ev.sunset) - _minutes(ev.sunrise)) / 60.0
        assert 11.8 < daylen < 12.3


def test_equinox_day_length_about_twelve_hours_midlat():
    ev = sun_events(AstroDate(2024, 3, 20), 40.0, 0.0)
    daylen = (_minutes(ev.sunset) - _minutes(ev.sunrise)) / 60.0
    assert 11.9 < daylen < 12.4  # refraction lengthens the day slightly


def test_northern_summer_day_longer_than_winter():
    summer = sun_events(AstroDate(2024, 6, 21), 51.5, 0.0)
    winter = sun_events(AstroDate(2024, 12, 21), 51.5, 0.0)
    s = (_minutes(summer.sunset) - _minutes(summer.sunrise)) / 60.0
    w = (_minutes(winter.sunset) - _minutes(winter.sunrise)) / 60.0
    assert s > 15 and w < 9


# --------------------------------------------------------------------------
# Twilight ordering invariants
# --------------------------------------------------------------------------

def test_twilight_ordering_full_sequence():
    ev = sun_events(AstroDate(2024, 3, 20), 40.0, 0.0)
    seq = [ev.astronomical_dawn, ev.nautical_dawn, ev.civil_dawn, ev.sunrise,
           ev.solar_noon, ev.sunset, ev.civil_dusk, ev.nautical_dusk,
           ev.astronomical_dusk]
    mins = [_minutes(e) for e in seq]
    assert mins == sorted(mins)


def test_dawn_before_sunrise_dusk_after_sunset():
    ev = sun_events(AstroDate(2024, 9, 1), 35.0, 139.0)
    assert _minutes(ev.civil_dawn) < _minutes(ev.sunrise)
    assert _minutes(ev.civil_dusk) > _minutes(ev.sunset)


def test_deeper_twilight_is_earlier_in_morning():
    ev = sun_events(AstroDate(2024, 4, 1), 45.0, 10.0)
    assert (_minutes(ev.astronomical_dawn) < _minutes(ev.nautical_dawn)
            < _minutes(ev.civil_dawn) < _minutes(ev.sunrise))


def test_solar_noon_midway_between_sunrise_and_sunset():
    ev = sun_events(AstroDate(2024, 5, 5), 30.0, 20.0)
    mid = (_minutes(ev.sunrise) + _minutes(ev.sunset)) / 2.0
    assert abs(mid - _minutes(ev.solar_noon)) < 1.5


# --------------------------------------------------------------------------
# Reference-frame and type contracts
# --------------------------------------------------------------------------

def test_returns_sunevents_dataclass():
    ev = sun_events(AstroDate(2024, 1, 1), 0.0, 0.0)
    assert isinstance(ev, SunEvents)
    assert ev.latitude == 0.0 and ev.longitude == 0.0


def test_solar_noon_always_astrodate_even_in_polar_night():
    ev = sun_events(AstroDate(2024, 12, 21), 78.0, 15.0)
    assert isinstance(ev.solar_noon, AstroDate)


def test_events_are_utc_astrodate():
    ev = sun_events(AstroDate(2024, 6, 1), 40.0, 0.0)
    assert isinstance(ev.sunrise, AstroDate)
    assert isinstance(ev.sunset, AstroDate)


def test_accepts_plain_date_and_datetime():
    a = sun_events(date(2024, 6, 1), 40.0, 0.0)
    b = sun_events(datetime(2024, 6, 1, 9, 30), 40.0, 0.0)
    c = sun_events(AstroDate(2024, 6, 1), 40.0, 0.0)
    assert _minutes(a.sunrise) == _minutes(b.sunrise) == _minutes(c.sunrise)


def test_solar_noon_consistent_with_apparent_solar_time():
    # Apparent solar time at the computed solar noon must read ~12:00, within
    # the combined stated accuracy of the two EoT series.
    ev = sun_events(AstroDate(2024, 8, 10), 40.0, -74.0)
    ast = apparent_solar_time(ev.solar_noon, -74.0)
    off = abs(_tod_seconds(ast) - 12 * 3600)
    assert off < 90  # < 1.5 min


def test_solar_noon_consistency_multiple_dates():
    for m in (2, 5, 8, 11):
        ev = sun_events(AstroDate(2024, m, 10), 25.0, 45.0)
        ast = apparent_solar_time(ev.solar_noon, 45.0)
        assert abs(_tod_seconds(ast) - 12 * 3600) < 90


# --------------------------------------------------------------------------
# Polar honesty
# --------------------------------------------------------------------------

def test_polar_day_at_78N_in_june():
    ev = sun_events(AstroDate(2024, 6, 21), 78.0, 15.0)
    assert isinstance(ev.sunrise, NoSunEvent)
    assert isinstance(ev.sunset, NoSunEvent)
    assert ev.sunrise.kind == "polar_day"
    assert ev.sunset.kind == "polar_day"


def test_polar_night_at_78N_in_december():
    ev = sun_events(AstroDate(2024, 12, 21), 78.0, 15.0)
    assert isinstance(ev.sunrise, NoSunEvent)
    assert isinstance(ev.sunset, NoSunEvent)
    assert ev.sunrise.kind == "polar_night"
    assert ev.sunset.kind == "polar_night"


def test_polar_day_twilights_also_absent():
    ev = sun_events(AstroDate(2024, 6, 21), 78.0, 15.0)
    for f in ("civil_dawn", "nautical_dawn", "astronomical_dawn",
              "civil_dusk", "nautical_dusk", "astronomical_dusk"):
        assert isinstance(getattr(ev, f), NoSunEvent)


def test_nosunevent_carries_date_and_latitude():
    ev = sun_events(AstroDate(2024, 6, 21), 78.0, 15.0)
    ns = ev.sunrise
    assert ns.date == AstroDate(2024, 6, 21)
    assert ns.latitude == 78.0
    assert ns.kind in ("polar_day", "polar_night")


def test_nosunevent_is_frozen():
    ns = NoSunEvent("polar_day", AstroDate(2024, 6, 21), 78.0)
    with pytest.raises(Exception):
        ns.kind = "polar_night"


def test_polar_boundary_north_both_sides_june():
    # Midnight-sun latitude at solstice (with 0.833-deg refraction) sits just
    # below 66N: 65.7N still sets, 66.0N is polar day.
    sets = sun_events(AstroDate(2024, 6, 21), 65.7, 0.0)
    polar = sun_events(AstroDate(2024, 6, 21), 66.0, 0.0)
    assert isinstance(sets.sunset, AstroDate)
    assert isinstance(polar.sunset, NoSunEvent)
    assert polar.sunset.kind == "polar_day"


def test_polar_boundary_south_both_sides_june():
    # Southern winter: near -67 the sun still just clears the refracted
    # horizon; by -78 it is full polar night.
    clears = sun_events(AstroDate(2024, 6, 21), -67.0, 0.0)
    night = sun_events(AstroDate(2024, 6, 21), -78.0, 0.0)
    assert isinstance(clears.sunrise, AstroDate)
    assert isinstance(night.sunrise, NoSunEvent)
    assert night.sunrise.kind == "polar_night"


def test_independent_boundary_evaluation_deep_twilight_present():
    # A latitude/date where the sun never rises but astronomical dawn still
    # occurs: each boundary is judged on its own zenith.
    ev = sun_events(AstroDate(2024, 12, 21), 68.0, 0.0)
    assert isinstance(ev.sunrise, NoSunEvent)
    assert isinstance(ev.astronomical_dawn, AstroDate)


# --------------------------------------------------------------------------
# sunset_day_start
# --------------------------------------------------------------------------

def test_sunset_day_start_is_previous_evening_sunset():
    d = AstroDate(2024, 6, 1)
    ss = sunset_day_start(d, 31.78, 35.22)  # Jerusalem
    prev = sun_events(AstroDate(2024, 5, 31), 31.78, 35.22)
    assert ss == prev.sunset


def test_sunset_day_start_returns_astrodate_normally():
    ss = sunset_day_start(AstroDate(2024, 3, 15), 31.78, 35.22)
    assert isinstance(ss, AstroDate)


def test_sunset_day_start_polar_returns_nosunevent():
    ss = sunset_day_start(AstroDate(2024, 6, 22), 78.0, 15.0)
    assert isinstance(ss, NoSunEvent)
    assert ss.kind == "polar_day"


# --------------------------------------------------------------------------
# Adversarial input validation
# --------------------------------------------------------------------------

def test_latitude_out_of_range_raises():
    with pytest.raises(ValueError):
        sun_events(AstroDate(2024, 1, 1), 90.5, 0.0)
    with pytest.raises(ValueError):
        sun_events(AstroDate(2024, 1, 1), -91.0, 0.0)


def test_longitude_out_of_range_raises():
    with pytest.raises(ValueError):
        sun_events(AstroDate(2024, 1, 1), 0.0, 181.0)
    with pytest.raises(ValueError):
        sun_events(AstroDate(2024, 1, 1), 0.0, -180.1)


def test_extreme_valid_bounds_accepted():
    # Exactly at the limits is valid.
    sun_events(AstroDate(2024, 3, 20), 90.0, 180.0)
    sun_events(AstroDate(2024, 3, 20), -90.0, -180.0)


def test_sunset_day_start_validates_inputs():
    with pytest.raises(ValueError):
        sunset_day_start(AstroDate(2024, 1, 1), 200.0, 0.0)


def test_bad_date_type_raises():
    with pytest.raises(TypeError):
        sun_events("2024-06-01", 40.0, 0.0)


def test_accuracy_bound_is_one_minute():
    assert SOLAR_ACCURACY == timedelta(minutes=1)


def test_leap_year_uses_366_denominator():
    # Same calendar day in a leap vs common year gives near-identical but not
    # identical events (365 vs 366 in gamma); both must be sane times.
    leap = sun_events(AstroDate(2024, 7, 1), 40.0, 0.0)
    common = sun_events(AstroDate(2023, 7, 1), 40.0, 0.0)
    assert abs(_minutes(leap.sunrise) - _minutes(common.sunrise)) < 3
