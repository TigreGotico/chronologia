"""Historical local time: local mean time and apparent solar time.

Before the railways forced standard time zones (Britain 1847, the
international zone system from 1884), every town kept its own clock set
by the sun.  This module reconstructs the two civil time reckonings that
predate the zones, both expressed against a single UTC/GMT reference so
they compose with the rest of :mod:`chronologia`:

* **Local mean time (LMT)** -- mean solar time at a meridian.  The clock
  runs on the *mean* (fictitious, uniform-rate) sun, so it advances at a
  constant rate; it differs from UTC purely by the observer's longitude,
  at the Earth's rotation rate of 4 minutes of time per degree
  (360 degrees / 24 h).  East of Greenwich is *ahead* of UTC (positive
  offset), west is *behind*.  :func:`local_mean_time` builds the
  :class:`LMTZone` fixed-offset zone for a longitude.

* **Apparent solar time** -- what a sundial reads: mean solar time
  corrected by the *equation of time*, the accumulated effect of the
  Earth's orbital eccentricity and axial tilt that makes the true sun run
  ahead of or behind the mean sun over the year (:func:`equation_of_time`,
  :func:`apparent_solar_time`).

Convention (class B -- convention-bearing, not a physical measurement):
LMT is *mean* solar time at the meridian, so it carries no equation-of-time
correction; apparent solar time adds that correction.  Longitude sign is
**east positive** (ISO 6709 / the geographic convention), so Lisbon at
about 9.14 degrees W has a *negative* longitude and a *negative* (behind
UTC) offset.

Source for the equation of time: Honsberg & Bowden, "Solar Time"
(PVCDROM / PVEducation), a mirror of the NOAA/Woolf closed-form
approximation --
``chronologia/../ (papers/standards/equation_of_time_pvcdrom_solar_time.html)``.
It states the formula is accurate to within half a minute; that bound is
exposed as :data:`EOT_ACCURACY`.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from chronologia.astrodate import AstroDate

#: Earth's rotation rate expressed as time-of-day per degree of longitude:
#: 360 degrees in 24 hours == 4 minutes of time per degree.
SECONDS_PER_DEGREE = 4 * 60  # 240 s

#: Stated accuracy of the equation-of-time approximation used here: the
#: cited source (Honsberg & Bowden, "Solar Time") gives its closed form as
#: accurate "to within half a minute".  A class-B, convention-bearing bound.
EOT_ACCURACY = timedelta(seconds=30)


@dataclass(frozen=True)
class LMTZone:
    """A fixed-offset zone: local **mean** solar time at a meridian.

    ``longitude_deg`` is the meridian, **east positive** (Lisbon ~ -9.14).
    ``offset`` is the exact time difference from UTC/GMT, longitude times
    4 minutes per degree, carried to seconds precision as a
    :class:`~datetime.timedelta`.

    This is *mean* solar time -- it runs at a uniform rate and carries no
    equation-of-time correction (that is apparent solar time's job; see
    :func:`apparent_solar_time`).  The type duck-types the read-only part
    of :class:`datetime.tzinfo` (:meth:`utcoffset`, :meth:`tzname`,
    :meth:`dst`) so it can label an instant, but it is a plain frozen
    dataclass, not a ``tzinfo`` subclass.
    """
    longitude_deg: float
    offset: timedelta

    def utcoffset(self, dt: object = None) -> timedelta:
        """The fixed offset from UTC (``tzinfo`` protocol)."""
        return self.offset

    def dst(self, dt: object = None) -> None:
        """Always ``None`` -- mean solar time has no daylight-saving rule."""
        return None

    def tzname(self, dt: object = None) -> str:
        """Label such as ``LMT+00:36:34(lambda=9.140E)``.

        The signed ``HH:MM:SS`` offset from UTC followed by the meridian in
        the ``lambda=`` notation with an ``E``/``W`` hemisphere suffix.
        """
        total = int(round(self.offset.total_seconds()))
        sign = "+" if total >= 0 else "-"
        total = abs(total)
        hh, rem = divmod(total, 3600)
        mm, ss = divmod(rem, 60)
        lon = self.longitude_deg
        hemi = "E" if lon >= 0 else "W"
        return (f"LMT{sign}{hh:02d}:{mm:02d}:{ss:02d}"
                f"(lambda={abs(lon):.3f}{hemi})")

    def from_utc(self, instant) -> AstroDate:
        """Convert a UTC instant to this zone's local **mean** time.

        ``instant`` is a UTC :class:`~datetime.datetime`,
        :class:`~datetime.date`, or :class:`AstroDate`; the return is the
        LMT wall-clock reading as an :class:`AstroDate`.
        """
        return _as_astrodate(instant) + self.offset


def local_mean_time(longitude_deg: float) -> LMTZone:
    """Build the local-mean-time zone for a meridian.

    The offset from UTC/GMT mean time is ``longitude_deg * 4 minutes``
    (east positive), exact to seconds:

    >>> local_mean_time(0).offset
    datetime.timedelta(0)
    >>> local_mean_time(-9.14).tzname()
    'LMT-00:36:34(lambda=9.140W)'

    Greenwich (0 degrees) yields a zero offset by construction; every
    other meridian's clock differs from UTC purely by longitude.
    """
    seconds = round(longitude_deg * SECONDS_PER_DEGREE)
    return LMTZone(longitude_deg=longitude_deg,
                   offset=timedelta(seconds=seconds))


def _day_of_year(d) -> int:
    """Day-of-year (Jan 1 == 1), leap-year-aware, range-safe.

    Works for any :class:`AstroDate` / :class:`~datetime.date` /
    :class:`~datetime.datetime` via the proleptic ordinal, so it never
    overflows the ``datetime`` year bounds.
    """
    point = _as_astrodate(d)
    jan1 = AstroDate(point.year, 1, 1)
    return point.toordinal() - jan1.toordinal() + 1


def equation_of_time(d) -> timedelta:
    """Equation of time on a given date, as a :class:`~datetime.timedelta`.

    Transcribes the closed-form approximation from Honsberg & Bowden,
    "Solar Time" (PVCDROM / PVEducation),
    ``papers/standards/equation_of_time_pvcdrom_solar_time.html``::

        EoT = 9.87 * sin(2B) - 7.53 * cos(B) - 1.5 * sin(B)   [minutes]
        B   = (360 / 365) * (day_of_year - 81)                [degrees]

    accurate to within half a minute (:data:`EOT_ACCURACY`).

    **Sign convention (stated explicitly, the classic confusion):** the
    source defines local solar time as ``LST = LT + EoT`` -- the equation
    of time is *added* to mean time to get apparent (sundial) time.  So a
    **positive** value means the apparent sun is **ahead** of the mean sun
    (the sundial runs *fast* relative to the clock); a negative value means
    the sundial runs *slow*.  This is ``EoT = apparent - mean``.  The
    yearly extremes are about ``+16.4 min`` in early November (sundial
    fastest) and about ``-14.2 min`` in mid-February (sundial slowest).

    ``d`` may be an :class:`AstroDate`, :class:`~datetime.date`, or
    :class:`~datetime.datetime`; only the calendar date matters, and leap
    years are handled via a true day-of-year count.
    """
    n = _day_of_year(d)
    b = math.radians((360.0 / 365.0) * (n - 81))
    minutes = 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)
    return timedelta(minutes=minutes)


def apparent_solar_time(instant, longitude_deg: float) -> AstroDate:
    """Apparent (sundial) solar time for a UTC instant at a longitude.

    ``apparent = LMT + equation_of_time`` -- mean solar time at the
    meridian plus the additive equation-of-time correction (the source's
    ``LST = LT + EoT`` convention; see :func:`equation_of_time`).  Class-B,
    convention-bearing: the equation-of-time term is good to within
    :data:`EOT_ACCURACY`.

    ``instant`` is treated as a UTC :class:`~datetime.datetime` /
    :class:`~datetime.date` / :class:`AstroDate`; the return is the
    apparent-solar wall-clock reading as an :class:`AstroDate`.
    """
    zone = local_mean_time(longitude_deg)
    lmt = zone.from_utc(instant)
    return lmt + equation_of_time(lmt)


def _as_astrodate(instant) -> AstroDate:
    if isinstance(instant, AstroDate):
        return instant
    if isinstance(instant, datetime):
        return AstroDate.from_datetime(instant)
    if isinstance(instant, date):
        return AstroDate.from_date(instant)
    raise TypeError(
        f"expected AstroDate, datetime, or date, got {type(instant).__name__}")
