"""Pure arithmetic calendar conversions through a Julian Day Number hub.

Every calendar converts to and from an integer **Julian Day Number** (JDN,
the astronomical count with the noon epoch, so ``gregorian_to_jdn(2000, 1,
1) == 2451545``).  JDN is the single interchange hub: to convert Hijri ->
Hebrew you go Hijri -> JDN -> Hebrew.  Nothing here imports the engine and
nothing here is language-aware; this module is math only.

Scope: **arithmetic** calendars whose rules are deterministic tables.  No
observational/astronomical calendars (sighting-based Hijri, Chinese) and no
holiday resolution.  Tabular Hijri can differ by +-1 day from an
observation-based sighting; that caveat is documented on ``islamic_civil``.

Every algorithm is transcribed from a downloaded canonical source, never
from a conversion library:

* Gregorian/Julian JDN pair -- Fliegel & Van Flandern (1968), CACM 11(10):657,
  the integer algorithm reproduced in the Explanatory Supplement to the
  Astronomical Almanac (Richards).  Cross-checked against the USNO Julian
  Date reference (``~/AgentWorkspaces/papers/calendars/usno_julian_date.html``).
* Islamic (tabular/civil) and Hebrew (molad + dechiyot) -- Dershowitz &
  Reingold, "Calendrical Calculations", Software--Practice & Experience
  20(9):899-928 (1990), transcribed from the Lisp in that paper
  (``~/AgentWorkspaces/papers/calendars/reingold_dershowitz_1990_calendrical_calculations.pdf``);
  the paper works in "absolute dates" (RD, fixed day count with RD 1 =
  proleptic Gregorian 0001-01-01), converted to JDN here by the constant
  ``JDN = RD + 1721425``.
* French Republican (Romme arithmetic variant) and Bahá'í (arithmetic
  Badí', pre-2015 Gregorian-locked Naw-Rúz) -- the arithmetic rules and
  epochs from the downloaded reference tables
  (``~/AgentWorkspaces/papers/calendars/french_republican_reference.html``,
  ``bahai_calendar_reference.html``), both built directly on the Gregorian
  JDN conversion above.

Hebrew month numbering (documented decision): this module uses the
**ecclesiastical / biblical** numbering of Dershowitz & Reingold, Nisan = 1
... Tishri = 7 ... Adar (II) = 12/13.  The civil new year (Rosh HaShanah)
therefore falls on 1 Tishri = month 7.  This numbering is used because the
paper's epoch constant and every intermediate formula are derived under it;
adopting the civil numbering (Tishri = 1) would silently break the cited
arithmetic.  Vocabulary that names the months for a language must map
"tishri" -> 7, "nisan" -> 1, etc.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Tuple

# JDN of RD 1 (proleptic Gregorian 0001-01-01) minus the RD value itself:
# JDN(noon integer) = RD + 1721425.  Verified: gregorian_to_jdn(1, 1, 1) ==
# 1721426 == RD 1 + 1721425.
_RD_TO_JDN = 1721425


# --------------------------------------------------------------------------
# Gregorian & Julian: Fliegel & Van Flandern (1968) integer algorithm.
# --------------------------------------------------------------------------

def gregorian_to_jdn(year: int, month: int, day: int) -> int:
    """Proleptic Gregorian (year, month, day) -> Julian Day Number.

    Fliegel & Van Flandern (1968).  Floor division throughout, so negative
    (proleptic, astronomical-numbered) years convert correctly.
    """
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return (day + (153 * m + 2) // 5 + 365 * y + y // 4
            - y // 100 + y // 400 - 32045)


def julian_to_jdn(year: int, month: int, day: int) -> int:
    """Proleptic Julian (year, month, day) -> Julian Day Number.

    Fliegel & Van Flandern (1968), Julian variant (no centurial correction).
    """
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return day + (153 * m + 2) // 5 + 365 * y + y // 4 - 32083


def jdn_to_gregorian(jdn: int) -> Tuple[int, int, int]:
    """Julian Day Number -> proleptic Gregorian (year, month, day).

    Inverse of :func:`gregorian_to_jdn` (Fliegel & Van Flandern reverse).
    """
    l = jdn + 68569
    n = (4 * l) // 146097
    l = l - (146097 * n + 3) // 4
    i = (4000 * (l + 1)) // 1461001
    l = l - (1461 * i) // 4 + 31
    j = (80 * l) // 2447
    day = l - (2447 * j) // 80
    l = j // 11
    month = j + 2 - 12 * l
    year = 100 * (n - 49) + i + l
    return year, month, day


def jdn_to_julian(jdn: int) -> Tuple[int, int, int]:
    """Julian Day Number -> proleptic Julian (year, month, day)."""
    j = jdn + 1402
    k = (j - 1) // 1461
    l = j - 1461 * k
    n = (l - 1) // 365 - l // 1461
    i = l - 365 * n + 30
    j2 = (80 * i) // 2447
    day = i - (2447 * j2) // 80
    i = j2 // 11
    month = j2 + 2 - 12 * i
    year = 4 * k + n + i - 4716
    return year, month, day


# --------------------------------------------------------------------------
# Islamic (tabular / civil): Dershowitz & Reingold (1990), RD-based.
# --------------------------------------------------------------------------

_ISLAMIC_EPOCH_RD = 227015  # RD of 1 Muharram AH 1 (== JDN 1948440)


def _islamic_leap(year: int) -> bool:
    return (11 * year + 14) % 30 < 11


def _islamic_month_length(month: int, year: int) -> int:
    if month % 2 == 1:
        return 30
    if month == 12 and _islamic_leap(year):
        return 30
    return 29


def _abs_from_islamic(year: int, month: int, day: int) -> int:
    return (day + 29 * (month - 1) + month // 2
            + (year - 1) * 354 + (3 + 11 * year) // 30
            + _ISLAMIC_EPOCH_RD - 1)


def _islamic_from_abs(rd: int) -> Tuple[int, int, int]:
    if rd < _ISLAMIC_EPOCH_RD:
        raise ValueError("date precedes the Islamic epoch")
    year = (rd - _ISLAMIC_EPOCH_RD) // 355 + 1
    while _abs_from_islamic(year + 1, 1, 1) <= rd:
        year += 1
    month = 1
    while (month < 12 and
           _abs_from_islamic(year, month, _islamic_month_length(month, year)) < rd):
        month += 1
    day = rd - _abs_from_islamic(year, month, 1) + 1
    return year, month, day


def islamic_civil_to_jdn(year: int, month: int, day: int) -> int:
    return _abs_from_islamic(year, month, day) + _RD_TO_JDN


def islamic_civil_from_jdn(jdn: int) -> Tuple[int, int, int]:
    return _islamic_from_abs(jdn - _RD_TO_JDN)


# --------------------------------------------------------------------------
# Hebrew (molad + dechiyot): Dershowitz & Reingold (1990), RD-based.
# --------------------------------------------------------------------------

_HEBREW_ABS_OFFSET = -1373429  # "days elapsed before absolute date 1"


def _hebrew_leap(year: int) -> bool:
    return (7 * year + 1) % 19 < 7


def _hebrew_last_month(year: int) -> int:
    return 13 if _hebrew_leap(year) else 12


def _hebrew_elapsed_days(year: int) -> int:
    """Days from the Sunday before the epoch to the molad of Tishri of
    ``year``, with all four dechiyot (postponement) rules applied."""
    months_elapsed = (235 * ((year - 1) // 19)      # complete cycles
                      + 12 * ((year - 1) % 19)      # regular months this cycle
                      + (7 * ((year - 1) % 19) + 1) // 19)  # leap months
    parts_elapsed = 5604 + 13753 * months_elapsed
    day = 1 + 29 * months_elapsed + parts_elapsed // 25920
    parts = parts_elapsed % 25920
    if (parts >= 19440                                        # molad zaqen
            or (day % 7 == 2 and parts >= 9924 and not _hebrew_leap(year))
            or (day % 7 == 1 and parts >= 16789 and _hebrew_leap(year - 1))):
        alt = day + 1
    else:
        alt = day
    if alt % 7 in (0, 3, 5):        # lo ADU rosh: never Sun/Wed/Fri
        return alt + 1
    return alt


def _hebrew_year_length(year: int) -> int:
    return _hebrew_elapsed_days(year + 1) - _hebrew_elapsed_days(year)


def _long_heshvan(year: int) -> bool:
    return _hebrew_year_length(year) % 10 == 5


def _short_kislev(year: int) -> bool:
    return _hebrew_year_length(year) % 10 == 3


def _hebrew_month_length(month: int, year: int) -> int:
    if (month in (2, 4, 6, 10, 13)
            or (month == 12 and not _hebrew_leap(year))
            or (month == 8 and not _long_heshvan(year))
            or (month == 9 and _short_kislev(year))):
        return 29
    return 30


def _abs_from_hebrew(year: int, month: int, day: int) -> int:
    if month < 7:      # Nisan..Elul: add Tishri..year-end, then Nisan..month-1
        prior = (sum(_hebrew_month_length(m, year)
                     for m in range(7, _hebrew_last_month(year) + 1))
                 + sum(_hebrew_month_length(m, year)
                       for m in range(1, month)))
    else:              # Tishri..: add Tishri..month-1
        prior = sum(_hebrew_month_length(m, year) for m in range(7, month))
    return day + prior + _hebrew_elapsed_days(year) + _HEBREW_ABS_OFFSET


def _hebrew_from_abs(rd: int) -> Tuple[int, int, int]:
    year = (rd - _HEBREW_ABS_OFFSET) // 366
    while _abs_from_hebrew(year + 1, 7, 1) <= rd:
        year += 1
    start = 1 if rd >= _abs_from_hebrew(year, 1, 1) else 7
    month = start
    while _abs_from_hebrew(year, month,
                           _hebrew_month_length(month, year)) < rd:
        month += 1
    day = rd - _abs_from_hebrew(year, month, 1) + 1
    return year, month, day


def hebrew_to_jdn(year: int, month: int, day: int) -> int:
    return _abs_from_hebrew(year, month, day) + _RD_TO_JDN


def hebrew_from_jdn(jdn: int) -> Tuple[int, int, int]:
    return _hebrew_from_abs(jdn - _RD_TO_JDN)


# --------------------------------------------------------------------------
# French Republican (Romme arithmetic variant).
# --------------------------------------------------------------------------

_FR_EPOCH_JDN = gregorian_to_jdn(1792, 9, 22)  # An I Vendemiaire 1


def _fr_sextile(year: int) -> bool:
    """Sextile (leap) year in the Romme arithmetic variant: year Y is
    sextile iff Y+1 is a Gregorian leap year.  This reproduces the
    historically observed sextiles (An III, VII, XI) and continues
    predictably with the Gregorian centurial correction.  The true-equinox
    variant (leap year fixed by the observed autumnal equinox at Paris) is
    out of scope -- it is not arithmetic."""
    y = year + 1
    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)


def _fr_year_length(year: int) -> int:
    return 366 if _fr_sextile(year) else 365


def french_republican_to_jdn(year: int, month: int, day: int) -> int:
    """(year, month, day) -> JDN.  Months 1..12 have 30 days; the five or
    six complementary days (sansculottides) are addressed as month 13."""
    offset = sum(_fr_year_length(y) for y in range(1, year))
    offset += (month - 1) * 30 + (day - 1)
    return _FR_EPOCH_JDN + offset


def french_republican_from_jdn(jdn: int) -> Tuple[int, int, int]:
    offset = jdn - _FR_EPOCH_JDN
    if offset < 0:
        raise ValueError("date precedes the French Republican epoch")
    year = 1
    while offset >= _fr_year_length(year):
        offset -= _fr_year_length(year)
        year += 1
    if offset < 360:
        return year, offset // 30 + 1, offset % 30 + 1
    return year, 13, offset - 360 + 1     # complementary day


# --------------------------------------------------------------------------
# Bahá'í (arithmetic Badí', pre-2015 Gregorian-locked Naw-Rúz).
# --------------------------------------------------------------------------

def _bahai_naw_ruz_jdn(year: int) -> int:
    """JDN of Naw-Rúz (year day 1).  In the pre-2015 arithmetic form
    Naw-Rúz is locked to 21 March Gregorian, so BE year Y begins on 21
    March of Gregorian year 1843 + Y.  The post-2015 astronomical form
    (Naw-Rúz set by the vernal equinox at Tehran) is out of scope."""
    return gregorian_to_jdn(1843 + year, 3, 21)


_BAHAI_EPOCH_JDN = _bahai_naw_ruz_jdn(1)  # BE 1 = 1844-03-21


def bahai_to_jdn(year: int, month: int, day: int) -> int:
    """(year, month, day) -> JDN.  Months 1..18 and 19 have 19 days each;
    the intercalary Ayyám-i-Há (4 or 5 days) sits between month 18 and
    month 19 and is addressed as month 0."""
    base = _bahai_naw_ruz_jdn(year)
    if month == 0:                          # Ayyam-i-Ha
        return base + 342 + (day - 1)
    if month == 19:                         # 'Ala', after Ayyam-i-Ha
        total = _bahai_naw_ruz_jdn(year + 1) - base
        ayyam = total - 361
        return base + 342 + ayyam + (day - 1)
    return base + (month - 1) * 19 + (day - 1)


def bahai_from_jdn(jdn: int) -> Tuple[int, int, int]:
    year = jdn_to_gregorian(jdn)[0] - 1843
    while _bahai_naw_ruz_jdn(year) > jdn:
        year -= 1
    while _bahai_naw_ruz_jdn(year + 1) <= jdn:
        year += 1
    offset = jdn - _bahai_naw_ruz_jdn(year)
    if offset < 342:
        return year, offset // 19 + 1, offset % 19 + 1
    rem = offset - 342
    total = _bahai_naw_ruz_jdn(year + 1) - _bahai_naw_ruz_jdn(year)
    ayyam = total - 361
    if rem < ayyam:
        return year, 0, rem + 1             # Ayyam-i-Ha
    return year, 19, rem - ayyam + 1


# --------------------------------------------------------------------------
# Registry.
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Calendar:
    """A registered arithmetic calendar.

    ``to_jdn(year, month, day) -> int`` and ``from_jdn(jdn) -> (year, month,
    day)`` are inverse integer functions through the JDN hub.  ``month_count``
    is the maximum month number a language may name (leap-month and
    intercalary calendars use the larger count).  ``epoch_jdn`` is the JDN of
    day 1 of the calendar (for reference/citation).
    """
    key: str
    month_count: int
    to_jdn: Callable[[int, int, int], int]
    from_jdn: Callable[[int], Tuple[int, int, int]]
    epoch_jdn: int


CALENDARS: Dict[str, Calendar] = {
    "islamic_civil": Calendar(
        "islamic_civil", 12, islamic_civil_to_jdn, islamic_civil_from_jdn,
        islamic_civil_to_jdn(1, 1, 1)),
    "hebrew": Calendar(
        "hebrew", 13, hebrew_to_jdn, hebrew_from_jdn,
        hebrew_to_jdn(1, 7, 1)),
    "julian": Calendar(
        "julian", 12, julian_to_jdn, jdn_to_julian, julian_to_jdn(1, 1, 1)),
    "french_republican": Calendar(
        "french_republican", 13, french_republican_to_jdn,
        french_republican_from_jdn, _FR_EPOCH_JDN),
    "bahai": Calendar(
        "bahai", 19, bahai_to_jdn, bahai_from_jdn, _BAHAI_EPOCH_JDN),
}
