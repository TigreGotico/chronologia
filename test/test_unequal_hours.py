"""Unequal (temporal / seasonal) hours and clock-count conventions.

The proportional-hour spans and clock-count instants are derived directly from
:mod:`chronologia.solar`, so the gold values here are *hand-derived from the
same sunrise/sunset outputs* the code consumes: a temporal hour is a plain
fraction of the daylight (or night) span, and a clock-count instant is an
equal-hour offset from a solar anchor.  Rome (41.9 N, 12.5 E) is the running
example -- a Roman daytime hour runs ~76 min at the June solstice and shrinks
to ~46 min at the December solstice.

Citations (see the ``citations`` / ``citation`` fields of each system):
Pliny NH VII.212-215 and Vitruvius IX.7 (Roman temporal hours); Shulchan
Aruch OC 233/261 with Mishnah Berurah 233:4 (zmanim GRA); Frumer, *Making
Time* (Edo Japanese toki); Dohrn-van Rossum, *History of the Hour* (Italian
hours); Neugebauer, *HAMA* (Babylonian hours).
"""
from datetime import timedelta

import pytest

from chronologia.astrodate import AstroDate, DateSpan
from chronologia.solar import NoSunEvent, sun_events
from chronologia.unequal_hours import (
    BABYLONIAN_HOURS, CLOCK_CONVENTIONS, EDO_JAPANESE, ITALIAN_HOURS,
    ROMAN_HOURS, UNEQUAL_HOUR_SYSTEMS, ZMANIM_GRA, ClockConvention,
    UnequalHourSystem, convention_time, temporal_hour_span)

ROME = (41.9, 12.5)
JUNE = AstroDate(2024, 6, 21)
DEC = AstroDate(2024, 12, 21)
EQUINOX = AstroDate(2024, 3, 20)
SVALBARD = (78.0, 15.0)


def _minutes(td):
    return td.total_seconds() / 60.0


# --------------------------------------------------------------------------
# Summer-vs-winter divergence of the Roman hour at Rome's latitude.
# --------------------------------------------------------------------------

def test_june_roman_day_hour_is_about_75_minutes():
    span = temporal_hour_span(JUNE, *ROME, 1, ROMAN_HOURS)
    assert _minutes(span.width) == pytest.approx(76.0, abs=1.5)


def test_december_roman_day_hour_is_about_45_minutes():
    span = temporal_hour_span(DEC, *ROME, 1, ROMAN_HOURS)
    assert _minutes(span.width) == pytest.approx(45.6, abs=1.5)


def test_summer_day_hour_is_markedly_longer_than_winter():
    summer = temporal_hour_span(JUNE, *ROME, 1, ROMAN_HOURS)
    winter = temporal_hour_span(DEC, *ROME, 1, ROMAN_HOURS)
    assert summer.width > winter.width + timedelta(minutes=25)


def test_day_hour_equals_daylight_over_twelve():
    ev = sun_events(JUNE, *ROME)
    expected = (ev.sunset - ev.sunrise) / 12
    span = temporal_hour_span(JUNE, *ROME, 1, ROMAN_HOURS)
    assert _minutes(span.width) == pytest.approx(_minutes(expected), abs=0.02)


def test_summer_night_hour_is_shorter_than_summer_day_hour():
    day = temporal_hour_span(JUNE, *ROME, 1, ROMAN_HOURS)
    night = temporal_hour_span(JUNE, *ROME, 13, ROMAN_HOURS)
    assert night.width < day.width


def test_night_hour_equals_night_span_over_twelve():
    ev = sun_events(JUNE, *ROME)
    nxt = sun_events(JUNE + timedelta(days=1), *ROME)
    expected = (nxt.sunrise - ev.sunset) / 12
    span = temporal_hour_span(JUNE, *ROME, 13, ROMAN_HOURS)
    assert _minutes(span.width) == pytest.approx(_minutes(expected), abs=0.02)


def test_equinox_day_hour_is_near_sixty_minutes():
    span = temporal_hour_span(EQUINOX, *ROME, 1, ROMAN_HOURS)
    assert _minutes(span.width) == pytest.approx(60.0, abs=2.0)


def test_equinox_day_and_night_hours_nearly_equal():
    day = temporal_hour_span(EQUINOX, *ROME, 1, ROMAN_HOURS)
    night = temporal_hour_span(EQUINOX, *ROME, 13, ROMAN_HOURS)
    assert abs(_minutes(day.width) - _minutes(night.width)) < 3.0


# --------------------------------------------------------------------------
# Tiling: the day-hours exactly cover sunrise->sunset, night sunset->sunrise.
# --------------------------------------------------------------------------

def test_first_day_hour_starts_at_sunrise():
    ev = sun_events(JUNE, *ROME)
    span = temporal_hour_span(JUNE, *ROME, 1, ROMAN_HOURS)
    assert span.start == ev.sunrise


def test_twelve_day_hours_end_exactly_at_sunset():
    ev = sun_events(JUNE, *ROME)
    span = temporal_hour_span(JUNE, *ROME, 12, ROMAN_HOURS)
    assert span.end == ev.sunset


def test_day_hours_tile_with_no_gap():
    spans = [temporal_hour_span(JUNE, *ROME, h, ROMAN_HOURS)
             for h in range(1, 13)]
    assert all(spans[i].end == spans[i + 1].start for i in range(11))


def test_first_night_hour_starts_at_sunset():
    ev = sun_events(JUNE, *ROME)
    span = temporal_hour_span(JUNE, *ROME, 13, ROMAN_HOURS)
    assert span.start == ev.sunset


def test_last_night_hour_ends_at_next_sunrise():
    nxt = sun_events(JUNE + timedelta(days=1), *ROME)
    span = temporal_hour_span(JUNE, *ROME, 24, ROMAN_HOURS)
    assert span.end == nxt.sunrise


def test_night_hours_tile_with_no_gap():
    spans = [temporal_hour_span(JUNE, *ROME, h, ROMAN_HOURS)
             for h in range(13, 25)]
    assert all(spans[i].end == spans[i + 1].start for i in range(11))


def test_edo_six_day_hours_cover_daylight():
    ev = sun_events(JUNE, *ROME)
    first = temporal_hour_span(JUNE, *ROME, 1, EDO_JAPANESE)
    sixth = temporal_hour_span(JUNE, *ROME, 6, EDO_JAPANESE)
    assert first.start == ev.sunrise and sixth.end == ev.sunset


def test_edo_day_hour_is_twice_a_roman_day_hour():
    edo = temporal_hour_span(JUNE, *ROME, 1, EDO_JAPANESE)
    roman = temporal_hour_span(JUNE, *ROME, 1, ROMAN_HOURS)
    assert _minutes(edo.width) == pytest.approx(2 * _minutes(roman.width),
                                                abs=0.1)


# --------------------------------------------------------------------------
# zmanim GRA: sha'ot zmaniyot derived from sunrise/sunset arithmetic.
# --------------------------------------------------------------------------

def test_zmanim_gra_matches_roman_geometry():
    # GRA and the Roman system share sunrise->sunset / 12 geometry; only the
    # naming differs, so an hour-length must agree.
    gra = temporal_hour_span(JUNE, *ROME, 1, ZMANIM_GRA)
    roman = temporal_hour_span(JUNE, *ROME, 1, ROMAN_HOURS)
    assert gra.width == roman.width


def test_zmanim_gra_jerusalem_midday_is_sixth_hours_end():
    # Chatzot (halachic midday) ends the 6th sha'ah zmanit; by the GRA it is
    # the midpoint of sunrise..sunset.  Derived from sun_events for Jerusalem.
    jlat, jlon = 31.78, 35.22
    ev = sun_events(JUNE, jlat, jlon)
    midday = ev.sunrise + (ev.sunset - ev.sunrise) / 2
    sixth = temporal_hour_span(JUNE, jlat, jlon, 6, ZMANIM_GRA)
    assert abs((sixth.end - midday).total_seconds()) < 1.0


def test_zmanim_gra_is_tabulated_basis():
    span = temporal_hour_span(JUNE, *ROME, 3, ZMANIM_GRA)
    assert span.basis == "tabulated"


# --------------------------------------------------------------------------
# Clock-count conventions.
# --------------------------------------------------------------------------

def test_italian_hour_24_is_sunset_itself():
    ev = sun_events(JUNE, *ROME)
    assert convention_time(JUNE, *ROME, 24, ITALIAN_HOURS) == ev.sunset


def test_italian_hour_0_is_also_sunset():
    ev = sun_events(JUNE, *ROME)
    assert convention_time(JUNE, *ROME, 0, ITALIAN_HOURS) == ev.sunset


def test_italian_hour_1_is_one_equal_hour_after_sunset():
    ev = sun_events(JUNE, *ROME)
    assert convention_time(JUNE, *ROME, 1, ITALIAN_HOURS) == \
        ev.sunset + timedelta(hours=1)


def test_italian_hours_are_equal_length():
    a = convention_time(JUNE, *ROME, 5, ITALIAN_HOURS)
    b = convention_time(JUNE, *ROME, 6, ITALIAN_HOURS)
    assert b - a == timedelta(hours=1)


def test_babylonian_hour_0_is_sunrise():
    ev = sun_events(JUNE, *ROME)
    assert convention_time(JUNE, *ROME, 0, BABYLONIAN_HOURS) == ev.sunrise


def test_babylonian_hour_12_is_twelve_hours_after_sunrise():
    ev = sun_events(JUNE, *ROME)
    assert convention_time(JUNE, *ROME, 12, BABYLONIAN_HOURS) == \
        ev.sunrise + timedelta(hours=12)


def test_babylonian_hour_24_wraps_back_to_sunrise():
    ev = sun_events(JUNE, *ROME)
    assert convention_time(JUNE, *ROME, 24, BABYLONIAN_HOURS) == ev.sunrise


def test_clock_convention_returns_astrodate():
    assert isinstance(convention_time(JUNE, *ROME, 3, ITALIAN_HOURS),
                      AstroDate)


# --------------------------------------------------------------------------
# Polar pass-through: typed NoSunEvent, never raised, never faked.
# --------------------------------------------------------------------------

def test_polar_day_temporal_hour_passes_through_nosunevent():
    result = temporal_hour_span(JUNE, *SVALBARD, 1, ROMAN_HOURS)
    assert isinstance(result, NoSunEvent) and result.kind == "polar_day"


def test_polar_night_temporal_hour_passes_through_nosunevent():
    result = temporal_hour_span(DEC, *SVALBARD, 1, ROMAN_HOURS)
    assert isinstance(result, NoSunEvent) and result.kind == "polar_night"


def test_polar_night_temporal_hour_uses_needed_anchor():
    # A night hour needs sunset and the *next* sunrise; in polar night both are
    # absent, so a NoSunEvent still comes back rather than an exception.
    result = temporal_hour_span(DEC, *SVALBARD, 13, ROMAN_HOURS)
    assert isinstance(result, NoSunEvent)


def test_polar_day_convention_time_passes_through():
    result = convention_time(JUNE, *SVALBARD, 5, ITALIAN_HOURS)
    assert isinstance(result, NoSunEvent) and result.kind == "polar_day"


def test_polar_night_convention_time_passes_through():
    result = convention_time(DEC, *SVALBARD, 5, BABYLONIAN_HOURS)
    assert isinstance(result, NoSunEvent) and result.kind == "polar_night"


# --------------------------------------------------------------------------
# Adversarial: out-of-range hours, bad keys, malformed systems.
# --------------------------------------------------------------------------

def test_temporal_hour_zero_rejected():
    with pytest.raises(ValueError):
        temporal_hour_span(JUNE, *ROME, 0, ROMAN_HOURS)


def test_temporal_hour_above_total_rejected():
    with pytest.raises(ValueError):
        temporal_hour_span(JUNE, *ROME, 25, ROMAN_HOURS)


def test_edo_hour_13_rejected():
    with pytest.raises(ValueError):
        temporal_hour_span(JUNE, *ROME, 13, EDO_JAPANESE)


def test_convention_hour_above_count_rejected():
    with pytest.raises(ValueError):
        convention_time(JUNE, *ROME, 25, ITALIAN_HOURS)


def test_convention_negative_hour_rejected():
    with pytest.raises(ValueError):
        convention_time(JUNE, *ROME, -1, ITALIAN_HOURS)


def test_bad_day_anchor_rejected_at_construction():
    with pytest.raises(ValueError):
        UnequalHourSystem("bad", 12, 12, "nautical_dawn")


def test_zero_day_hours_rejected():
    with pytest.raises(ValueError):
        UnequalHourSystem("bad", 0, 12, "sunrise")


def test_bad_anchor_event_rejected():
    with pytest.raises(ValueError):
        ClockConvention("bad", "moonrise", 1, 24)


def test_bad_direction_rejected():
    with pytest.raises(ValueError):
        ClockConvention("bad", "sunset", 2, 24)


def test_bad_count_rejected():
    with pytest.raises(ValueError):
        ClockConvention("bad", "sunset", 1, 0)


def test_latitude_out_of_range_rejected():
    with pytest.raises(ValueError):
        temporal_hour_span(JUNE, 100.0, 12.5, 1, ROMAN_HOURS)


# --------------------------------------------------------------------------
# Registries and system metadata.
# --------------------------------------------------------------------------

def test_registries_expose_shipped_systems():
    assert set(UNEQUAL_HOUR_SYSTEMS) == {"roman", "zmanim_gra", "edo_japanese"}
    assert set(CLOCK_CONVENTIONS) == {"italian_hours", "babylonian_hours"}


def test_magen_avraham_is_not_shipped():
    # Deliberately omitted: its 16.1/8.5-degree anchors are not solar.py's
    # twilights (see the module docstring).
    assert "zmanim_magen_avraham" not in UNEQUAL_HOUR_SYSTEMS


def test_every_system_carries_citations():
    for system in UNEQUAL_HOUR_SYSTEMS.values():
        assert system.citations
    for conv in CLOCK_CONVENTIONS.values():
        assert conv.citation


def test_systems_are_frozen_hashable():
    assert hash(ROMAN_HOURS) and hash(ITALIAN_HOURS)


def test_total_hours_property():
    assert ROMAN_HOURS.total_hours == 24
    assert EDO_JAPANESE.total_hours == 12


def test_temporal_hour_returns_datespan_off_polar():
    assert isinstance(temporal_hour_span(JUNE, *ROME, 4, ROMAN_HOURS),
                      DateSpan)
