"""Unequal (temporal / seasonal) hours and clock-count conventions.

Before mechanical clocks imposed a steady 60-minute hour, most of the
pre-modern world divided *daylight* into a fixed count of hours and *night*
into another.  The count was constant; the hour's length was not.  A daytime
hour stretched in summer, when the sun was up for longer, and shrank in winter
-- at Rome's latitude (about 41.9 degrees north) a Roman daytime hour ran to
roughly 76 minutes at the June solstice and shrank to about 46 minutes at the
December solstice, while the night hours did the mirror-opposite.  These are
**proportional** or **temporal** (also *seasonal*) hours.

This module builds those hours on top of :mod:`chronologia.solar`.  The
daylight span (sunrise to sunset, or a twilight-anchored variant) is divided
into the system's ``day_hours``; the night span (sunset to the next sunrise)
into its ``night_hours``.  Each unequal hour is returned as a
:class:`~chronologia.astrodate.DateSpan` whose ``width`` *is* the actual,
date- and latitude-varying length of that hour.

Two families are provided:

* **Proportional-hour systems** (:class:`UnequalHourSystem`,
  :func:`temporal_hour_span`) -- Roman/medieval 12+12 temporal hours, Jewish
  *sha'ot zmaniyot* (GRA), and Edo-period Japanese 6+6 hours.
* **Clock-count conventions** (:class:`ClockConvention`,
  :func:`convention_time`) -- *equal*-hour counts re-anchored to a solar
  event: Italian hours counted 1..24 from sunset, Babylonian hours counted
  from sunrise.

**Basis.**  Every span/instant produced here inherits the class-B accuracy of
:mod:`chronologia.solar` -- the NOAA arithmetic sunrise/sunset is
convention-bearing, not an ephemeris (``SOLAR_ACCURACY`` bounds it to about a
minute for 1901..2099).  Proportional-hour spans are therefore built with
``basis="tabulated"``: their endpoints come from a deterministic solar model
that may differ from a precise observation.

**Polar honesty (typed pass-through).**  When the solar anchor an unequal hour
needs does not occur -- the sun never rises or never sets that day --
:func:`sun_events` returns a :class:`~chronologia.solar.NoSunEvent`.  This
module never raises and never fabricates a time in that case: it returns the
very :class:`NoSunEvent` it received, so polar conditions propagate as data.

**Magen Avraham zmanim -- omitted, on purpose.**  The GRA reckons the twelve
*sha'ot zmaniyot* from sunrise (*netz*) to sunset (*shkia*), which maps
exactly onto :func:`sun_events`' ``sunrise``/``sunset``.  The competing Magen
Avraham reckoning runs from *alot hashachar* to *tzeit hakochavim* -- dawn and
nightfall -- standardly fixed at solar depressions of 16.1 degrees (alot) and
8.5 degrees (tzeit), or the equivalent fixed 72 minutes.  :mod:`chronologia.solar`
exposes only the 6 / 12 / 18-degree civil / nautical / astronomical twilights;
none of those angles is the Magen Avraham definition, so treating civil dawn
(6 degrees) as *alot* would be a fabricated equivalence, not a cited one.
Rather than ship a mislabelled proxy, the Magen Avraham system is omitted until
solar.py can produce a 16.1 / 8.5-degree crossing.  The ``day_anchor`` field
below is nonetheless kept general (it accepts ``"civil_dawn"``) so the twilight
-anchored shape is expressible the moment a citable clean mapping exists.

Sources are cited per system in the ``citations`` / ``citation`` fields and in
``test/test_unequal_hours.py``.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Union

from chronologia.astrodate import BASIS_TABULATED, AstroDate, DateSpan
from chronologia.solar import NoSunEvent, SunEvent, SunEvents, sun_events

#: Daylight is bounded by (dawn field, dusk field) of :class:`SunEvents`.  A
#: system's ``day_anchor`` selects the pair: ``"sunrise"`` -> the true
#: rise/set horizon crossing (the GRA / Roman / Edo convention); ``"civil_dawn"``
#: -> the 6-degree civil twilight pair (a twilight-anchored shape, kept
#: expressible though no shipped system uses it -- see the module docstring on
#: the Magen Avraham omission).
_ANCHOR_FIELDS = {
    "sunrise": ("sunrise", "sunset"),
    "civil_dawn": ("civil_dawn", "civil_dusk"),
}

#: A clock convention's ``anchor_event`` names the :class:`SunEvents` field it
#: counts equal hours from.  ``"midnight"`` uses the day's UTC midnight (always
#: present); the other three are solar events that may be a :class:`NoSunEvent`.
_CONVENTION_FIELDS = {
    "sunset": "sunset",
    "sunrise": "sunrise",
    "noon": "solar_noon",
}


@dataclass(frozen=True)
class UnequalHourSystem:
    """A proportional-hour system: ``day_hours`` of daylight, ``night_hours``
    of night, each an equal fraction of its (date/latitude-varying) span.

    ``day_anchor`` selects which solar boundaries delimit daylight -- see
    :data:`_ANCHOR_FIELDS`.  ``citations`` records the canonical source(s) the
    division traces to.  Frozen and hashable; the shipped instances live in
    :data:`UNEQUAL_HOUR_SYSTEMS`.
    """
    key: str
    day_hours: int
    night_hours: int
    day_anchor: str
    citations: tuple[str, ...] = ()

    def __post_init__(self):
        if self.day_hours < 1 or self.night_hours < 1:
            raise ValueError(
                f"{self.key}: day_hours/night_hours must be >= 1, "
                f"got {self.day_hours}/{self.night_hours}")
        if self.day_anchor not in _ANCHOR_FIELDS:
            raise ValueError(
                f"{self.key}: unknown day_anchor {self.day_anchor!r}; "
                f"expected one of {sorted(_ANCHOR_FIELDS)}")

    @property
    def total_hours(self) -> int:
        """Day + night hours: the valid range of ``hour_number`` (1..total)."""
        return self.day_hours + self.night_hours


@dataclass(frozen=True)
class ClockConvention:
    """An *equal*-hour clock count re-anchored to a solar event.

    Unlike a proportional-hour system, the hour here is a steady 60 minutes;
    only the *origin* of the count moves with the sun.  ``anchor_event`` is one
    of ``"sunset"``, ``"sunrise"``, ``"noon"``, ``"midnight"``; ``direction``
    is +1 (count forward from the anchor) or -1; ``count`` is the hours in one
    cycle (24).  The count wraps modulo ``count``, so the ``count``-th hour
    coincides with the anchor itself (Italian hour 24 == sunset).  Shipped
    instances live in :data:`CLOCK_CONVENTIONS`.
    """
    key: str
    anchor_event: str
    direction: int
    count: int
    citation: str = ""

    def __post_init__(self):
        if self.anchor_event not in _CONVENTION_FIELDS \
                and self.anchor_event != "midnight":
            raise ValueError(
                f"{self.key}: unknown anchor_event {self.anchor_event!r}; "
                f"expected sunset/sunrise/noon/midnight")
        if self.direction not in (1, -1):
            raise ValueError(
                f"{self.key}: direction must be +1 or -1, got {self.direction}")
        if self.count < 1:
            raise ValueError(f"{self.key}: count must be >= 1, got {self.count}")


def _anchor_instant(events: SunEvents, anchor_event: str) -> SunEvent:
    if anchor_event == "midnight":
        return events.date
    return getattr(events, _CONVENTION_FIELDS[anchor_event])


def temporal_hour_span(date, latitude: float, longitude: float,
                       hour_number: int,
                       system: UnequalHourSystem) -> Union[DateSpan, NoSunEvent]:
    """The ``hour_number``-th unequal hour of ``date`` under ``system``.

    ``hour_number`` runs ``1..system.total_hours``: ``1..day_hours`` are the
    daylight hours (dawn->dusk divided into ``day_hours``), and the rest are
    the night hours (this evening's dusk -> the *next* morning's dawn divided
    into ``night_hours``).  Latitude is degrees north, longitude degrees east
    (the :func:`sun_events` convention).

    Returns a :class:`DateSpan` whose ``width`` is that hour's true length --
    which varies with date and latitude -- and whose ``basis`` is
    ``"tabulated"`` (the solar model is class-B; see the module docstring).
    If the solar anchor the hour needs does not occur (polar day / night), the
    typed :class:`NoSunEvent` from :func:`sun_events` is returned unchanged --
    never an exception, never a fabricated time.

    >>> ss = temporal_hour_span(AstroDate(2024, 6, 21), 41.9, 12.5, 1, ROMAN_HOURS)
    >>> round(ss.width.total_seconds() / 60)   # a June day-hour at Rome
    76
    """
    if not 1 <= hour_number <= system.total_hours:
        raise ValueError(
            f"hour_number must be 1..{system.total_hours} for {system.key}, "
            f"got {hour_number}")
    dawn_field, dusk_field = _ANCHOR_FIELDS[system.day_anchor]
    events = sun_events(date, latitude, longitude)

    if hour_number <= system.day_hours:
        start = getattr(events, dawn_field)
        end = getattr(events, dusk_field)
        count = system.day_hours
        index = hour_number
    else:
        start = getattr(events, dusk_field)
        next_events = sun_events(events.date + timedelta(days=1),
                                 latitude, longitude)
        end = getattr(next_events, dawn_field)
        count = system.night_hours
        index = hour_number - system.day_hours

    if isinstance(start, NoSunEvent):
        return start
    if isinstance(end, NoSunEvent):
        return end

    # Integer-microsecond boundaries so the hours tile with no fencepost gap
    # (hour k's end is byte-identical to hour k+1's start) and the final hour
    # ends exactly on ``end`` -- float timedelta arithmetic would drift by a
    # microsecond at the seam.  The hour's ``width`` still varies by season.
    span_us = int((end - start).total_seconds() * 1_000_000)

    def boundary(i: int) -> AstroDate:
        return start + timedelta(microseconds=round(span_us * i / count))

    return DateSpan(boundary(index - 1), boundary(index),
                    basis=BASIS_TABULATED)


def convention_time(date, latitude: float, longitude: float, hour: int,
                    convention: ClockConvention) -> Union[AstroDate, NoSunEvent]:
    """The instant of clock-count ``hour`` under ``convention`` on ``date``.

    The hour is a steady 60 minutes; the count's origin is ``convention``'s
    solar anchor.  ``hour`` runs ``0..convention.count`` and wraps modulo
    ``count``, so hour 0 and hour ``count`` both land on the anchor itself
    (Italian hour 24 == the sunset that opens the day; Babylonian hour 0 ==
    sunrise).  Returns a UTC :class:`AstroDate`, or the typed
    :class:`NoSunEvent` from :func:`sun_events` when the anchor does not occur.

    >>> t = convention_time(AstroDate(2024, 6, 21), 41.9, 12.5, 24, ITALIAN_HOURS)
    >>> ev = sun_events(AstroDate(2024, 6, 21), 41.9, 12.5)
    >>> t == ev.sunset
    True
    """
    if not 0 <= hour <= convention.count:
        raise ValueError(
            f"hour must be 0..{convention.count} for {convention.key}, "
            f"got {hour}")
    events = sun_events(date, latitude, longitude)
    anchor = _anchor_instant(events, convention.anchor_event)
    if isinstance(anchor, NoSunEvent):
        return anchor
    steps = hour % convention.count
    return anchor + convention.direction * timedelta(hours=steps)


# --------------------------------------------------------------------------
# Shipped systems and conventions.
# --------------------------------------------------------------------------

#: Roman / medieval temporal hours: 12 of daylight, 12 of night, the daylight
#: bounded by sunrise and sunset.  Rome introduced the twelve-hour division of
#: daylight in 263 BC with its first public sundial (Pliny the Elder,
#: *Naturalis Historia* VII.212-215); the analemma construction that lays out
#: the seasonally varying hour-lines of a sundial is Vitruvius, *De
#: architectura* IX.7.  The lengthening/shortening of the hora with the season
#: is catalogued by G. Bilfinger, *Die antiken Stundenangaben* (Stuttgart 1888).
ROMAN_HOURS = UnequalHourSystem(
    key="roman",
    day_hours=12,
    night_hours=12,
    day_anchor="sunrise",
    citations=(
        "Pliny the Elder, Naturalis Historia VII.212-215 (twelve daylight "
        "hours at Rome; first public sundial 263 BC).",
        "Vitruvius, De architectura IX.7 (analemma / seasonal hour-lines).",
        "G. Bilfinger, Die antiken Stundenangaben (Stuttgart 1888).",
    ),
)

#: Jewish *sha'ot zmaniyot* by the Vilna Gaon (GRA): the daylight from sunrise
#: (*netz hachama*) to sunset (*shkia*) divided into twelve proportional hours;
#: the night likewise.  Shulchan Aruch, Orach Chayim 233:1 and 261:1-2, with
#: the GRA reckoning as summarised in Mishnah Berurah 233:4.  (The Magen
#: Avraham dawn->nightfall variant is deliberately omitted -- see the module
#: docstring: its 16.1 / 8.5-degree anchors are not among solar.py's twilights.)
ZMANIM_GRA = UnequalHourSystem(
    key="zmanim_gra",
    day_hours=12,
    night_hours=12,
    day_anchor="sunrise",
    citations=(
        "Shulchan Aruch, Orach Chayim 233:1, 261:1-2 (sha'ot zmaniyot).",
        "Mishnah Berurah 233:4 (GRA: sunrise netz to sunset shkia / 12).",
    ),
)

#: Edo-period Japanese hours (*toki*): six daylight and six night hours, the
#: day divided at sunrise and sunset, each hour again varying with the season
#: (the wadokei clocks were built to keep this unequal time).  Y. Frumer,
#: *Making Time: Astronomical Time Measurement in Tokugawa Japan* (Chicago
#: 2018), ch. 1-2.
EDO_JAPANESE = UnequalHourSystem(
    key="edo_japanese",
    day_hours=6,
    night_hours=6,
    day_anchor="sunrise",
    citations=(
        "Y. Frumer, Making Time: Astronomical Time Measurement in Tokugawa "
        "Japan (Chicago 2018), ch. 1-2 (six day + six night unequal toki).",
    ),
)

#: Italian hours (*ore all'italiana*): twenty-four *equal* hours counted from
#: sunset, so the 24th hour struck at sunset and the count restarted.  Used
#: across Italy into the 18th century.  G. Dohrn-van Rossum, *History of the
#: Hour: Clocks and Modern Temporal Orders* (Chicago 1996), ch. 5-6.
ITALIAN_HOURS = ClockConvention(
    key="italian_hours",
    anchor_event="sunset",
    direction=1,
    count=24,
    citation=(
        "G. Dohrn-van Rossum, History of the Hour (Chicago 1996), ch. 5-6 "
        "(ore italiane: 24 equal hours counted from sunset)."),
)

#: Babylonian hours: equal hours counted from sunrise, hour 0 at sunrise.
#: The sunrise-anchored day-count is the Babylonian astronomical convention
#: reported by O. Neugebauer, *A History of Ancient Mathematical Astronomy*
#: (Berlin 1975), pt. 1 (on the "Babylonian" vs "Italian" reckonings of the
#: civil day from sunrise vs sunset).
BABYLONIAN_HOURS = ClockConvention(
    key="babylonian_hours",
    anchor_event="sunrise",
    direction=1,
    count=24,
    citation=(
        "O. Neugebauer, A History of Ancient Mathematical Astronomy (Berlin "
        "1975), pt. 1 (Babylonian day counted in equal hours from sunrise)."),
)

#: Registry of the shipped proportional-hour systems, keyed by ``.key``.
UNEQUAL_HOUR_SYSTEMS = {
    s.key: s for s in (ROMAN_HOURS, ZMANIM_GRA, EDO_JAPANESE)
}

#: Registry of the shipped clock-count conventions, keyed by ``.key``.
CLOCK_CONVENTIONS = {
    c.key: c for c in (ITALIAN_HOURS, BABYLONIAN_HOURS)
}
