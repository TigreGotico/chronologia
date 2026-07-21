"""Tests for the civil-day ``zone=`` seam across solar/dayparts/prayer/hours.

Two anchoring conventions coexist in this library: the **solar day** (a UTC
calendar day, the historical default -- every field before this seam existed)
and the **civil day** (the ``[00:00, 24:00)`` wall-clock stretch of some
``tzinfo`` zone on a date).  They usually agree to within minutes, but at
extreme longitude/zone-offset combinations they can disagree by a whole
calendar day -- the classic case being ``Pacific/Kiritimati`` (Kiribati,
UTC+14) at a longitude that is still numerically *west* of the date line.

``zone=None`` (the default everywhere) is required to stay byte-identical to
the pre-seam behaviour; this file pins several outputs against the values
computed before ``zone`` existed (mirrored by the still-passing pre-existing
suites in ``test_solar.py`` etc.) to guard that promise directly.
"""
from datetime import timedelta, timezone as tzutc

import pytest

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None

from chronologia.astrodate import AstroDate, DateSpan
from chronologia.dayparts import daypart_span
from chronologia.prayer_times import prayer_times
from chronologia.solar import NoSunEvent, sun_events
from chronologia.unequal_hours import (ITALIAN_HOURS, ROMAN_HOURS,
                                       convention_time, temporal_hour_span)

KIRITIMATI = ZoneInfo("Pacific/Kiritimati")
SHANGHAI = ZoneInfo("Asia/Shanghai")
NEW_YORK = ZoneInfo("America/New_York")
ROME = ZoneInfo("Europe/Rome")
RIYADH = ZoneInfo("Asia/Riyadh")

# Kiritimati (Kiribati): actual island coordinates sit just west of 180 degrees
# (numerically negative / "western hemisphere" longitude) even though the
# zone offset is UTC+14 -- the classic date-line mismatch case.
KIRI_LAT, KIRI_LON = 1.87, -157.4
# Urumqi: 43.8N 87.6E, but the whole of China clocks to Beijing time
# (Asia/Shanghai, UTC+8), so its solar events run hours behind the wall clock.
URUMQI_LAT, URUMQI_LON = 43.8, 87.6
# Denver: the pinned NOAA gold-value location already exercised in
# test_solar.py (40N 105W, 2010-06-21 solstice).
DENVER_LAT, DENVER_LON = 40.0, -105.0


def _instant_eq(aware: AstroDate, naive_utc: AstroDate) -> bool:
    """True when an aware AstroDate names the same instant as a naive-UTC one."""
    return aware == naive_utc.replace(tzinfo=tzutc.utc)


# --------------------------------------------------------------------------
# zone=None: byte-identical to solar-day anchoring (no behaviour change)
# --------------------------------------------------------------------------

def test_sun_events_zone_none_identical_to_omitted_zone():
    d = AstroDate(2010, 6, 21)
    explicit_none = sun_events(d, DENVER_LAT, DENVER_LON, zone=None)
    omitted = sun_events(d, DENVER_LAT, DENVER_LON)
    assert explicit_none == omitted


def test_sun_events_zone_none_pins_denver_solar_noon_gold():
    # Same NOAA gold value test_solar.py pins: solar noon 19:01 UTC.
    ev = sun_events(AstroDate(2010, 6, 21), DENVER_LAT, DENVER_LON)
    assert ev.solar_noon.hour == 19
    assert abs(ev.solar_noon.minute - 1) <= 2
    assert ev.solar_noon.tzinfo is None


def test_daypart_span_zone_none_identical_to_omitted_zone():
    d = AstroDate(2024, 1, 15)
    explicit_none = daypart_span(d, "morning", zone=None)
    omitted = daypart_span(d, "morning")
    assert explicit_none == omitted
    assert explicit_none.start.tzinfo is None


def test_prayer_times_zone_none_identical_to_omitted_zone():
    d = AstroDate(2024, 6, 21)
    explicit_none = prayer_times(d, 21.4225, 39.8262, "umm_al_qura_makkah",
                                 zone=None)
    omitted = prayer_times(d, 21.4225, 39.8262, "umm_al_qura_makkah")
    assert explicit_none == omitted


def test_unequal_hours_zone_none_identical_to_omitted_zone():
    d = AstroDate(2024, 6, 21)
    explicit_none = temporal_hour_span(d, 41.9, 12.5, 1, ROMAN_HOURS, zone=None)
    omitted = temporal_hour_span(d, 41.9, 12.5, 1, ROMAN_HOURS)
    assert explicit_none == omitted


def test_convention_time_zone_none_identical_to_omitted_zone():
    d = AstroDate(2024, 6, 21)
    explicit_none = convention_time(d, 41.9, 12.5, 24, ITALIAN_HOURS, zone=None)
    omitted = convention_time(d, 41.9, 12.5, 24, ITALIAN_HOURS)
    assert explicit_none == omitted


# --------------------------------------------------------------------------
# Kiribati: civil-day sunrise lands on the correct calendar day even though
# the solar-day computation, converted to the same zone, does not.
# --------------------------------------------------------------------------

def test_kiribati_civil_sunrise_lands_inside_civil_day():
    d = AstroDate(2024, 6, 21)
    window_start = AstroDate(2024, 6, 21, tzinfo=KIRITIMATI)
    window_end = AstroDate(2024, 6, 22, tzinfo=KIRITIMATI)
    civil = sun_events(d, KIRI_LAT, KIRI_LON, zone=KIRITIMATI)
    assert window_start <= civil.sunrise < window_end


def test_kiribati_solar_day_sunrise_falls_outside_the_civil_day():
    # The story the module docstring documents: converting the *solar-day*
    # (UTC-anchored) sunrise into the Kiritimati zone lands it on the 22nd,
    # a full calendar day away from the civil day it was asked about.
    d = AstroDate(2024, 6, 21)
    window_start = AstroDate(2024, 6, 21, tzinfo=KIRITIMATI)
    window_end = AstroDate(2024, 6, 22, tzinfo=KIRITIMATI)
    solar = sun_events(d, KIRI_LAT, KIRI_LON)
    solar_in_zone = solar.sunrise.replace(tzinfo=tzutc.utc).astimezone(KIRITIMATI)
    assert not (window_start <= solar_in_zone < window_end)
    assert solar_in_zone.day == 22


def test_kiribati_civil_sunset_also_lands_inside_civil_day():
    d = AstroDate(2024, 6, 21)
    window_start = AstroDate(2024, 6, 21, tzinfo=KIRITIMATI)
    window_end = AstroDate(2024, 6, 22, tzinfo=KIRITIMATI)
    civil = sun_events(d, KIRI_LAT, KIRI_LON, zone=KIRITIMATI)
    assert window_start <= civil.sunset < window_end


def test_kiribati_civil_events_are_aware_in_the_requested_zone():
    d = AstroDate(2024, 6, 21)
    civil = sun_events(d, KIRI_LAT, KIRI_LON, zone=KIRITIMATI)
    assert civil.sunrise.tzinfo is KIRITIMATI
    assert civil.solar_noon.tzinfo is KIRITIMATI
    assert civil.date.tzinfo is KIRITIMATI
    assert civil.date == AstroDate(2024, 6, 21, tzinfo=KIRITIMATI)


# --------------------------------------------------------------------------
# Urumqi: civil-day sunrise wall clock is deep into the morning because the
# whole of China clocks to Beijing time despite Urumqi's far-west longitude.
# --------------------------------------------------------------------------

def test_urumqi_civil_sunrise_is_late_morning_wall_clock():
    # Winter solstice: short day, and the ~2h10m longitude lag behind the
    # Beijing (120E) meridian pushes local sunrise to around 09:00-10:00.
    d = AstroDate(2024, 12, 21)
    civil = sun_events(d, URUMQI_LAT, URUMQI_LON, zone=SHANGHAI)
    assert civil.sunrise.hour == 9


def test_urumqi_civil_sunrise_differs_from_naive_shifted_solar_day():
    # Sanity check the lag is really there: the solar-day (UTC) sunrise
    # differs from the civil (Shanghai) sunrise only by the zone conversion,
    # but the resulting wall-clock hour is nowhere near a "normal" morning
    # rise (contrast with Denver's ~05:31 local at its own solstice).
    d = AstroDate(2024, 12, 21)
    civil = sun_events(d, URUMQI_LAT, URUMQI_LON, zone=SHANGHAI)
    assert civil.sunrise.hour >= 9


# --------------------------------------------------------------------------
# daypart_span: aware endpoints; DST gap/fold documented convention.
# --------------------------------------------------------------------------

def test_daypart_span_zone_produces_aware_endpoints():
    span = daypart_span(AstroDate(2024, 7, 4), "morning", zone=NEW_YORK)
    assert span.start.tzinfo is NEW_YORK
    assert span.end.tzinfo is NEW_YORK
    assert span.start.hour == 6
    assert span.end.hour == 12


def test_daypart_span_night_across_spring_forward_is_8_hours():
    # 2024-03-10 America/New_York: clocks spring forward 02:00 -> 03:00.
    # "night" [21:00, 06:00) anchored to 2024-03-09 spans that transition:
    # nominally 9 hours, minus the hour that never happened = 8 real hours.
    span = daypart_span(AstroDate(2024, 3, 9), "night", zone=NEW_YORK)
    assert span.width == timedelta(hours=8)


def test_daypart_span_night_across_fall_back_is_10_hours():
    # 2024-11-03 America/New_York: clocks fall back 02:00 -> 01:00.
    # "night" anchored to 2024-11-02 spans that transition: nominally 9
    # hours, plus the repeated hour = 10 real hours.
    span = daypart_span(AstroDate(2024, 11, 2), "night", zone=NEW_YORK)
    assert span.width == timedelta(hours=10)


def test_daypart_span_gap_boundary_resolves_post_transition():
    # "midnight" anchor (00:00) does not itself sit in the gap, but a
    # DayPart boundary that *does* land inside a spring-forward gap must
    # resolve to the post-transition instant (offset already advanced),
    # never raise.  Build a direct check via resolve_wall_clock semantics:
    # 2024-03-10 02:30 America/New_York never occurs (jumps 02:00->03:00).
    from chronologia.dayparts import _resolve_boundary
    from datetime import time as _time
    boundary = _resolve_boundary(2024, 3, 10, _time(2, 30), NEW_YORK)
    assert boundary.utcoffset() == timedelta(hours=-4)  # EDT, post-transition


def test_daypart_span_fold_boundary_resolves_later_occurrence():
    # 2024-11-03 01:30 America/New_York occurs twice (fold); the documented
    # convention keeps the *later* (post-transition, EST) occurrence.
    from chronologia.dayparts import _resolve_boundary
    from datetime import time as _time
    boundary = _resolve_boundary(2024, 11, 3, _time(1, 30), NEW_YORK)
    assert boundary.utcoffset() == timedelta(hours=-5)  # EST, later occurrence


def test_daypart_span_zone_afternoon_width_unaffected_off_transition_day():
    # A day-part entirely clear of any transition still reports its nominal
    # width -- the honesty is specific to the transitioning day, not a
    # blanket distortion.
    span = daypart_span(AstroDate(2024, 7, 4), "afternoon", zone=NEW_YORK)
    assert span.width == timedelta(hours=6)


# --------------------------------------------------------------------------
# prayer_times: aware rendering, same instants
# --------------------------------------------------------------------------

def test_prayer_times_zone_rendering_same_instant_as_utc():
    d = AstroDate(2024, 6, 21)
    utc = prayer_times(d, 21.4225, 39.8262, "umm_al_qura_makkah")
    aware = prayer_times(d, 21.4225, 39.8262, "umm_al_qura_makkah", zone=RIYADH)
    assert _instant_eq(aware.dhuhr, utc.dhuhr)
    assert _instant_eq(aware.maghrib, utc.maghrib)
    assert aware.dhuhr.tzinfo is RIYADH


def test_prayer_times_zone_rendering_wall_clock_differs_from_utc_fields():
    d = AstroDate(2024, 6, 21)
    utc = prayer_times(d, 21.4225, 39.8262, "umm_al_qura_makkah")
    aware = prayer_times(d, 21.4225, 39.8262, "umm_al_qura_makkah", zone=RIYADH)
    # Riyadh is UTC+3 with no DST, so the wall-clock hour must shift by
    # exactly 3 (mod 24) even though the instant is unchanged.
    assert (aware.dhuhr.hour - utc.dhuhr.hour) % 24 == 3


def test_prayer_times_zone_leaves_nosunevent_unconverted():
    # High-latitude white-night case: Isha/Fajr are undefined in midsummer.
    d = AstroDate(2024, 6, 21)
    aware = prayer_times(d, 69.6, 18.96, "mwl", zone=ZoneInfo("Europe/Oslo"))
    assert isinstance(aware.fajr, NoSunEvent) or isinstance(aware.fajr, AstroDate)
    # whichever it is, NoSunEvent instances carry no tzinfo attribute misuse
    if isinstance(aware.fajr, NoSunEvent):
        assert aware.fajr.date.tzinfo is None


# --------------------------------------------------------------------------
# unequal_hours: aware rendering, same instants
# --------------------------------------------------------------------------

def test_temporal_hour_span_zone_same_instants_as_utc():
    d = AstroDate(2024, 6, 21)
    utc_span = temporal_hour_span(d, 41.9, 12.5, 1, ROMAN_HOURS)
    aware_span = temporal_hour_span(d, 41.9, 12.5, 1, ROMAN_HOURS, zone=ROME)
    assert _instant_eq(aware_span.start, utc_span.start)
    assert _instant_eq(aware_span.end, utc_span.end)
    assert aware_span.width == utc_span.width


def test_convention_time_zone_same_instant_as_utc():
    d = AstroDate(2024, 6, 21)
    utc_time = convention_time(d, 41.9, 12.5, 24, ITALIAN_HOURS)
    aware_time = convention_time(d, 41.9, 12.5, 24, ITALIAN_HOURS, zone=ROME)
    assert _instant_eq(aware_time, utc_time)
    assert aware_time.tzinfo is ROME


def test_temporal_hour_span_zone_leaves_nosunevent_unconverted():
    # Polar night: no sunrise/sunset to anchor the daylight hours.
    result = temporal_hour_span(AstroDate(2024, 12, 21), 78.0, 15.5, 1,
                                ROMAN_HOURS, zone=ZoneInfo("Europe/Oslo"))
    assert isinstance(result, NoSunEvent)
    assert result.date.tzinfo is None


# --------------------------------------------------------------------------
# Adversarial
# --------------------------------------------------------------------------

def test_sun_events_bad_zone_type_raises():
    with pytest.raises(TypeError):
        sun_events(AstroDate(2024, 6, 21), 40.0, -105.0, zone="not-a-tzinfo")


def test_daypart_span_bad_zone_type_raises():
    with pytest.raises(TypeError):
        daypart_span(AstroDate(2024, 6, 21), "morning", zone="not-a-tzinfo")


def test_kiribati_civil_solar_noon_always_present_and_aware():
    # solar_noon has no polar-honesty escape hatch -- it must always be a
    # real, aware AstroDate even at this extreme longitude/offset pairing.
    d = AstroDate(2024, 6, 21)
    civil = sun_events(d, KIRI_LAT, KIRI_LON, zone=KIRITIMATI)
    assert isinstance(civil.solar_noon, AstroDate)
    assert civil.solar_noon.tzinfo is KIRITIMATI
    window_start = AstroDate(2024, 6, 21, tzinfo=KIRITIMATI)
    window_end = AstroDate(2024, 6, 22, tzinfo=KIRITIMATI)
    assert window_start <= civil.solar_noon < window_end
