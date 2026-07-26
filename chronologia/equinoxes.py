"""Equinoxes, solstices, astronomical seasons and the 24 solar terms.

The instants of the equinoxes and solstices, the astronomical season spans
they bound, and the Chinese *jieqi* (24 solar terms) all come from **mean
orbital theory** -- closed-form arithmetic on mean elements, not a full
ephemeris integration (the package's no-ephemeris scope, shared with
:mod:`chronologia.moon`).  Like moon phases this is exact arithmetic on an
approximate model: the model carries the error, not the computation, so every
result is a :class:`~chronologia.astrodate.DateSpan` whose width is the stated
accuracy and whose :attr:`~chronologia.astrodate.DateSpan.basis` records that
it is a reconstruction from theory rather than an observation.

**Sources (downloaded, cited)**, mirrored into ``papers/standards/`` (see that
directory's ``INDEX.md``):

* ``meeus_equinox_solstice_astroalgorithms4python.py`` -- Jean Meeus,
  *Astronomical Algorithms* (2nd ed., 1998, Willmann-Bell), chapter 27
  "Equinoxes and Solstices", reproduced verbatim in the open-source
  AstroAlgorithms4Python ``equinox.py``.  Carries the full coefficient set
  transcribed below: the JDE0 mean-equinox polynomial for the ``+1000..+3000``
  range (table 27.B, all four cardinal events, ``Y=(year-2000)/1000``), the
  24-row periodic-terms table (27.C: :data:`_TERMS`), and the correction
  ``W = 35999.373*T - 2.47`` deg with
  ``dl = 1 + 0.0334*cos W + 0.0007*cos 2W`` and
  ``JDE = JDE0 + 0.00001*S/dl`` where ``S`` sums the periodic terms.
* ``meeus_equinox_solstice_stellafane.html`` -- Stellafane "Equinox & Solstice
  Calculator", which implements the same method and states the accuracy
  verbatim: **"error is less than one minute for the years 1951-2050"**, valid
  year range **1000 to 3000**, output in **TDT** (Terrestrial Dynamical Time
  ~ TT).  That one-minute figure is :data:`EQUINOX_ACCURACY`; the 1000..3000
  range is :data:`VALID_YEAR_RANGE` (a ``ValueError`` outside it, since the
  27.B polynomial is not fitted there and no 27.A table is transcribed here).
* ``equinoxes_solstices_2001-2100_astropixels.html`` -- Fred Espenak /
  AstroPixels published Universal-Time equinox/solstice table, the gold set
  cross-checked in ``test/test_equinoxes.py``.

**Accuracy -- equinoxes/solstices.**  :data:`EQUINOX_ACCURACY` == 1 minute
(Meeus/Stellafane's stated bound over 1951-2050; it degrades gently toward the
1000..3000 range edges but stays close to a minute, hence the single stated
bound over the whole valid range).

**Accuracy -- solar terms.**  The intermediate 15-degree crossings are NOT
covered by the 27.B cardinal-point polynomial; they are found instead by
inverting Meeus's *low-accuracy* Sun longitude (chapter 25 -- mean longitude
plus the equation of the centre, :func:`_sun_apparent_longitude`), which Meeus
states is good to about ``0.01`` degrees.  At the Sun's ~``0.9856`` deg/day
mean rate that is ~15 minutes of time; adding the nutation term this module
omits (~``0.004`` deg ~ 6 min) and mean-element slack, :data:`SOLAR_TERM_ACCURACY`
is set to **30 minutes** -- honestly wider than the cardinal equinoxes.  This
is the class-B improvement path for the Chinese-calendar family: it gives the
*jieqi* to the half-minute-of-arc, but it **does not upgrade the Chinese
calendar itself** (:mod:`chronologia.calendars`), whose tabulated
month/leap-month structure stays authoritative -- a mean-longitude term instant
is not a substitute for the table's true-longitude astronomical basis.

**TT -> UTC.**  Meeus's result is in TT (dynamical time).  Where the
leap-second table applies (1972 onward, :mod:`chronologia.leapseconds`) the
instant is converted to civil UTC via :func:`~chronologia.leapseconds.tt_to_utc`
(``TT - UTC = utc_tai_offset + 32.184 s``, and beyond the table's confirmed
horizon the last offset is held constant -- the leapseconds module's own
documented predicted basis).  **Before 1972** the leap-second machinery is out
of scope (fractional "rubber seconds"), so the TT instant is returned
unconverted and labelled as such; the residual ``TT - UTC`` there is bounded by
Delta-T, well under the seasonal spacing this module reports and far under a
day.

**Basis.**  Every returned :class:`~chronologia.astrodate.DateSpan` carries
``basis="reconstructed"`` -- the same peer basis :mod:`chronologia.moon` uses
for an already-modelled instant, chosen here for the same reason: these are
closed-form arithmetic reconstructions of an astronomical truth from mean
orbital theory.  Unlike :func:`chronologia.moon.next_phase`, these functions
take a *year*, not a caller "now" anchor, so there is no past/future instant to
split ``reconstructed`` from ``predicted`` on; the two are lattice peers of
equal rank (:func:`~chronologia.astrodate.combine_basis`), so the single
``reconstructed`` label composes identically either way.

**Meteorological vs astronomical seasons.**  :func:`astronomical_season_span`
returns the equinox-to-solstice spans -- the astronomical convention.  This is
deliberately the *alternative* to the meteorological seasons used elsewhere
(fixed three-month blocks starting on the first of March/June/September/
December, convenient for climate statistics).  Both conventions are in common
use; the astronomical one ties each season to a real solar event, the
meteorological one to whole calendar months.  See ``docs/sun-moon-and-seasons.md``.
"""
from __future__ import annotations

import math
from datetime import date, datetime, timedelta
from typing import Tuple, Union

from chronologia.astrodate import (BASIS_RECONSTRUCTED, AstroDate, DateSpan)
from chronologia.leapseconds import tt_to_utc

#: Meeus/Stellafane stated accuracy of the ch.27 cardinal-event method:
#: "error is less than one minute for the years 1951-2050" (mirrored source),
#: degrading gently toward the valid-range edges.
EQUINOX_ACCURACY = timedelta(minutes=1)

#: Accuracy of the 24 solar terms: the ch.25 low-accuracy Sun longitude Meeus
#: states as good to ~0.01 deg (~15 min at the Sun's mean rate), widened for
#: the omitted nutation term (~6 min) and mean-element slack.  Wider than
#: :data:`EQUINOX_ACCURACY` by construction -- see the module docstring.
SOLAR_TERM_ACCURACY = timedelta(minutes=30)

#: Inclusive year range over which the transcribed 27.B polynomial is valid
#: (Meeus/Stellafane).  Outside it these functions raise ``ValueError`` -- the
#: -1000..+1000 table (27.A) is not transcribed here.
VALID_YEAR_RANGE = (1000, 3000)

#: Julian Day of the J2000.0 epoch (2000-01-01 12:00 TT).
_J2000 = 2451545.0
_JULIAN_CENTURY_DAYS = 36525.0
_US_PER_DAY = 86_400_000_000
#: Leap-second table floor: below this year TT->UTC is out of scope.
_LEAPSECOND_FLOOR_YEAR = 1972

#: The recognised cardinal events and their table-27.B JDE0 polynomials,
#: ``JDE0 = a0 + a1*Y + a2*Y^2 + a3*Y^3 + a4*Y^4`` with ``Y=(year-2000)/1000``
#: (Meeus ch.27, transcribed from the mirrored source, verbatim).
_JDE0_COEFFS = {
    "march":     (2451623.80984, 365242.37404,  0.05169, -0.00411, -0.00057),
    "june":      (2451716.56767, 365241.62603,  0.00325,  0.00888, -0.00030),
    "september": (2451810.21715, 365242.01767, -0.11575,  0.00337,  0.00078),
    "december":  (2451900.05952, 365242.74049, -0.06223, -0.00823,  0.00032),
}

#: Table 27.C periodic terms: 24 rows of ``(A, B, C)`` for the correction
#: ``S = sum A*cos(B + C*T)`` (T in Julian centuries), transcribed verbatim.
_TERMS: Tuple[Tuple[float, float, float], ...] = (
    (485, 324.96,   1934.136), (203, 337.23,  32964.467),
    (199, 342.08,     20.186), (182,  27.85, 445267.112),
    (156,  73.14,  45036.886), (136, 171.52,  22518.443),
    ( 77, 222.54,  65928.934), ( 74, 296.72,   3034.906),
    ( 70, 243.58,   9037.513), ( 58, 119.81,  33718.147),
    ( 52, 297.17,    150.678), ( 50,  21.02,   2281.226),
    ( 45, 247.54,  29929.562), ( 44, 325.15,  31555.956),
    ( 29,  60.93,   4443.417), ( 18, 155.12,  67555.328),
    ( 17, 288.79,   4562.452), ( 16, 198.04,  62894.029),
    ( 14, 199.76,  31436.921), ( 12,  95.39,  14577.848),
    ( 12, 287.11,  31931.756), ( 12, 320.81,  34777.259),
    (  9, 227.73,   1222.114), (  8,  15.45,  16859.074),
)

#: The 24 solar terms (jieqi) in the conventional order beginning at *lichun*,
#: pinyin names, each at ecliptic longitude ``(315 + 15*index) % 360`` degrees
#: (Wikipedia, "Solar term"; chunfen == the March-equinox longitude 0 deg).
SOLAR_TERM_NAMES: Tuple[str, ...] = (
    "lichun", "yushui", "jingzhe", "chunfen", "qingming", "guyu",
    "lixia", "xiaoman", "mangzhong", "xiazhi", "xiaoshu", "dashu",
    "liqiu", "chushu", "bailu", "qiufen", "hanlu", "shuangjiang",
    "lidong", "xiaoxue", "daxue", "dongzhi", "xiaohan", "dahan",
)
_TERM_INDEX = {name: i for i, name in enumerate(SOLAR_TERM_NAMES)}


def _term_longitude(index: int) -> float:
    """Ecliptic longitude (degrees) of solar term ``index`` (0 == lichun)."""
    return (315.0 + 15.0 * index) % 360.0


# -- Meeus ch.27: cardinal equinox/solstice instants ---------------------

def _check_year(year: int) -> None:
    lo, hi = VALID_YEAR_RANGE
    if not lo <= year <= hi:
        raise ValueError(
            f"year {year} is outside the valid range {lo}..{hi} for the "
            "transcribed Meeus table 27.B; the -1000..+1000 table (27.A) is "
            "not available in chronologia.equinoxes")


def _jde0(year: int, which: str) -> float:
    try:
        a0, a1, a2, a3, a4 = _JDE0_COEFFS[which]
    except KeyError:
        raise ValueError(
            f"unknown event {which!r}; expected one of "
            f"{sorted(_JDE0_COEFFS)}") from None
    y = (year - 2000) / 1000.0
    return a0 + a1 * y + a2 * y ** 2 + a3 * y ** 3 + a4 * y ** 4


def _periodic_correction(jde0: float) -> float:
    """Apply the 27.C periodic terms + Delta-lambda correction to ``jde0``."""
    t = (jde0 - _J2000) / _JULIAN_CENTURY_DAYS
    w = math.radians(35999.373 * t - 2.47)
    dl = 1.0 + 0.0334 * math.cos(w) + 0.0007 * math.cos(2.0 * w)
    s = sum(a * math.cos(math.radians(b + c * t)) for a, b, c in _TERMS)
    return jde0 + 0.00001 * s / dl


def _jd_to_astrodate(jd: float) -> AstroDate:
    """Julian Day (TT) to a naive :class:`AstroDate` (Meeus ch.7, Gregorian)."""
    jd += 0.5
    z = math.floor(jd)
    f = jd - z
    if z < 2299161:
        a = z
    else:
        alpha = math.floor((z - 1867216.25) / 36524.25)
        a = z + 1 + alpha - math.floor(alpha / 4)
    b = a + 1524
    c = math.floor((b - 122.1) / 365.25)
    d = math.floor(365.25 * c)
    e = math.floor((b - d) / 30.6001)
    day = b - d - math.floor(30.6001 * e) + f
    day_int = int(math.floor(day))
    day_frac = day - day_int
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715
    base = AstroDate(int(year), int(month), day_int)
    return base + timedelta(microseconds=round(day_frac * _US_PER_DAY))


def _cal_to_jd(year: int, month: int, day: float) -> float:
    """Gregorian calendar (day may be fractional) to Julian Day (Meeus ch.7)."""
    if month <= 2:
        year -= 1
        month += 12
    a = year // 100
    b = 2 - a + a // 4
    return (math.floor(365.25 * (year + 4716))
            + math.floor(30.6001 * (month + 1)) + day + b - 1524.5)


def _tt_to_civil(tt: AstroDate) -> AstroDate:
    """TT :class:`AstroDate` to civil UTC where leap seconds apply, else TT.

    From 1972 on the leap-second table converts TT->UTC exactly (beyond its
    horizon it holds the last offset, its own predicted basis).  Before 1972
    the table is out of scope, so the TT instant is returned unconverted (see
    the module docstring's TT->UTC note).
    """
    if tt.year < _LEAPSECOND_FLOOR_YEAR:
        return tt
    return tt_to_utc(tt)


def _cardinal_instant(year: int, which: str) -> AstroDate:
    _check_year(year)
    jde = _periodic_correction(_jde0(year, which))
    return _tt_to_civil(_jd_to_astrodate(jde))


def _span(instant: AstroDate, accuracy: timedelta) -> DateSpan:
    return DateSpan(instant - accuracy, instant + accuracy,
                    basis=BASIS_RECONSTRUCTED)


def equinox(year: int, which: str = "march") -> DateSpan:
    """The equinox or solstice of ``year`` named by ``which``.

    ``which`` is one of ``"march"`` (northward/vernal equinox), ``"june"``
    (northern summer solstice), ``"september"`` (southward equinox) or
    ``"december"`` (northern winter solstice).  Returns a
    :class:`~chronologia.astrodate.DateSpan` of width
    ``2 * EQUINOX_ACCURACY`` centred on the Meeus ch.27 instant, in civil UTC
    (TT before 1972; see the module docstring), ``basis="reconstructed"``.

    >>> from chronologia.equinoxes import equinox
    >>> sp = equinox(2024, "march")
    >>> sp.start.year, sp.start.month, sp.start.day
    (2024, 3, 20)

    :raises ValueError: ``which`` is not a recognised event, or ``year`` is
        outside :data:`VALID_YEAR_RANGE`.
    """
    if which not in _JDE0_COEFFS:
        raise ValueError(
            f"unknown event {which!r}; expected one of "
            f"{sorted(_JDE0_COEFFS)}")
    return _span(_cardinal_instant(year, which), EQUINOX_ACCURACY)


#: (start event, end event, +year offset applied to the end event) for each
#: astronomical season, per hemisphere.  Southern seasons are the northern
#: ones shifted half a year (the same solar event opens autumn in the south
#: that opens spring in the north).
_SEASON_SPANS = {
    "north": {
        "spring": ("march", "june", 0),
        "summer": ("june", "september", 0),
        "autumn": ("september", "december", 0),
        "winter": ("december", "march", 1),
    },
    "south": {
        "autumn": ("march", "june", 0),
        "winter": ("june", "september", 0),
        "spring": ("september", "december", 0),
        "summer": ("december", "march", 1),
    },
}
#: ``fall`` is accepted as a synonym for ``autumn``.
_SEASON_ALIASES = {"fall": "autumn"}


def astronomical_season_span(year: int, season: str,
                             hemisphere: str = "north") -> DateSpan:
    """The astronomical (equinox-to-solstice) span of ``season`` in ``year``.

    ``season`` is ``"spring"``, ``"summer"``, ``"autumn"`` (or ``"fall"``) or
    ``"winter"``; ``hemisphere`` is ``"north"`` or ``"south"``.  The span runs
    from the opening solar event to the next one -- e.g. northern spring is the
    March equinox to the June solstice; northern winter runs from the December
    solstice of ``year`` to the March equinox of ``year + 1``.  In the southern
    hemisphere the same solar events open the opposite seasons (the March
    equinox opens *autumn* in the south).  ``basis="reconstructed"``.

    This is the **astronomical** season convention, the alternative to the
    **meteorological** seasons (fixed three-month blocks from the first of
    March/June/September/December) used for climate statistics -- both are in
    common use; see ``docs/sun-moon-and-seasons.md``.

    >>> from chronologia.equinoxes import astronomical_season_span
    >>> sp = astronomical_season_span(2024, "spring")
    >>> sp.start.month, sp.end.month
    (3, 6)

    :raises ValueError: unknown ``season`` or ``hemisphere``, or a ``year``
        (or ``year + 1`` for winter/summer) outside :data:`VALID_YEAR_RANGE`.
    """
    if hemisphere not in _SEASON_SPANS:
        raise ValueError(
            f"unknown hemisphere {hemisphere!r}; expected 'north' or 'south'")
    key = _SEASON_ALIASES.get(season, season)
    table = _SEASON_SPANS[hemisphere]
    if key not in table:
        raise ValueError(
            f"unknown season {season!r}; expected one of "
            "'spring', 'summer', 'autumn'/'fall', 'winter'")
    start_which, end_which, end_offset = table[key]
    start = _cardinal_instant(year, start_which)
    end = _cardinal_instant(year + end_offset, end_which)
    return DateSpan(start, end, basis=BASIS_RECONSTRUCTED)


# -- Meeus ch.25: solar-term instants via Sun-longitude inversion --------

def _sun_apparent_longitude(t: float) -> float:
    """Sun's apparent ecliptic longitude (deg, 0..360) at TT centuries ``t``.

    Meeus ch.25 low-accuracy formula: mean longitude + equation of the centre,
    minus the constant aberration ``0.00569`` deg (nutation omitted -- see the
    module docstring's accuracy note).
    """
    l0 = 280.46646 + 36000.76983 * t + 0.0003032 * t * t
    m = math.radians(357.52911 + 35999.05029 * t - 0.0001537 * t * t)
    c = ((1.914602 - 0.004817 * t - 0.000014 * t * t) * math.sin(m)
         + (0.019993 - 0.000101 * t) * math.sin(2 * m)
         + 0.000289 * math.sin(3 * m))
    return (l0 + c - 0.00569) % 360.0


def _solar_term_instant(year: int, index: int) -> AstroDate:
    _check_year(year)
    target = _term_longitude(index)
    # First guess: day-of-year where the Sun reaches `target`.  The March
    # equinox (longitude 0) falls near day 79.5; the Sun gains ~0.98565 deg/day.
    doy = (79.5 + target / 0.98565) % 365.2422
    jd = _cal_to_jd(year, 1, 1.0) + doy
    t = (jd - _J2000) / _JULIAN_CENTURY_DAYS
    for _ in range(8):
        lam = _sun_apparent_longitude(t)
        diff = (target - lam + 180.0) % 360.0 - 180.0  # into [-180, 180)
        if abs(diff) < 1e-9:
            break
        t += diff / 36000.769  # dlambda/dt ~ 36000.77 deg per century
    jde = t * _JULIAN_CENTURY_DAYS + _J2000
    return _tt_to_civil(_jd_to_astrodate(jde))


def solar_term(year: int, index_or_name: Union[int, str]) -> DateSpan:
    """The instant of one of the 24 solar terms (jieqi) in ``year``.

    ``index_or_name`` is either an integer ``0..23`` or a pinyin name from
    :data:`SOLAR_TERM_NAMES` (index 0 == ``"lichun"``, longitude 315 deg,
    early February; index 3 == ``"chunfen"``, the March equinox at longitude
    0 deg).  Returns a :class:`~chronologia.astrodate.DateSpan` of width
    ``2 * SOLAR_TERM_ACCURACY`` centred on the mean-longitude instant, in
    civil UTC (TT before 1972), ``basis="reconstructed"``.

    Found by inverting Meeus's low-accuracy Sun longitude, so this is the
    class-B improvement path for the Chinese-calendar family -- accurate to
    :data:`SOLAR_TERM_ACCURACY`, deliberately wider than the cardinal
    equinoxes.  It **does not** upgrade :mod:`chronologia.calendars`'s Chinese
    calendar, whose tabulated structure stays authoritative (module docstring).

    >>> from chronologia.equinoxes import solar_term
    >>> lichun = solar_term(2024, "lichun")
    >>> lichun.start.month
    2

    :raises ValueError: ``index_or_name`` names no term, or the integer index
        is outside ``0..23``, or ``year`` is outside :data:`VALID_YEAR_RANGE`.
    :raises TypeError: ``index_or_name`` is neither an int nor a str.
    """
    if isinstance(index_or_name, bool) or not isinstance(
            index_or_name, (int, str)):
        raise TypeError(
            "index_or_name must be an int 0..23 or a solar-term name, got "
            f"{type(index_or_name).__name__}")
    if isinstance(index_or_name, str):
        try:
            index = _TERM_INDEX[index_or_name]
        except KeyError:
            raise ValueError(
                f"unknown solar term {index_or_name!r}; expected one of "
                f"{list(SOLAR_TERM_NAMES)}") from None
    else:
        index = index_or_name
        if not 0 <= index <= 23:
            raise ValueError(
                f"solar-term index {index} out of range 0..23")
    return _span(_solar_term_instant(year, index), SOLAR_TERM_ACCURACY)
