"""Islamic prayer times as cited angle-set variants over the solar machinery.

The five daily prayers plus sunrise are computed from the same NOAA solar
hour-angle engine that :mod:`chronologia.solar` uses; this module adds only the
*jurisprudential* parameters that distinguish the published calculation
conventions -- the twilight depression angles for Fajr and Isha and the shadow
factor for Asr.  Nothing here rules on which convention is correct: each is a
named school with different published angles, and the library computes what the
angles imply and no more.

**Source.**  Definitions, per-convention angles, and the hour-angle / shadow
formulas transcribe the PrayTimes reference documentation --
``papers/standards/praytimes_calculation_methods.html`` (mirror of
https://praytimes.org/calculation).  The Fajr/Isha depression-angle table and
the Asr shadow factors (1 = majority/Shafi'i, 2 = Hanafi) are quoted verbatim
in :data:`CONVENTIONS` and :data:`ASR_METHODS` citations.

**The formulas.**  With ``Dhuhr`` the solar noon (PrayTimes:
``Dhuhr = 12 + TimeZone - Lng/15 - EqT``, here evaluated directly in UTC by
:func:`chronologia.solar.sun_events`):

- ``Fajr  = Dhuhr - T(alpha_fajr)`` and ``Isha = Dhuhr + T(alpha_isha)`` where
  ``T(alpha)`` is the depression-angle hour angle -- exactly the crossing the
  solar engine computes at zenith ``90 + alpha`` (the same form the civil /
  nautical / astronomical twilights use, with the convention's angle in place
  of 6 / 12 / 18 degrees).
- ``Asr = Dhuhr + A(t)`` where ``A(t)`` is the hour angle at which an upright
  object's shadow reaches ``t`` times its height *plus its noon shadow*:
  the sun altitude ``h`` satisfies ``cot(h) = t + tan(|L - D|)`` (``L``
  latitude, ``D`` declination), and the crossing is computed at zenith
  ``90 - h``.
- ``Sunrise`` is the 90.833-degree rise crossing and ``Maghrib`` is sunset --
  both taken straight from :func:`~chronologia.solar.sun_events`.

**Dhuhr margin.**  PrayTimes notes that "a slight margin is usually considered
for Dhuhr"; it is a precautionary custom, not prescribed in the base formula
(``Dhuhr`` = solar noon).  This module reports solar noon unmodified and adds no
margin -- the golden rule again: compute, do not rule.

**Maghrib delay.**  Likewise the 1-3 minute precautionary delay after sunset is
optional custom; ``maghrib`` is the computed sunset exactly.

**High-latitude honesty.**  When the sun never reaches the depression angle
(the short summer nights of high latitudes -- "white nights"), Fajr and/or Isha
are *undefined*: the field is a typed :class:`~chronologia.solar.NoSunEvent`,
never a fabricated time.  The various higher-latitude estimation rules
(middle-of-the-night, one-seventh, angle-based) are **out of scope**: they are
jurisprudential choices about what to substitute when the arithmetic yields
nothing, not arithmetic themselves, and different authorities pick differently.
The variant mechanism here (a frozen convention record) is exactly where such a
rule would later attach as another named school -- but this library will not
invent one.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import timedelta, tzinfo as _tzinfo
from typing import Literal, Optional, Union

from chronologia.astrodate import AstroDate
from chronologia.solar import (SOLAR_ACCURACY, NoSunEvent, SunEvent,
                               _as_astrodate, _boundary, _declination,
                               _eqtime_minutes, _gamma, _midnight_utc,
                               _to_zone, _validate, sun_events)

__all__ = [
    "PrayerConvention",
    "AsrMethod",
    "PrayerTimes",
    "CONVENTIONS",
    "ASR_METHODS",
    "prayer_times",
]

IshaKind = Literal["angle", "interval"]


@dataclass(frozen=True)
class IshaRule:
    """How a convention fixes Isha: a depression *angle* or a fixed *interval*.

    ``kind == "angle"`` -> ``value`` is the sun-depression angle in degrees
    (Isha = Dhuhr + T(value)).  ``kind == "interval"`` -> ``value`` is a number
    of minutes *after Maghrib* (the Umm al-Qura convention: Isha = Maghrib + 90
    min).  Supporting both is the whole reason this is a tagged record and not a
    bare float.
    """
    kind: IshaKind
    value: float


@dataclass(frozen=True)
class PrayerConvention:
    """A named calculation school: the Fajr/Isha parameters plus a citation.

    ``fajr_angle`` and (for angle-based Isha) the Isha angle are sun-depression
    angles in degrees; ``isha`` is an :class:`IshaRule` so the Umm al-Qura
    fixed-interval form is a first-class case.  ``asr_shadow_factor`` is the
    school's default Asr factor (1 for every convention shipped here -- the
    Hanafi factor is selected per call, not baked into the twilight school);
    ``citation`` quotes the published source verbatim.  Frozen: a convention is
    a fixed set of cited constants, never mutated.
    """
    key: str
    fajr_angle: float
    isha: IshaRule
    asr_shadow_factor: int
    citation: str


@dataclass(frozen=True)
class AsrMethod:
    """An Asr shadow-factor school (majority vs Hanafi), with its citation."""
    key: str
    shadow_factor: int
    citation: str


_PRAYTIMES = ("PrayTimes, https://praytimes.org/calculation, "
              "papers/standards/praytimes_calculation_methods.html")

#: The published Fajr/Isha conventions, quoted from the PrayTimes methods table
#: ("Convention / Fajr Angle / Isha Angle").  Each carries the source verbatim.
CONVENTIONS = {
    "mwl": PrayerConvention(
        "mwl", 18.0, IshaRule("angle", 17.0), 1,
        f"Muslim World League: Fajr 18, Isha 17. {_PRAYTIMES}"),
    "isna": PrayerConvention(
        "isna", 15.0, IshaRule("angle", 15.0), 1,
        f"Islamic Society of North America (ISNA): Fajr 15, Isha 15. "
        f"{_PRAYTIMES}"),
    "egyptian_gas": PrayerConvention(
        "egyptian_gas", 19.5, IshaRule("angle", 17.5), 1,
        f"Egyptian General Authority of Survey: Fajr 19.5, Isha 17.5. "
        f"{_PRAYTIMES}"),
    "umm_al_qura_makkah": PrayerConvention(
        "umm_al_qura_makkah", 18.5, IshaRule("interval", 90.0), 1,
        f"Umm al-Qura University, Makkah: Fajr 18.5, Isha 90 minutes after "
        f"Maghrib (120 during Ramadan; the base 90 is used here). {_PRAYTIMES}"),
    "karachi": PrayerConvention(
        "karachi", 18.0, IshaRule("angle", 18.0), 1,
        f"University of Islamic Sciences, Karachi: Fajr 18, Isha 18. "
        f"{_PRAYTIMES}"),
}

#: The two Asr schools.  PrayTimes: "The majority of Islamic schools of thought
#: (Shafi'i, Maliki, Ja'fari, and Hanbali) ... shadow equals the object's own
#: height ... The Hanafi school ... shadow is twice the length of the object",
#: i.e. Asr = Dhuhr + A(1) (standard) or Dhuhr + A(2) (Hanafi).
ASR_METHODS = {
    "standard": AsrMethod(
        "standard", 1,
        f"Majority (Shafi'i, Maliki, Ja'fari, Hanbali): shadow factor 1, "
        f"Asr = Dhuhr + A(1). {_PRAYTIMES}"),
    "hanafi": AsrMethod(
        "hanafi", 2,
        f"Hanafi school: shadow factor 2, Asr = Dhuhr + A(2). {_PRAYTIMES}"),
}


@dataclass(frozen=True)
class PrayerTimes:
    """The day's prayer instants at one location, all in UTC.

    ``dhuhr``, ``sunrise`` and ``maghrib`` come straight from the solar engine;
    ``fajr``, ``asr`` and ``isha`` from the convention's angles / factor.  Every
    time field is a :class:`~chronologia.solar.SunEvent` -- an
    :class:`~chronologia.astrodate.AstroDate` when defined, or a typed
    :class:`~chronologia.solar.NoSunEvent` when the depression angle is never
    reached (white nights) or the sun does not rise / set (polar day / night).
    ``convention`` and ``asr`` name the schools used.
    """
    date: AstroDate
    latitude: float
    longitude: float
    convention: str
    asr: str
    fajr: SunEvent
    sunrise: SunEvent
    dhuhr: AstroDate
    asr_time: SunEvent
    maghrib: SunEvent
    isha: SunEvent


def _asr_zenith(latitude: float, decl: float, factor: int) -> float:
    """Zenith (degrees) of the Asr shadow crossing for ``factor`` (1 or 2).

    Sun altitude ``h`` with ``cot(h) = factor + tan(|L - D|)`` (PrayTimes Asr
    definition); the solar boundary is taken at zenith ``90 - h``.  ``L`` and
    ``D`` are in radians; ``atan2(1, cot)`` gives the always-positive altitude.
    """
    lat = math.radians(latitude)
    cot_h = factor + math.tan(abs(lat - decl))
    altitude = math.atan2(1.0, cot_h)
    return 90.0 - math.degrees(altitude)


def prayer_times(date, latitude: float, longitude: float,
                 convention: str = "mwl",
                 asr: str = "standard",
                 zone: Optional[_tzinfo] = None) -> PrayerTimes:
    """Islamic prayer times for ``date`` at (``latitude``, ``longitude``), UTC.

    ``date`` is an :class:`~chronologia.astrodate.AstroDate`,
    :class:`~datetime.date`, or :class:`~datetime.datetime` (only the calendar
    date is used).  ``latitude`` is degrees north (-90..90), ``longitude``
    degrees **east** (-180..180); both are range-validated.  ``convention``
    selects a Fajr/Isha school from :data:`CONVENTIONS` (``"mwl"``, ``"isna"``,
    ``"egyptian_gas"``, ``"umm_al_qura_makkah"``, ``"karachi"``); ``asr``
    selects the shadow factor from :data:`ASR_METHODS` (``"standard"`` = 1,
    ``"hanafi"`` = 2).  Unknown keys raise :class:`ValueError`.

    ``zone``, when given, changes only *presentation*: every computed instant
    is identical (the underlying hour-angle arithmetic is entirely UTC and
    unaffected), but each real :class:`~chronologia.astrodate.AstroDate` field
    is converted (via :meth:`~chronologia.astrodate.AstroDate.astimezone`)
    into an aware reading in ``zone`` before being returned, so
    ``prayer_times(d, lat, lon, zone=z).dhuhr == prayer_times(d, lat, lon).dhuhr``
    (same instant) while the former prints local wall-clock digits.
    :class:`~chronologia.solar.NoSunEvent` fields (undefined at high
    latitudes) are returned unconverted, since they name no instant.

    Returns a :class:`PrayerTimes`.  Fajr and Isha are typed
    :class:`~chronologia.solar.NoSunEvent` when the depression angle is never
    reached; the higher-latitude estimation rules are deliberately not applied
    (see the module docstring).

    >>> pt = prayer_times(AstroDate(2024, 3, 15), 30.0444, 31.2357, "egyptian_gas")
    >>> pt.dhuhr.strftime("%H:%M")
    '10:04'
    """
    if convention not in CONVENTIONS:
        raise ValueError(
            f"unknown convention {convention!r}; "
            f"choose from {sorted(CONVENTIONS)}")
    if asr not in ASR_METHODS:
        raise ValueError(
            f"unknown asr method {asr!r}; choose from {sorted(ASR_METHODS)}")
    _validate(latitude, longitude)

    conv = CONVENTIONS[convention]
    asr_method = ASR_METHODS[asr]

    point = _as_astrodate(date)
    events = sun_events(point, latitude, longitude)

    g = _gamma(point)
    eqtime = _eqtime_minutes(g)
    decl = _declination(g)

    fajr = _boundary(point, latitude, longitude, 90.0 + conv.fajr_angle,
                     eqtime, decl, evening=False)

    if conv.isha.kind == "angle":
        isha: SunEvent = _boundary(point, latitude, longitude,
                                   90.0 + conv.isha.value, eqtime, decl,
                                   evening=True)
    else:  # fixed interval after maghrib; propagate a polar/absent maghrib
        maghrib_ev = events.sunset
        isha = (maghrib_ev + timedelta(minutes=conv.isha.value)
                if isinstance(maghrib_ev, AstroDate) else maghrib_ev)

    asr_time = _boundary(point, latitude, longitude,
                         _asr_zenith(latitude, decl, asr_method.shadow_factor),
                         eqtime, decl, evening=True)

    def present(value: SunEvent) -> SunEvent:
        if zone is None or not isinstance(value, AstroDate):
            return value
        return _to_zone(value, zone)

    return PrayerTimes(
        date=_midnight_utc(point),
        latitude=latitude,
        longitude=longitude,
        convention=convention,
        asr=asr,
        fajr=present(fajr),
        sunrise=present(events.sunrise),
        # solar_noon is always an AstroDate; present() widens to SunEvent.
        dhuhr=present(events.solar_noon),  # type: ignore[arg-type]
        asr_time=present(asr_time),
        maghrib=present(events.sunset),
        isha=present(isha),
    )
