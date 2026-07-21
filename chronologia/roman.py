"""Roman calendar day reckoning: Kalends, Nones and Ides.

The Romans named a day by *inclusive backward counting* from the next of
three monthly anchor days:

* **Kalends** (Kalendae) -- the 1st of the month;
* **Nones** (Nonae) -- the 5th, or the 7th in March, May, July, October;
* **Ides** (Idus) -- the 13th, or the 15th in those same four months.

"ante diem III Kalendas Aprilis" (a.d. III Kal. Apr.) is the 3rd day
before the Kalends of April counting inclusively: 1 April is day 1,
31 March day 2, 30 March day 3 -> 30 March.  "pridie" ("the day before")
is the count-2 case; the bare ablative ("Idibus Martiis", on the Ides) is
the anchor day itself (count 1).

The arithmetic is over the **Julian** calendar (the calendar actually in
use), through ``calendars.julian_to_jdn`` / ``jdn_to_julian``; the returned
``(year, month, day)`` is the Julian-calendar date, so 30 March reads as
month 3 day 30 -- the Roman date's own labels, not a Gregorian shift.

Source: ``roman_calendar_reckoning_reference.html``.
"""
from __future__ import annotations

from typing import Optional, Tuple

from chronologia.calendars import jdn_to_julian, julian_to_jdn

#: months whose Nones/Ides fall two days later (March, May, July, October).
_LATE_MONTHS = frozenset({3, 5, 7, 10})
ROMAN_ANCHORS = frozenset({"kalends", "nones", "ides"})


def _nones_day(month: int) -> int:
    return 7 if month in _LATE_MONTHS else 5


def _ides_day(month: int) -> int:
    return 15 if month in _LATE_MONTHS else 13


def _anchor_jdn(year: int, month: int, anchor: str) -> int:
    if anchor == "kalends":
        return julian_to_jdn(year, month, 1)
    if anchor == "nones":
        return julian_to_jdn(year, month, _nones_day(month))
    return julian_to_jdn(year, month, _ides_day(month))     # ides


def _previous_anchor_jdn(year: int, month: int, anchor: str) -> int:
    """JDN of the anchor immediately preceding ``anchor`` (the lower bound of
    the inclusive-backward span, exclusive)."""
    if anchor == "ides":
        return _anchor_jdn(year, month, "nones")
    if anchor == "nones":
        return _anchor_jdn(year, month, "kalends")
    # kalends: the previous anchor is the Ides of the previous month
    pm, py = (12, year - 1) if month == 1 else (month - 1, year)
    return _anchor_jdn(py, pm, "ides")


def roman_to_julian(year: int, month: int, anchor: str, count: int
                    ) -> Optional[Tuple[int, int, int]]:
    """Julian ``(year, month, day)`` named "a.d. ``count`` ``anchor`` of
    ``month``", or ``None`` when ``count`` overshoots the previous anchor.

    ``count`` is the inclusive backward ordinal (1 == the anchor day itself,
    2 == pridie).  ``month``/``year`` name the month the anchor belongs to;
    the resolved day may fall in the previous month (Kalends counting).
    """
    if count < 1:
        return None
    anchor_jdn = _anchor_jdn(year, month, anchor)
    prev_jdn = _previous_anchor_jdn(year, month, anchor)
    if count > anchor_jdn - prev_jdn:
        return None                     # past the previous anchor -> not valid
    return jdn_to_julian(anchor_jdn - (count - 1))
