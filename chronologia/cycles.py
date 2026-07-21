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

* French Republican décade -- ``french_republican_reference.html`` (the
  30-day month divided into three ten-day décades, days primidi..décadi).
* Nundinal cycle -- ``roman_nundinal_cycle_reference.html`` (the ancient
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
from typing import Mapping, Optional

from chronologia.calendars import CALENDARS, gregorian_to_jdn

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
    # (french_republican_reference.html).
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
