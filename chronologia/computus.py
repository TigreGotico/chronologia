"""Computus: the date of Easter and the movable feasts reckoned from it.

Easter is the great *movable* feast: it is not a fixed calendar date but a
rule — the first Sunday after the first ecclesiastical full moon on or after
the (fixed) 21 March equinox.  Crucially the "full moon" here is **not** an
astronomical observation; it is a value read from a codified arithmetic lunar
table (the epact / golden-number cycle), so the whole computation is exact
integer arithmetic on a calendar, not ephemeris astronomy.  This module is
therefore class A (exact) rather than the mean-arithmetic class of
:mod:`chronologia.moon`: given a year it returns a *definite* date, no
accuracy bound.

East and West disagree for two independent reasons, and this module keeps
both: the West computes the rule on the **Gregorian** calendar with the
Gregorian lunar correction, while most of the Orthodox East still computes it
on the **Julian** calendar with the older Julian lunar table.  The two
calendars have drifted 13 days apart, and the two lunar tables differ as well,
so the Julian Easter usually falls one to five weeks after the Gregorian one —
occasionally they coincide (2025 is such a year).

**Sources (downloaded, cited)**, mirrored into ``papers/standards/`` (see that
directory's ``INDEX.md``):

* ``computus_wikipedia.html`` (Wikipedia, "Computus"; ``Date_of_Easter``
  redirects here) — carries the two formulations transcribed below verbatim:
  the **"Anonymous Gregorian algorithm"** (also called the Meeus/Jones/Butcher
  algorithm, given by Jean Meeus in *Astronomical Algorithms* and traceable to
  a correspondent of *Nature*, 1876), which yields the Gregorian-calendar month
  and day of Western Easter; and **"Meeus's Julian algorithm"** (Meeus,
  *Astronomical Algorithms*), which yields the **Julian**-calendar month and
  day of Orthodox Easter.  Both are pure integer arithmetic.
* ``moveable_feast_wikipedia.html`` (Wikipedia, "Moveable feast") and
  ``liturgical_year_wikipedia.html`` (Wikipedia, "Liturgical year") — the
  liturgical-calendar references for the day-offsets of the feasts computed
  from Easter (Ash Wednesday "46 days before Easter", Ascension "40 days after"
  i.e. the 39-day offset counting Easter as day 0, Pentecost the seventh Sunday
  after Easter, etc.) and for the fixed solar feasts (Christmas 25 December,
  Epiphany 6 January, Assumption 15 August, All Saints 1 November).

**The three Easter renderings.**  :func:`easter` takes a ``method``:

* ``"gregorian"`` — Western Easter as a **proleptic-Gregorian instant**
  (:class:`AstroDate`).  The algorithm's output *is* a Gregorian date, so the
  fields are used directly; this is a real Sunday.
* ``"julian"`` — Orthodox Easter carrying its **own Julian-calendar label**:
  the ``month``/``day`` fields hold the Julian-calendar numbers straight from
  Meeus's Julian algorithm.  This is the date "in the Julian calendar" — the
  form an Orthodox almanac prints as *the* Paschal date.  Because those numbers
  are stuffed into an :class:`AstroDate` (which is otherwise proleptic
  Gregorian), the result is a **label, not the civil instant**: do not read its
  ``weekday()`` as a civil Sunday, and do not do day arithmetic on it directly.
  To recover the instant, feed it back through the Julian calendar, which is
  exactly what the next option does.
* ``"julian_gregorian_date"`` — the Orthodox-practice convenience: the same
  Julian Easter **rendered in the Gregorian civil calendar** (Julian label →
  JDN → Gregorian).  This is the day Orthodox Christians actually mark on a
  civil wall calendar, and it is a real Sunday instant.  For 2024 the ``julian``
  label is 22 April (Julian) and this rendering is 5 May (Gregorian).

The movable feasts (:func:`movable_feast`) are always offset from the **real
Sunday instant**, so for the Orthodox methods they are reckoned from the
``julian_gregorian_date`` rendering and returned as civil Gregorian instants.
"""
from __future__ import annotations

from datetime import timedelta
from typing import Dict, Tuple

from chronologia.astrodate import AstroDate

#: The accepted ``method`` values of :func:`easter` (see the module docstring).
EASTER_METHODS = ("gregorian", "julian", "julian_gregorian_date")

#: Movable feast -> day offset from Easter Sunday (Easter itself is day 0).
#: Cited from ``moveable_feast_wikipedia.html`` / ``liturgical_year_wikipedia.html``:
#: Ash Wednesday 46 days before Easter (-46); Palm Sunday the Sunday before
#: Easter (-7); Good Friday the Friday before (-2); Ascension the 40th day of
#: Eastertide counting Easter as day 1, i.e. +39; Pentecost the seventh Sunday
#: after Easter, +49; Trinity Sunday the Sunday after Pentecost, +56; Corpus
#: Christi the Thursday after Trinity Sunday, +60.
MOVABLE_FEAST_OFFSETS: Dict[str, int] = {
    "ash_wednesday": -46,
    "palm_sunday": -7,
    "good_friday": -2,
    "ascension": 39,
    "pentecost": 49,
    "trinity_sunday": 56,
    "corpus_christi": 60,
}

#: Fixed (solar) feast -> ``(month, day)``, cited from
#: ``liturgical_year_wikipedia.html``: Christmas 25 December, Epiphany
#: 6 January, Assumption 15 August, All Saints' Day 1 November.  These do not
#: move with Easter; :func:`fixed_feast` simply stamps them onto a year.
FIXED_FEASTS: Dict[str, Tuple[int, int]] = {
    "christmas": (12, 25),
    "epiphany": (1, 6),
    "assumption": (8, 15),
    "all_saints": (11, 1),
}


def _gregorian_easter(year: int) -> Tuple[int, int]:
    """``(month, day)`` of Western Easter on the Gregorian calendar.

    The Anonymous Gregorian algorithm (Meeus/Jones/Butcher), transcribed
    verbatim from ``computus_wikipedia.html``.  Pure integer arithmetic.
    """
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    ell = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * ell) // 451
    month = (h + ell - 7 * m + 114) // 31
    day = ((h + ell - 7 * m + 114) % 31) + 1
    return month, day


def _julian_easter_label(year: int) -> Tuple[int, int]:
    """``(month, day)`` of Orthodox Easter **on the Julian calendar**.

    Meeus's Julian algorithm, transcribed verbatim from
    ``computus_wikipedia.html``.  The result is a Julian-calendar date; convert
    it through :func:`~chronologia.calendars.julian_to_jdn` to reach the civil
    (Gregorian) instant.
    """
    a = year % 4
    b = year % 7
    c = year % 19
    d = (19 * c + 15) % 30
    e = (2 * a + 4 * b - d + 34) % 7
    month = (d + e + 114) // 31
    day = ((d + e + 114) % 31) + 1
    return month, day


def _validate_method(method: str) -> None:
    if method not in EASTER_METHODS:
        raise ValueError(
            f"unknown Easter method {method!r}; expected one of "
            f"{list(EASTER_METHODS)}")


def easter(year: int, method: str = "gregorian") -> AstroDate:
    """The date of Easter Sunday in ``year``, as an :class:`AstroDate`.

    ``method`` selects the rendering (see the module docstring for the full
    distinction):

    * ``"gregorian"`` (default) — Western Easter, a real proleptic-Gregorian
      Sunday instant.
    * ``"julian"`` — Orthodox Easter carrying its **own Julian-calendar
      label** in the ``month``/``day`` fields; a label, not the civil instant,
      so ``.weekday()`` is not a civil Sunday.  Recover the instant with
      ``AstroDate.from_calendar("julian", year, month, day)`` — which is what
      ``"julian_gregorian_date"`` returns.
    * ``"julian_gregorian_date"`` — the same Orthodox Easter **rendered in the
      Gregorian civil calendar**; a real Sunday instant (the day marked on a
      civil calendar in Orthodox practice).

    For ``year < 1583`` the ``"gregorian"`` method is **proleptic**: the
    Gregorian calendar did not yet exist, so the value is the rule applied
    backwards, not a date anyone historically observed.  The arithmetic is
    exact for every integer year (no accuracy bound); it is the *meaning* of a
    pre-1583 Gregorian Easter that is conventional.

    :raises ValueError: ``method`` is not one of :data:`EASTER_METHODS`.
    """
    _validate_method(method)
    if method == "gregorian":
        month, day = _gregorian_easter(year)
        return AstroDate(year, month, day)
    month, day = _julian_easter_label(year)
    if method == "julian":
        return AstroDate(year, month, day)
    # julian_gregorian_date: render the Julian label in the civil calendar.
    return AstroDate.from_calendar("julian", year, month, day)


def _easter_instant(year: int, method: str) -> AstroDate:
    """The real proleptic-Gregorian Sunday instant of Easter for offsetting.

    ``"gregorian"`` uses the Gregorian instant; the two Orthodox methods both
    use the ``julian_gregorian_date`` civil instant (offsetting the raw Julian
    *label* would be meaningless).
    """
    _validate_method(method)
    if method == "gregorian":
        return easter(year, "gregorian")
    return easter(year, "julian_gregorian_date")


def movable_feast(name: str, year: int,
                  method: str = "gregorian") -> AstroDate:
    """A movable feast in ``year`` as a civil (proleptic-Gregorian) instant.

    ``name`` is one of :data:`MOVABLE_FEAST_OFFSETS` (``ash_wednesday``,
    ``palm_sunday``, ``good_friday``, ``ascension``, ``pentecost``,
    ``trinity_sunday``, ``corpus_christi``).  The feast is the cited whole-day
    offset from Easter Sunday, added on the real calendar, so the result is
    always an actual civil date — for the Orthodox methods it is reckoned from
    the ``julian_gregorian_date`` rendering of Easter, never from the raw
    Julian label.

    :raises ValueError: ``name`` is not a known movable feast, or ``method``
        is not one of :data:`EASTER_METHODS`.
    """
    if name not in MOVABLE_FEAST_OFFSETS:
        raise ValueError(
            f"unknown movable feast {name!r}; expected one of "
            f"{sorted(MOVABLE_FEAST_OFFSETS)}")
    return _easter_instant(year, method) + timedelta(
        days=MOVABLE_FEAST_OFFSETS[name])


def fixed_feast(name: str, year: int) -> AstroDate:
    """A fixed (solar) feast in ``year`` as a proleptic-Gregorian instant.

    ``name`` is one of :data:`FIXED_FEASTS` (``christmas``, ``epiphany``,
    ``assumption``, ``all_saints``).  These feasts sit on a fixed month and day
    every year and do not move with Easter.

    :raises ValueError: ``name`` is not a known fixed feast.
    """
    if name not in FIXED_FEASTS:
        raise ValueError(
            f"unknown fixed feast {name!r}; expected one of "
            f"{sorted(FIXED_FEASTS)}")
    month, day = FIXED_FEASTS[name]
    return AstroDate(year, month, day)


def advent_sunday(year: int) -> AstroDate:
    """Advent Sunday (the first Sunday of Advent) in ``year``.

    Advent Sunday is the fourth Sunday before Christmas Day — equivalently the
    Sunday falling between 27 November and 3 December inclusive (the Sunday
    nearest St Andrew's Day, 30 November).  It begins the Western liturgical
    year, so unlike the other feasts here it is defined by counting Sundays
    back from the *fixed* Christmas date rather than by an offset from Easter;
    this module computes it by finding the first Sunday on or after 27 November
    (``liturgical_year_wikipedia.html``).
    """
    anchor = AstroDate(year, 11, 27)
    # weekday(): Monday==0 .. Sunday==6; step forward to the next Sunday.
    return anchor + timedelta(days=(6 - anchor.weekday()) % 7)
