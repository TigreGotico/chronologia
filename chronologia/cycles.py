"""Named day cycles: the generalisation of the seven-day week.

A :class:`DayCycle` is a repeating labelled sequence of days declared
against a calendar.  The Gregorian seven-day week is the canonical
instance -- ``weekday_ref`` in the engine is exactly a query over this
cycle -- but the same machinery expresses any fixed cycle: the French
Republican *décade* (ten days, anchored inside each 30-day month) and the
Roman *nundinal* market cycle (eight days, free-running) are registered
here as further instances.

Two ``kind`` s cover the space:

* ``free_running`` -- the cycle never resets; a day's position is
  ``(jdn - anchor_jdn) % length``.  The seven-day week and the nundinal
  cycle are free-running.
* ``month_anchored`` -- the cycle restarts at the first of every calendar
  month; a day's position is ``(day_of_month - 1) % length`` on the named
  calendar.  The Republican décade is month-anchored (three décades fill
  each 30-day month).

Sources (downloaded, cited):

* French Republican décade -- Wikipedia, "French Republican calendar" (the
  30-day month divided into three ten-day décades, days primidi..décadi).
* Nundinal cycle -- Wikipedia, "Nundinal cycle" (the ancient
  eight-day market cycle, free-running and continuous).  Its *length* and
  free-running character are historically grounded; the absolute *phase*
  (which JDN carries letter A) was already uncertain in antiquity, so the
  ``anchor_jdn`` here is a conventional reference, not a claim about a
  specific attested market day -- the mechanism, not the epoch, is what
  this instance demonstrates.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import TYPE_CHECKING, List, Mapping, Optional, Tuple, Union

from chronologia.calendars import CALENDARS, gregorian_to_jdn, jdn_to_gregorian

if TYPE_CHECKING:
    from chronologia.astrodate import AstroDate

#: microseconds in a civil day -- the exact hub every subdivision rescales to.
US_PER_DAY = 86_400 * 1_000_000

# JDN of proleptic Gregorian 0001-01-01, a Monday: the seven-day week's
# free-running anchor, so position 0 == Monday == weekday index 0.
_MONDAY_ANCHOR_JDN = gregorian_to_jdn(1, 1, 1)


@dataclass(frozen=True)
class DayCycle:
    """A repeating labelled sequence of days.

    ``anchor_jdn`` is the JDN carrying position 0 for a ``free_running``
    cycle (ignored for ``month_anchored``); ``calendar`` names the calendar
    whose months a ``month_anchored`` cycle restarts on.
    """
    name: str
    length: int
    kind: str                       # "free_running" | "month_anchored"
    anchor_jdn: int = 0
    calendar: Optional[str] = None

    def position(self, jdn: int) -> int:
        """The 0-based position of ``jdn`` within this cycle."""
        if self.kind == "free_running":
            return (jdn - self.anchor_jdn) % self.length
        assert self.calendar is not None  # month_anchored always names one
        cal = CALENDARS[self.calendar]
        day_of_month = cal.from_jdn(jdn)[2]
        return (day_of_month - 1) % self.length


#: Registered day cycles, keyed by the name the ``cycle_<key>_<n>.voc``
#: filename convention binds vocabulary to.
DAY_CYCLES = {
    # the canonical instance: the Gregorian seven-day week (Mon=0..Sun=6),
    # the same cycle weekday_ref resolves against.
    "week": DayCycle("week", 7, "free_running", _MONDAY_ANCHOR_JDN),
    # French Republican décade: ten days, restarting each 30-day month.
    "republican_decade": DayCycle("republican_decade", 10, "month_anchored",
                                  calendar="french_republican"),
    # Roman nundinal cycle: eight days, free-running (phase conventional).
    "nundinal": DayCycle("nundinal", 8, "free_running", _MONDAY_ANCHOR_JDN),
}


# --------------------------------------------------------------------------
# Day subdivisions: alternative divisions of the civil day into fixed units.
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class DaySubdivision:
    """A division of one civil day into fixed units, each an exact fraction
    of the day.

    French decimal time divides the day into 10 decimal hours, each 100
    decimal minutes, each 100 decimal seconds; so a decimal hour is exactly
    1/10 of a day (2.4 civil hours) and "5 decimal hours" is exactly noon.
    ``Fraction`` keeps the rescaling exact to the civil microsecond.
    """
    name: str
    fractions: Mapping[str, Fraction]       # unit -> fraction of one day

    def units_to_us(self, hours=0, minutes=0, seconds=0) -> int:
        """Civil microseconds since midnight for a subdivision reading."""
        frac = (hours * self.fractions["hour"]
                + minutes * self.fractions.get("minute", Fraction(0))
                + seconds * self.fractions.get("second", Fraction(0)))
        return int(frac * US_PER_DAY)       # exact for the tabled fractions

    def unit_width_us(self, unit: str) -> int:
        """Civil microseconds spanned by one of ``unit`` (its referential width)."""
        return int(self.fractions[unit] * US_PER_DAY)


#: Registered day subdivisions, keyed by the ``day_subdivision`` lang.json fact.
DAY_SUBDIVISIONS = {
    # French Republican decimal time (décret of 1793): 10 decimal hours per
    # day, 100 decimal minutes per hour, 100 decimal seconds per minute
    # (Wikipedia, "French Republican calendar").
    "french_decimal": DaySubdivision("french_decimal", {
        "hour": Fraction(1, 10),
        "minute": Fraction(1, 1000),
        "second": Fraction(1, 100000),
    }),
}


def resolve_cycle_day(cycle: DayCycle, position: int, rel: int,
                      anchor_jdn: int) -> Optional[int]:
    """JDN of the day at ``position`` in ``cycle`` relative to ``anchor_jdn``.

    ``rel`` follows the weekday convention: ``+1`` the next such day strictly
    ahead, ``-1`` the most recent one strictly behind, ``0`` the one in the
    current cycle window (the reproduction of weekday_ref's next/last/this).
    Returns ``None`` when a month-anchored target falls outside its month
    (an intercalary-boundary discontinuity).
    """
    length = cycle.length
    cur = cycle.position(anchor_jdn)
    if rel > 0:
        delta = (position - cur) % length or length
    elif rel < 0:
        delta = -((cur - position) % length or length)
    else:
        delta = position - cur
    target = anchor_jdn + delta
    if cycle.position(target) != position:
        return None                 # month-anchored boundary discontinuity
    return target


# --------------------------------------------------------------------------
# Year cycles: cyclic *year* labels (the generalisation of DayCycle to
# years instead of days) -- the 60-term Chinese sexagenary cycle, the
# 12-term Chinese zodiac, and the 15-year Roman/Byzantine indiction.
# --------------------------------------------------------------------------
#
# Two anchoring flavours cover the space, mirroring DayCycle's two ``kind``s:
#
# * ``calendar_key`` set (sexagenary, chinese_zodiac) -- the cycle labels the
#   *native year* of a calendar registered in ``CALENDARS`` (here, the
#   Chinese lunisolar year).  ``anchor_year`` is that calendar's own year
#   number carrying ``names[0]``.  Resolving a Gregorian instant crosses
#   through the calendar's ``from_astro`` first, so the label flips at the
#   calendar's own year boundary (Chinese New Year), not at 1 January --
#   this is what makes 2024-01-15 (before CNY 2024-02-10) still a rabbit
#   year, where a naive ``gregorian_year % 12`` would get it wrong.
# * ``calendar_key`` is ``None`` (indiction) -- the cycle labels the plain
#   Gregorian year, but its year may start on a day other than 1 January;
#   ``year_start`` (month, day) names that start, mirroring
#   ``Era.year_start`` (the Byzantine Anno Mundi/indiction convention: the
#   administrative year begins 1 September).  A moment on/after
#   ``year_start`` belongs to the *following* Gregorian year's label.
#
# Sources (downloaded, cited):
#
# * Sexagenary cycle / Chinese zodiac -- the 10 Heavenly Stems (jia, yi,
#   bing, ding, wu, ji, geng, xin, ren, gui) x 12 Earthly Branches (zi, chou,
#   yin, mao, chen, si, wu, wei, shen, you, xu, hai) pairing, and the
#   correspondence "1984 began the present cycle (a jiazi year)" -- Wikipedia,
#   "Sexagenary cycle" (en.wikipedia.org/wiki/Sexagenary_cycle, retrieved
#   2026-07-21).  The animal-to-branch correspondence (zi=rat .. hai=pig) is
#   the standard Chinese zodiac ordering, same source family.  The label
#   applies to the *Chinese lunisolar year* (``CALENDARS["chinese"]``'s own
#   year number, itself the Gregorian year of the non-leap 1st Lunar Month
#   opening it -- see ``calendar_data/chinese.tab``), so it is bounded by
#   that table's coverage (lunar years 1901..2099).
# * Indiction -- the 15-year Roman/Byzantine tax cycle, introduced by
#   Constantine 1 September 312 and used until 1806; the Constantinopolitan
#   convention starts the indiction year 1 September (shifted there from
#   23 September in the later 5th century, probably 462 AD).  Formula:
#   for a Julian/Gregorian year Y, indiction = ``(Y + 2) mod 15 + 1`` for
#   January-August of Y; the indiction increments at 1 September, so
#   September-December of Y uses ``(Y + 3) mod 15 + 1`` (equivalently: run
#   the Jan-Aug formula on Y + 1).  Corroborated by two independent
#   worked-example sources: skypoint.com/members/waltzmn/MSDating.html
#   ("Indiction = (X+2) MOD 15 + 1 ... this only applies to the first eight
#   months of the year"; manuscript dated May [year] 6343) and Wikipedia,
#   "Indiction" (en.wikipedia.org/wiki/Indiction; "the indiction for the
#   year 2017 is 10: (2017 + 3) mod 15 = 10" -- the same identity, since
#   ``(Y+3) mod 15`` and ``(Y+2) mod 15 + 1`` agree except at the mod-15
#   remainder-zero edge, which the ``+1`` form resolves to 15 instead of 0).
#   Both retrieved 2026-07-21.

#: The 10 Heavenly Stems, pinyin, in their canonical cyclic order.
_HEAVENLY_STEMS = ("jia", "yi", "bing", "ding", "wu", "ji", "geng", "xin",
                   "ren", "gui")
#: The 12 Earthly Branches, pinyin, in their canonical cyclic order.
_EARTHLY_BRANCHES = ("zi", "chou", "yin", "mao", "chen", "si", "wu", "wei",
                     "shen", "you", "xu", "hai")
#: The 12 zodiac animals, in Earthly-Branch order (zi=rat .. hai=pig).
_ZODIAC_ANIMALS = ("rat", "ox", "tiger", "rabbit", "dragon", "snake",
                   "horse", "goat", "monkey", "rooster", "dog", "pig")

#: The 60 sexagenary names (stem-branch, hyphenated pinyin), generated from
#: the stem x branch pairing -- ``names[i]`` is stem ``i % 10`` paired with
#: branch ``i % 12`` for ``i`` in ``0..59``, e.g. ``names[0] == "jia-zi"``,
#: ``names[40] == "jia-chen"``, ``names[16] == "geng-chen"``.
_SEXAGENARY_NAMES = tuple(
    f"{_HEAVENLY_STEMS[i % 10]}-{_EARTHLY_BRANCHES[i % 12]}" for i in range(60))


@dataclass(frozen=True)
class YearCycle:
    """A repeating labelled sequence of *years* (the year-axis counterpart
    of :class:`DayCycle`).

    ``anchor_year`` is the native year (on ``calendar_key`` when set, else
    the plain Gregorian year) carrying ``names[0]``.  ``calendar_key`` names
    a :data:`~chronologia.calendars.CALENDARS` entry whose own year number
    the cycle labels (``None`` for a cycle that labels the Gregorian year
    itself).  ``year_start`` is the ``(month, day)`` a Gregorian-year-keyed
    cycle's year begins on when it is not 1 January (ignored when
    ``calendar_key`` is set, since the calendar's own year boundary applies
    instead).
    """
    key: str
    length: int
    names: Tuple[str, ...]
    anchor_year: int
    calendar_key: Optional[str]
    citation: str
    year_start: Tuple[int, int] = (1, 1)

    def native_year(self, moment) -> int:
        """The native year label ``moment`` falls in, on this cycle's axis."""
        if self.calendar_key is not None:
            cal = CALENDARS[self.calendar_key]
            return cal.from_astro(moment).year
        year = moment.year
        if (moment.month, moment.day) >= self.year_start:
            year += 1                   # past this Gregorian year's start day
        return year

    def position(self, native_year: int) -> int:
        """The 0-based position ``native_year`` occupies in this cycle."""
        return (native_year - self.anchor_year) % self.length

    def name_at(self, native_year: int) -> str:
        """The cycle name labelling ``native_year``."""
        return self.names[self.position(native_year)]

    def year_span(self, native_year: int) -> Tuple["AstroDate", "AstroDate"]:
        """Half-open ``[start, next-start)`` Gregorian-proleptic span of the
        cycle year labelled ``native_year``."""
        from chronologia.astrodate import AstroDate
        if self.calendar_key is not None:
            cal = CALENDARS[self.calendar_key]
            start = cal.date(native_year, 1, 1)
            end = cal.date(native_year + 1, 1, 1)
            return start, end
        sm, sd = self.year_start
        # native_year N covers [year_start of Gregorian year N-1 .. of N)
        # when year_start isn't 1 Jan (the label is assigned to the *later*
        # Gregorian year for the Sept-Dec tail, so the span starts a
        # Gregorian year earlier); plain 1-Jan-anchored cycles start at N.
        start_year = native_year - 1 if self.year_start != (1, 1) else native_year
        end_year = native_year if self.year_start != (1, 1) else native_year + 1
        start = AstroDate(*jdn_to_gregorian(gregorian_to_jdn(start_year, sm, sd)))
        end = AstroDate(*jdn_to_gregorian(gregorian_to_jdn(end_year, sm, sd)))
        return start, end


#: Registered year cycles, keyed by name.
YEAR_CYCLES = {
    # The 60-term Chinese sexagenary cycle (stem-branch), labelling the
    # Chinese lunisolar year; 1984 is jiazi (position 0).
    "sexagenary": YearCycle(
        "sexagenary", 60, _SEXAGENARY_NAMES, 1984, "chinese",
        "Wikipedia, \"Sexagenary cycle\" -- 1984 begins the current cycle "
        "(jiazi); stem x branch pairing, retrieved 2026-07-21."),
    # The 12-animal Chinese zodiac, labelling the Chinese lunisolar year;
    # 1984 is the rat (position 0), same anchoring as sexagenary.
    "chinese_zodiac": YearCycle(
        "chinese_zodiac", 12, _ZODIAC_ANIMALS, 1984, "chinese",
        "Wikipedia, \"Sexagenary cycle\" -- 1984 is a rat year; zi=rat.."
        "hai=pig branch-to-animal correspondence, retrieved 2026-07-21."),
    # The 15-year Roman/Byzantine indiction (Constantinopolitan convention:
    # administrative year begins 1 September).  names[i] == str(i+1);
    # anchor_year=13 makes position(Y) == (Y+2) mod 15, the cited formula.
    "indiction": YearCycle(
        "indiction", 15, tuple(str(n) for n in range(1, 16)), 13, None,
        "skypoint.com Dating Manuscripts (\"Indiction = (X+2) MOD 15 + 1\", "
        "first eight months only) and Wikipedia \"Indiction\" (\"(Y+3) mod "
        "15\" for 2017 = 10, the same identity); Constantinopolitan "
        "1-September year start; both retrieved 2026-07-21.",
        year_start=(9, 1)),
}


def year_cycle_label(moment, cycle: Union[str, YearCycle]) -> str:
    """The cycle name labelling ``moment`` (an ``AstroDate``/``date``/
    ``datetime``), e.g. ``year_cycle_label(AstroDate(2024, 6, 1),
    "chinese_zodiac") == "dragon"``.

    Raises :class:`KeyError` for an unknown ``cycle`` string, and propagates
    :class:`~chronologia.calendars.CalendarRangeError` when a calendar-backed
    cycle's moment falls outside its table (``sexagenary``/``chinese_zodiac``
    are bounded to Chinese lunisolar years 1901..2099).
    """
    if isinstance(cycle, str):
        if cycle not in YEAR_CYCLES:
            raise KeyError(f"unknown year cycle {cycle!r}; expected one of "
                           f"{sorted(YEAR_CYCLES)}")
        cycle = YEAR_CYCLES[cycle]
    return cycle.name_at(cycle.native_year(moment))


def years_of(cycle: Union[str, YearCycle], name: str, start: int, end: int
            ) -> List[Tuple["AstroDate", "AstroDate"]]:
    """The half-open ``[start, next-start)`` spans of every year named
    ``name`` in this cycle whose native year falls in ``start..end``
    inclusive (plain Gregorian-year integers), e.g. ``years_of(
    "chinese_zodiac", "dragon", 1990, 2025)`` lists 2000, 2012 and 2024.

    Raises :class:`ValueError` for a ``name`` this cycle does not carry.
    """
    if isinstance(cycle, str):
        if cycle not in YEAR_CYCLES:
            raise KeyError(f"unknown year cycle {cycle!r}; expected one of "
                           f"{sorted(YEAR_CYCLES)}")
        cycle = YEAR_CYCLES[cycle]
    if name not in cycle.names:
        raise ValueError(f"{cycle.key}: unknown name {name!r}; expected one "
                         f"of {cycle.names}")
    idx = cycle.names.index(name)
    return [cycle.year_span(native_year)
            for native_year in range(start, end + 1)
            if cycle.position(native_year) == idx]
