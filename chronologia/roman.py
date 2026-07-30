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

Source: Wikipedia, "Roman calendar" (day reckoning by Kalends, Nones and
Ides).
"""
from __future__ import annotations

import re
from typing import Optional, Tuple

from chronologia.calendars import jdn_to_julian, julian_to_jdn

#: months whose Nones/Ides fall two days later (March, May, July, October).
_LATE_MONTHS = frozenset({3, 5, 7, 10})
ROMAN_ANCHORS = frozenset({"kalends", "nones", "ides"})

#: additive value of each Roman-numeral letter.
_ROMAN_VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
#: the six legal subtractive pairs (IV IX XL XC CD CM); no other smaller-
#: before-larger arrangement is a well-formed classical numeral.
_ROMAN_SUBTRACTIVE = frozenset({"IV", "IX", "XL", "XC", "CD", "CM"})


def roman_to_int(text: str) -> Optional[int]:
    """Parse a strict, well-formed Roman numeral (1..3999) to ``int``.

    Case-sensitive on the caller's part is *not* enforced here -- the string
    is upper-cased first -- but the numeral must be **canonical**: repetition
    limits (``I``/``X``/``C``/``M`` at most three in a row, ``V``/``L``/``D``
    never repeated) and only the six standard subtractive pairs are accepted.
    A malformed or empty string (``"IIII"``, ``"VV"``, ``"IC"``, ``"MIX?"``)
    yields ``None`` rather than a lenient reading, so the homograph guard in
    the numeral fold never binds a value to a word that merely *looks* Roman.

    Reuse point for every Roman-numeral surface in the engine (century
    ordinals, regnal ordinals, classical year/date formulas): the numeral
    math lives here, next to the Roman calendar reckoning.
    """
    s = text.upper()
    if not s or any(ch not in _ROMAN_VALUES for ch in s):
        return None
    # repetition limits: I/X/C/M up to 3 in a row; V/L/D never doubled
    if re.search(r"(IIII|XXXX|CCCC|MMMM|VV|LL|DD)", s):
        return None
    total = 0
    i = 0
    n = len(s)
    while i < n:
        if i + 1 < n and s[i:i + 2] in _ROMAN_SUBTRACTIVE:
            total += _ROMAN_VALUES[s[i + 1]] - _ROMAN_VALUES[s[i]]
            i += 2
        elif i + 1 < n and _ROMAN_VALUES[s[i + 1]] > _ROMAN_VALUES[s[i]]:
            return None                 # illegal subtractive arrangement (IL, IC)
        else:
            total += _ROMAN_VALUES[s[i]]
            i += 1
    # round-trip check rejects non-canonical forms that slipped through
    return total if _int_to_roman(total) == s else None


def _int_to_roman(n: int) -> str:
    """Canonical Roman-numeral form of ``1 <= n <= 3999`` (empty otherwise)."""
    if not (1 <= n <= 3999):
        return ""
    table = ((1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
             (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
             (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"))
    out = []
    for value, sym in table:
        while n >= value:
            out.append(sym)
            n -= value
    return "".join(out)


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
