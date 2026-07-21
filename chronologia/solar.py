"""Arithmetic solar events: sunrise, sunset, solar noon, and twilights.

Transcribes the NOAA *General Solar Position Calculations* / *Sunrise/Sunset
Calculations* (NOAA Global Monitoring Division) closed-form algorithm --
``papers/standards/noaa_general_solar_position_calculations.pdf`` (mirror of
the NOAA Global Monitoring solar-calculator, ``noaa_solar_calculator_details.html``).
Given a calendar date, latitude, and longitude the algorithm yields the day's
sunrise, sunset, solar noon, and the three standard twilight boundaries
(civil / nautical / astronomical, at solar depression -6 / -12 / -18 degrees).

Accuracy (class B -- convention-bearing, not an ephemeris): the NOAA method is
a low-order truncated series stated by NOAA to be accurate to within about a
minute for the years 1901..2099, degrading outside that range and toward the
poles; :data:`SOLAR_ACCURACY` exposes the +/- one minute bound.  Standard
atmospheric refraction and solar-disk size are folded into the fixed
rise/set zenith of 90.833 degrees (NOAA's stated convention); no altitude,
temperature, or pressure correction beyond that is applied.

**Equation of time.**  The algorithm needs the equation of time *and* the solar
declination from the *same* fractional-year angle ``gamma``, so this module
implements NOAA's own ``eqtime``/``decl`` series internally rather than reusing
:func:`chronologia.localtime.equation_of_time` (a different -- Woolf / PVCDROM --
approximation).  Sharing one ``gamma`` keeps declination and equation of time
mutually consistent, which the sunrise formula requires; the two EoT series
agree within their combined stated accuracy (a consistency check lives in the
test suite).  ``gamma`` is evaluated at local noon (the ``(hour-12)/24`` term
is zero), giving one declination/EoT pair per day as the NOAA daily calculator
does.

**Reference frame.**  All returned instants are **UTC** (:class:`AstroDate`),
matching NOAA's ``sunrise = 720 - 4*(longitude + ha) - eqtime`` which yields
minutes past UTC midnight.  Longitude is **east-positive** (ISO 6709, the
convention shared with :mod:`chronologia.localtime`); NOAA's own text states
"longitude ... positive to the east of the Prime Meridian".

**Polar honesty.**  When the sun never rises or never sets for a given field at
a given date and latitude, that field is a typed :class:`NoSunEvent` (the
``NeverExisted`` pattern) carrying the ``kind`` (``polar_day``/``polar_night``),
never a fabricated time and never an exception.  Each boundary is evaluated
independently, so a polar day where the sun clears the horizon but never the
civil-twilight line reports a real ``sunset`` alongside a ``NoSunEvent`` civil
dusk.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Literal, Union

from chronologia.astrodate import AstroDate

#: Stated accuracy of the NOAA truncated-series solar algorithm used here:
#: about +/- one minute for 1901..2099, degrading outside that range and toward
#: the poles.  A class-B, convention-bearing bound.
SOLAR_ACCURACY = timedelta(minutes=1)

#: Rise/set zenith angle in degrees: 90 degrees plus NOAA's fixed 0.833-degree
#: allowance for atmospheric refraction and the solar disk's semidiameter.
ZENITH_OFFICIAL = 90.833
#: Civil-twilight zenith: sun 6 degrees below the horizon.
ZENITH_CIVIL = 96.0
#: Nautical-twilight zenith: sun 12 degrees below the horizon.
ZENITH_NAUTICAL = 102.0
#: Astronomical-twilight zenith: sun 18 degrees below the horizon.
ZENITH_ASTRONOMICAL = 108.0

PolarKind = Literal["polar_day", "polar_night"]


@dataclass(frozen=True)
class NoSunEvent:
    """A solar boundary that does not occur on a given date/latitude.

    Returned in place of an :class:`AstroDate` when the sun never reaches the
    requested altitude that day: ``polar_day`` when the sun stays *above* the
    line (it never sets past it), ``polar_night`` when it stays *below* (it
    never rises to it).  Carries the ``date`` and ``latitude`` that produced
    the condition; never a fabricated time, never an exception (the
    ``NeverExisted`` pattern).
    """
    kind: PolarKind
    date: AstroDate
    latitude: float


#: A solar boundary is either a real UTC instant or a typed absence.
SunEvent = Union[AstroDate, NoSunEvent]


@dataclass(frozen=True)
class SunEvents:
    """The solar boundaries of one calendar day at one location, all in UTC.

    ``solar_noon`` is always an :class:`AstroDate` (it depends only on
    longitude and the equation of time).  Every other field is a
    :data:`SunEvent` -- an :class:`AstroDate` when the crossing occurs, or a
    :class:`NoSunEvent` when it does not.  Dawn fields are the morning
    crossings, dusk fields the evening crossings; ``sunrise``/``sunset`` use
    the 90.833-degree rise/set zenith, the twilight fields the -6/-12/-18
    degree depression zeniths.
    """
    date: AstroDate
    latitude: float
    longitude: float
    solar_noon: AstroDate
    sunrise: SunEvent
    sunset: SunEvent
    civil_dawn: SunEvent
    civil_dusk: SunEvent
    nautical_dawn: SunEvent
    nautical_dusk: SunEvent
    astronomical_dawn: SunEvent
    astronomical_dusk: SunEvent


def _as_astrodate(instant) -> AstroDate:
    if isinstance(instant, AstroDate):
        return instant
    if isinstance(instant, datetime):
        return AstroDate.from_datetime(instant)
    if isinstance(instant, date):
        return AstroDate.from_date(instant)
    raise TypeError(
        f"expected AstroDate, datetime, or date, got {type(instant).__name__}")


def _day_of_year(point: AstroDate) -> int:
    return point.toordinal() - AstroDate(point.year, 1, 1).toordinal() + 1


def _is_leap(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _gamma(point: AstroDate) -> float:
    """NOAA fractional-year angle (radians), evaluated at local noon.

    ``gamma = (2*pi/N) * (day_of_year - 1 + (hour-12)/24)`` with ``N`` = 366 in
    leap years else 365; ``hour`` is 12 so the sub-day term vanishes.
    """
    n = 366.0 if _is_leap(point.year) else 365.0
    return (2.0 * math.pi / n) * (_day_of_year(point) - 1)


def _eqtime_minutes(g: float) -> float:
    """NOAA equation of time in minutes from the fractional-year angle."""
    return 229.18 * (
        0.000075
        + 0.001868 * math.cos(g)
        - 0.032077 * math.sin(g)
        - 0.014615 * math.cos(2 * g)
        - 0.040849 * math.sin(2 * g))


def _declination(g: float) -> float:
    """NOAA solar declination in radians from the fractional-year angle."""
    return (
        0.006918
        - 0.399912 * math.cos(g)
        + 0.070257 * math.sin(g)
        - 0.006758 * math.cos(2 * g)
        + 0.000907 * math.sin(2 * g)
        - 0.002697 * math.cos(3 * g)
        + 0.00148 * math.sin(3 * g))


def _midnight_utc(point: AstroDate) -> AstroDate:
    return AstroDate(point.year, point.month, point.day)


def _minutes_to_instant(midnight: AstroDate, minutes: float) -> AstroDate:
    """UTC minutes-past-midnight to an :class:`AstroDate` (rolls across days)."""
    return midnight + timedelta(minutes=minutes)


def _boundary(point: AstroDate, latitude: float, longitude: float,
              zenith: float, eqtime: float, decl: float,
              *, evening: bool) -> SunEvent:
    """One morning/evening crossing at a zenith, or a typed :class:`NoSunEvent`.

    ``cos(ha) = cos(zenith)/(cos(lat)cos(decl)) - tan(lat)tan(decl)``.  When it
    exceeds 1 the sun never reaches the line (stays below -> ``polar_night``);
    when below -1 it never leaves it (stays above -> ``polar_day``).
    """
    lat = math.radians(latitude)
    cos_ha = (math.cos(math.radians(zenith))
              / (math.cos(lat) * math.cos(decl))
              - math.tan(lat) * math.tan(decl))
    if cos_ha > 1.0:
        return NoSunEvent("polar_night", _midnight_utc(point), latitude)
    if cos_ha < -1.0:
        return NoSunEvent("polar_day", _midnight_utc(point), latitude)
    ha = math.degrees(math.acos(cos_ha))
    signed = -ha if evening else ha
    minutes = 720.0 - 4.0 * (longitude + signed) - eqtime
    return _minutes_to_instant(_midnight_utc(point), minutes)


def _validate(latitude: float, longitude: float) -> None:
    if not -90.0 <= latitude <= 90.0:
        raise ValueError(f"latitude must be in -90..90, got {latitude}")
    if not -180.0 <= longitude <= 180.0:
        raise ValueError(f"longitude must be in -180..180, got {longitude}")


def sun_events(date, latitude: float, longitude: float) -> SunEvents:
    """Solar boundaries of ``date`` at (``latitude``, ``longitude``), in UTC.

    ``date`` is an :class:`AstroDate`, :class:`~datetime.date`, or
    :class:`~datetime.datetime` (only the calendar date is used).  Latitude is
    degrees north (-90..90), longitude degrees **east** (-180..180); both are
    range-validated (``ValueError`` otherwise).  Returns a :class:`SunEvents`
    whose ``solar_noon`` is always present and whose rise/set/twilight fields
    are each an :class:`AstroDate` or a :class:`NoSunEvent` (polar honesty).

    >>> ev = sun_events(AstroDate(2000, 3, 20), 0.0, 0.0)
    >>> ev.solar_noon.hour
    12
    """
    _validate(latitude, longitude)
    point = _as_astrodate(date)
    midnight = _midnight_utc(point)
    g = _gamma(point)
    eqtime = _eqtime_minutes(g)
    decl = _declination(g)

    solar_noon = _minutes_to_instant(midnight, 720.0 - 4.0 * longitude - eqtime)

    def morning(z):
        return _boundary(point, latitude, longitude, z, eqtime, decl,
                         evening=False)

    def evening(z):
        return _boundary(point, latitude, longitude, z, eqtime, decl,
                         evening=True)

    return SunEvents(
        date=midnight,
        latitude=latitude,
        longitude=longitude,
        solar_noon=solar_noon,
        sunrise=morning(ZENITH_OFFICIAL),
        sunset=evening(ZENITH_OFFICIAL),
        civil_dawn=morning(ZENITH_CIVIL),
        civil_dusk=evening(ZENITH_CIVIL),
        nautical_dawn=morning(ZENITH_NAUTICAL),
        nautical_dusk=evening(ZENITH_NAUTICAL),
        astronomical_dawn=morning(ZENITH_ASTRONOMICAL),
        astronomical_dusk=evening(ZENITH_ASTRONOMICAL),
    )


def sunset_day_start(date, latitude: float, longitude: float) -> SunEvent:
    """The sunset that opens the sunset-anchored civil day of ``date``.

    Sunset-anchored calendars (Hebrew, Islamic) begin each day at the *previous*
    evening's sunset, so the day labelled ``date`` starts at sunset on
    ``date - 1``.  Returns that computed sunset as a UTC :class:`AstroDate`, or
    a :class:`NoSunEvent` in polar conditions -- the location-supplied upgrade
    to the arithmetic sunset-day convention.  The location-free civil-day
    convention (midnight) remains the default everywhere else in the library;
    this helper is opted into only when a latitude/longitude is available.

    >>> ss = sunset_day_start(AstroDate(2024, 6, 1), 31.78, 35.22)
    >>> ss.day
    31
    """
    _validate(latitude, longitude)
    point = _as_astrodate(date)
    previous = _midnight_utc(point) - timedelta(days=1)
    return sun_events(previous, latitude, longitude).sunset
