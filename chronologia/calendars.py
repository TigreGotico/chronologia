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

Deliberately excluded (considered, not shipped): the **Burmese** (Makaranta /
Thandeikta) and **Javanese** lunisolar calendars.  Neither reduces to a
verifiable pure-arithmetic rule.  The Burmese watat (intercalary-month)
determination depends on an apparent-solar-longitude excess and carries
era-specific royal-decree exception years, so a faithful implementation needs
embedded exception tables rather than a formula.  The Javanese 8-year windu
cycle is nominally arithmetic (three 355-day "wuntu" years per windu), but its
leap-year positions are reported inconsistently across sources and the system
applies a 120-year "kurup" correction (the Aboge -> Asapon epoch shift) that
moves the leap pattern; no single downloaded canonical source pins both the
rule and datable gold values, so an implementation could not be verified.
Rather than invent unverified leap rules, both are left out.

Every algorithm is transcribed from a downloaded canonical source, never
from a conversion library:

* Gregorian/Julian JDN pair -- Fliegel & Van Flandern (1968), CACM 11(10):657,
  the integer algorithm reproduced in the Explanatory Supplement to the
  Astronomical Almanac (Richards).  Cross-checked against the USNO Julian
  Date reference.
* Islamic (tabular/civil) and Hebrew (molad + dechiyot) -- Dershowitz &
  Reingold, "Calendrical Calculations", Software--Practice & Experience
  20(9):899-928 (1990), transcribed from the Lisp in that paper;
  the paper works in "absolute dates" (RD, fixed day count with RD 1 =
  proleptic Gregorian 0001-01-01), converted to JDN here by the constant
  ``JDN = RD + 1721425``.
* French Republican (Romme arithmetic variant) and Bahá'í (arithmetic
  Badí', pre-2015 Gregorian-locked Naw-Rúz) -- the arithmetic rules and
  epochs from the published reference tables, both built directly on the
  Gregorian JDN conversion above.

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

import os
from dataclasses import dataclass, field
from typing import (Callable, Dict, List, Mapping, Optional, Tuple, Union)

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
    if not 1 <= month <= 12:
        raise CalendarRangeError(
            f"julian month {month} out of range for year {year}; "
            f"expected 1..12")
    _julian_leap = year % 4 == 0
    _month_len = (31, 29 if _julian_leap else 28, 31, 30, 31, 30,
                  31, 31, 30, 31, 30, 31)[month - 1]
    if not 1 <= day <= _month_len:
        raise CalendarRangeError(
            f"julian day {day} out of range for {year}-{month}; "
            f"expected 1..{_month_len}")
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


def _year_containing(elapsed: int, start_of_year, seed: int,
                     longest_year: int) -> int:
    """The calendar year whose first day is the last one at or before
    ``elapsed`` (an absolute day count), from a ``seed`` estimate.

    ``start_of_year(y)`` is the absolute day of year ``y``'s first day, monotone
    increasing in ``y``.  A fixed rough divisor drifts LINEARLY with the year
    magnitude, so a bare +-1 correction turns a large (but valid) year into a
    multi-second linear scan; jumping by ``error // longest_year`` (an
    under-jump, so it never overshoots) converges in O(log magnitude) for any
    year.  The closing +-1 loops guarantee the exact year, so the seed and the
    jumps only have to get roughly there.
    """
    year = seed
    for _ in range(200):          # a backstop; real convergence is O(log)
        err = elapsed - start_of_year(year)
        if 0 <= err < longest_year:
            break
        year += err // longest_year or (1 if err > 0 else -1)
    while start_of_year(year + 1) <= elapsed:
        year += 1
    while start_of_year(year) > elapsed:
        year -= 1
    return year


def _abs_from_islamic(year: int, month: int, day: int) -> int:
    return (day + 29 * (month - 1) + month // 2
            + (year - 1) * 354 + (3 + 11 * year) // 30
            + _ISLAMIC_EPOCH_RD - 1)


def _islamic_from_abs(rd: int) -> Tuple[int, int, int]:
    if rd < _ISLAMIC_EPOCH_RD:
        raise ValueError("date precedes the Islamic epoch")
    year = _year_containing(rd, lambda y: _abs_from_islamic(y, 1, 1),
                            (rd - _ISLAMIC_EPOCH_RD) // 355 + 1, 356)
    month = 1
    while (month < 12 and
           _abs_from_islamic(year, month, _islamic_month_length(month, year)) < rd):
        month += 1
    day = rd - _abs_from_islamic(year, month, 1) + 1
    return year, month, day


def islamic_civil_to_jdn(year: int, month: int, day: int) -> int:
    if not 1 <= month <= 12:
        raise CalendarRangeError(
            f"islamic_civil month {month} out of range for year {year}; "
            f"expected 1..12")
    length = _islamic_month_length(month, year)
    if not 1 <= day <= length:
        raise CalendarRangeError(
            f"islamic_civil day {day} out of range for {year}-{month}; "
            f"expected 1..{length}")
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
    year = _year_containing(rd, lambda y: _abs_from_hebrew(y, 7, 1),
                            (rd - _HEBREW_ABS_OFFSET) // 366, 386)
    start = 1 if rd >= _abs_from_hebrew(year, 1, 1) else 7
    month = start
    while _abs_from_hebrew(year, month,
                           _hebrew_month_length(month, year)) < rd:
        month += 1
    day = rd - _abs_from_hebrew(year, month, 1) + 1
    return year, month, day


def hebrew_to_jdn(year: int, month: int, day: int) -> int:
    last = _hebrew_last_month(year)
    if not 1 <= month <= last:
        raise CalendarRangeError(
            f"hebrew month {month} out of range for year {year}; "
            f"expected 1..{last}")
    length = _hebrew_month_length(month, year)
    if not 1 <= day <= length:
        raise CalendarRangeError(
            f"hebrew day {day} out of range for {year}-{month}; "
            f"expected 1..{length}")
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


def _fr_days_before(year: int) -> int:
    """Days from An I Vendemiaire 1 to year ``year`` Vendemiaire 1 -- the
    closed-form value of ``sum(_fr_year_length(y) for y in range(1, year))``,
    so conversion is O(1) rather than O(year) (a huge Python-big-int year no
    longer drives an unbounded loop)."""
    if year <= 1:
        return 0
    # 365 days per year plus one for each sextile year in [1, year-1]. Year Y
    # is sextile iff Y+1 is a Gregorian leap year, so the extra-day count is the
    # number of Gregorian leap years in [2, year].
    greg_leaps = year // 4 - year // 100 + year // 400
    return 365 * (year - 1) + greg_leaps


def french_republican_to_jdn(year: int, month: int, day: int) -> int:
    """(year, month, day) -> JDN.  Months 1..12 have 30 days; the five or
    six complementary days (sansculottides) are addressed as month 13."""
    if not 1 <= month <= 13:
        raise CalendarRangeError(
            f"french_republican month {month} out of range for year {year}; "
            f"expected 1..13")
    if month <= 12:
        length = 30
    else:
        length = 6 if _fr_sextile(year) else 5
    if not 1 <= day <= length:
        raise CalendarRangeError(
            f"french_republican day {day} out of range for {year}-{month}; "
            f"expected 1..{length}")
    offset = _fr_days_before(year) + (month - 1) * 30 + (day - 1)
    return _FR_EPOCH_JDN + offset


def french_republican_from_jdn(jdn: int) -> Tuple[int, int, int]:
    offset = jdn - _FR_EPOCH_JDN
    if offset < 0:
        raise ValueError("date precedes the French Republican epoch")
    # Estimate the year from the mean length (365.2425 d), then correct with the
    # O(1) cumulative -- bounds the loop to a couple of steps instead of O(year).
    year = max(1, (offset * 10_000) // 3_652_425 + 1)
    while _fr_days_before(year) > offset:
        year -= 1
    while _fr_days_before(year + 1) <= offset:
        year += 1
    offset -= _fr_days_before(year)
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
    if not 0 <= month <= 19:
        raise CalendarRangeError(
            f"bahai month {month} out of range for year {year}; "
            f"expected 0..19")
    base = _bahai_naw_ruz_jdn(year)
    if month == 0:                          # Ayyam-i-Ha
        total = _bahai_naw_ruz_jdn(year + 1) - base
        ayyam = total - 361
        if not 1 <= day <= ayyam:
            raise CalendarRangeError(
                f"bahai day {day} out of range for {year}-0 (Ayyam-i-Ha); "
                f"expected 1..{ayyam}")
        return base + 342 + (day - 1)
    if not 1 <= day <= 19:
        raise CalendarRangeError(
            f"bahai day {day} out of range for {year}-{month}; "
            f"expected 1..19")
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
# Coptic & Ethiopic: 12x30 + a 5/6-day epagomenal 13th month.
# --------------------------------------------------------------------------
# Both are the ancient Egyptian "wandering year" fixed to the Julian leap
# rule: twelve 30-day months plus a short 13th month of 5 days (6 in a leap
# year).  A year Y is leap iff ``Y % 4 == 3`` -- the Coptic/Ethiopic leap day
# falls in the year *preceding* the Julian bissextile, so their new year keeps
# a fixed Julian date.  Algorithm and epochs transcribed from Dershowitz &
# Reingold, "Calendrical Calculations", chapter 4 (Coptic and Ethiopic),
# reproduced in the 1990 SP&E paper's companion material;
# epochs cross-checked against published reference tables.
#
# Coptic epoch: 1 Thoout AM 1 (Era of the Martyrs / Diocletian) == 284-08-29
# Julian == JDN 1825030.  Ethiopic epoch (Incarnation era): 1 Maskaram EE 1 ==
# 8-08-29 Julian == JDN 1724221, exactly 276 Julian years after the Coptic
# epoch, so a given day is numbered 276 years higher in the Ethiopic reckoning
# (Coptic AM 1741 == Ethiopic EE 2017, both starting 2024-09-11 Gregorian).

_COPTIC_EPOCH_JDN = julian_to_jdn(284, 8, 29)   # 1825030
_ETHIOPIC_EPOCH_JDN = julian_to_jdn(8, 8, 29)   # 1724221


def _coptic_like_to_jdn(epoch: int, year: int, month: int, day: int,
                        key: str = "coptic-like") -> int:
    if not 1 <= month <= 13:
        raise CalendarRangeError(
            f"{key} month {month} out of range for year {year}; "
            f"expected 1..13")
    if month <= 12:
        length = 30
    else:
        length = 6 if year % 4 == 3 else 5
    if not 1 <= day <= length:
        raise CalendarRangeError(
            f"{key} day {day} out of range for {year}-{month}; "
            f"expected 1..{length}")
    return epoch + 365 * (year - 1) + year // 4 + 30 * (month - 1) + (day - 1)


def _coptic_like_from_jdn(epoch: int, jdn: int) -> Tuple[int, int, int]:
    days = jdn - epoch
    year = (4 * days + 1463) // 1461
    month = (jdn - _coptic_like_to_jdn(epoch, year, 1, 1)) // 30 + 1
    day = jdn - _coptic_like_to_jdn(epoch, year, month, 1) + 1
    return year, month, day


def coptic_to_jdn(year: int, month: int, day: int) -> int:
    """Coptic (year, month, day) -> JDN.  Months 1..12 have 30 days; the
    epagomenal 5 (or 6, when ``year % 4 == 3``) days are month 13.  Proleptic
    for years <= 0."""
    return _coptic_like_to_jdn(_COPTIC_EPOCH_JDN, year, month, day, "coptic")


def coptic_from_jdn(jdn: int) -> Tuple[int, int, int]:
    return _coptic_like_from_jdn(_COPTIC_EPOCH_JDN, jdn)


def ethiopic_to_jdn(year: int, month: int, day: int) -> int:
    """Ethiopic (year, month, day) -> JDN.  Same 12x30 + 5/6 structure as
    Coptic; epoch is 276 Julian years later (Incarnation era)."""
    return _coptic_like_to_jdn(_ETHIOPIC_EPOCH_JDN, year, month, day, "ethiopian")


def ethiopic_from_jdn(jdn: int) -> Tuple[int, int, int]:
    return _coptic_like_from_jdn(_ETHIOPIC_EPOCH_JDN, jdn)


# --------------------------------------------------------------------------
# Berber (Amazigh): the Julian calendar under a shifted era.
# --------------------------------------------------------------------------
# The Amazigh calendar in modern use (Algeria, Morocco, the Kabyle and
# Riffian diaspora, ...) is structurally the Julian calendar -- same twelve
# months, same ``year % 4 == 0`` leap rule, same 1 January new year -- with
# the months given Berber names and the year counted from a different era.
# The +950 era offset (agricultural year 2976 == Julian/Gregorian 2026) was
# fixed in 1968 by the Académie Berbère, who chose it to commemorate the
# accession of Shoshenq I, the Berber pharaoh of Egypt's 22nd dynasty
# (conventionally dated 950 BC).  It is a documented 20th-century symbolic
# choice, not an ancient reckoning: no earlier era count for this calendar
# is attested.  Because the offset is a pure additive year shift onto the
# existing Julian arithmetic, 1 Yennayer (Berber new year) falls on 1
# January Julian every year, which is 14 January Gregorian for the 1900-2099
# window (13 days of Julian/Gregorian drift).
#
# Year-end leap-day placement.  Popular description often states that the
# calendar's intercalary day is appended at the *end* of the year (after
# Dujembeṛ) rather than inside February as in the base Julian layout. That
# claim traces to a single source (Wikipedia's "Berber calendar" article)
# with no corroborating primary reference, and changing where within the
# year the leap day sits does not change which years are leap or the total
# day count, so it cannot be checked against any dated event. This module
# therefore keeps the plain Julian placement (extra day in February, via
# ``julian_to_jdn``/``jdn_to_julian``) and does not hard-code the
# append-at-year-end convention; it is flagged here as an open question
# pending native/community confirmation, not shipped as arithmetic.
#
# Civil Yennayer holidays are explicitly OUT of scope for this arithmetic
# entry. Algeria's Yennayer public holiday is a fixed civil date, 12
# January Gregorian, set by presidential decree (27 December 2017, first
# observed 2018) -- two days *earlier* than the 14 January this calendar's
# Julian arithmetic produces for the same era year. Morocco's is fixed at
# 13 January Gregorian by royal decree (May 2023, effective 2024). Neither
# is derived from -- or reconcilable with -- the Julian-era arithmetic
# above: they are legislated civil dates, not calendar output, and belong
# to the civil-holidays data layer (see ``holiday_data/dz.tab``,
# ``holiday_data/ma.tab``), never to this function. A popular folk
# justification for Algeria's 12 January ("13 days of drift back from 1
# January") is arithmetically inconsistent -- 13 days after 1 January is
# 14 January, not 12 -- and is not encoded here in any form.
#
# Gold check: 1 Yennayer 2976 == Julian 2026-01-01 == Gregorian 2026-01-14.


def berber_to_jdn(year: int, month: int, day: int) -> int:
    """Berber/Amazigh (year, month, day) -> JDN.

    Julian month/leap structure; the calendar year is the Julian year plus
    950 (the Académie Berbère's 1968 era anchor -- see module note).
    Proleptic for years <= 0.
    """
    return julian_to_jdn(year - 950, month, day)


def berber_from_jdn(jdn: int) -> Tuple[int, int, int]:
    year, month, day = jdn_to_julian(jdn)
    return year + 950, month, day


# --------------------------------------------------------------------------
# Revised Julian (Milankovic): the 900-year leap-century rule.
# --------------------------------------------------------------------------
# Adopted 1923 by several Orthodox churches.  Structurally the Julian/AD
# calendar (same months, same ``Y % 4`` base rule) but a century year is leap
# only when ``Y % 900 in (200, 600)`` -- a 218-leap-years-per-900 cycle
# (mean year 365.2422 d), closer to the tropical year than the Gregorian
# 97/400.  The two agree from 1 March 1600 through 28 February 2800 and first
# diverge on 2800-03-01: 2800 is a Gregorian leap year (divisible by 400) but
# not a Revised Julian one (2800 % 900 == 100).  Leap rule from the downloaded
# reference material; the year/month arithmetic mirrors the Fliegel & Van
# Flandern method used for Gregorian above.

_RJ_MONTH_CUM = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)


def _rj_leap(year: int) -> bool:
    if year % 4:
        return False
    if year % 100:
        return True
    return year % 900 in (200, 600)


def _rj_leaps_before(year: int) -> int:
    """Number of Revised Julian leap years in AD years 1..``year``."""
    def cent(r: int) -> int:      # century years <= year with Y % 900 == r
        return (year - r) // 900 + 1 if year >= r else 0
    return year // 4 - year // 100 + cent(200) + cent(600)


def _rj_year_day(year: int, month: int, day: int) -> int:
    yd = _RJ_MONTH_CUM[month - 1] + day
    if month > 2 and _rj_leap(year):
        yd += 1
    return yd


def revised_julian_to_jdn(year: int, month: int, day: int) -> int:
    """Revised Julian (year, month, day) -> JDN.  Proleptic for years <= 0."""
    return (_RJ_EPOCH_JDN + 365 * (year - 1) + _rj_leaps_before(year - 1)
            + _rj_year_day(year, month, day) - 1)


# Anchor so that within the agreement window the Revised Julian date equals the
# Gregorian date of the same JDN (Revised Julian 0001-01-01 lands on proleptic
# Gregorian 0001-01-01, the same as Julian differs -- verified by the sweep).
_RJ_EPOCH_JDN = (gregorian_to_jdn(2000, 1, 1)
                 - (365 * 1999 + _rj_leaps_before(1999)))


def revised_julian_from_jdn(jdn: int) -> Tuple[int, int, int]:
    year = _year_containing(jdn, lambda y: revised_julian_to_jdn(y, 1, 1),
                            (jdn - _RJ_EPOCH_JDN) // 366 + 1, 367)
    yday = jdn - revised_julian_to_jdn(year, 1, 1) + 1
    month = 1
    while month < 12 and _rj_year_day(year, month + 1, 1) <= yday:
        month += 1
    day = yday - _rj_year_day(year, month, 1) + 1
    return year, month, day


# --------------------------------------------------------------------------
# Armenian: the 365-day "vague year" (no leap at all).
# --------------------------------------------------------------------------
# Twelve 30-day months plus five epagomenal days (aweleac', month 13), and
# -- unlike Coptic/Ethiopic -- no intercalation whatsoever, so every year is
# exactly 365 days and the new year drifts one day earlier per four Julian
# years.  Epoch (start of the Armenian era): 1 Navasard AE 1 == 552-07-11
# Julian == JDN 1922868.  Algorithm and epoch transcribed from Dershowitz &
# Reingold, "Calendrical Calculations" (Armenian calendar), a plain shift of
# the Egyptian wandering year; the epoch is the anchor from which the modern
# conversions below are derived (the vague year has no astronomical event to
# re-check against, unlike the leap-locked calendars).

_ARMENIAN_EPOCH_JDN = julian_to_jdn(552, 7, 11)   # 1922868


def armenian_to_jdn(year: int, month: int, day: int) -> int:
    """Armenian (year, month, day) -> JDN.  Months 1..12 have 30 days; the
    five epagomenal days are month 13.  No leap year.  Proleptic for
    years <= 0."""
    return _ARMENIAN_EPOCH_JDN + 365 * (year - 1) + 30 * (month - 1) + (day - 1)


def armenian_from_jdn(jdn: int) -> Tuple[int, int, int]:
    days = jdn - _ARMENIAN_EPOCH_JDN
    year, rem = days // 365 + 1, days % 365
    return year, rem // 30 + 1, rem % 30 + 1


# --------------------------------------------------------------------------
# Egyptian civil calendar: the original 365-day "vague year".
# --------------------------------------------------------------------------
# Twelve 30-day months (grouped in three four-month seasons: Akhet
# "Inundation" months 1-4, Peret "Emergence" months 5-8, Shemu "Harvest"
# months 9-12) plus five epagomenal days (the birthdays of Osiris, Horus,
# Seth, Isis and Nephthys) as month 13 -- and, unlike Coptic/Ethiopic, no
# intercalation whatsoever, so the calendar is *the* vague year: every year
# is exactly 365 days, and the civil new year (1 Thoth) drifts one day
# earlier against the solar/Sothic year every four years, completing a full
# cycle in 1460 Egyptian years (the Sothic cycle).  The Armenian calendar
# above is a documented later transplant of this same wandering-year
# arithmetic.
#
# Epoch: the era of Nabonassar anchor used since antiquity to fix the
# Egyptian civil calendar astronomically (Ptolemy's *Almagest* keyed his
# observation tables to it): 1 Thoth I, year 1 of Nabonassar = 26 February
# 747 BC Julian (proleptic astronomical year -746) = JDN 1448638.  Algorithm
# (a plain 365-day linear count, one 30-day month at a time, epagomenal days
# as month 13) and the epoch value are both transcribed from Dershowitz &
# Reingold, "Calendrical Calculations" (the Egyptian calendar section);
# cross-checked here against ``julian_to_jdn(-746, 2, 26) == 1448638``, which
# matches the source's stated JDN for the epoch exactly.

_EGYPTIAN_EPOCH_JDN = julian_to_jdn(-746, 2, 26)   # 1448638


def egyptian_to_jdn(year: int, month: int, day: int) -> int:
    """Egyptian civil (year, month, day) -> JDN.  Months 1..12 have 30 days;
    the five epagomenal days are month 13.  No leap year, ever -- the vague
    year is always 365 days long.  Proleptic for years <= 0."""
    return _EGYPTIAN_EPOCH_JDN + 365 * (year - 1) + 30 * (month - 1) + (day - 1)


def egyptian_from_jdn(jdn: int) -> Tuple[int, int, int]:
    days = jdn - _EGYPTIAN_EPOCH_JDN
    year, rem = days // 365 + 1, days % 365
    return year, rem // 30 + 1, rem % 30 + 1


# --------------------------------------------------------------------------
# Maya Long Count: a pure day count in a mixed-radix positional notation.
# --------------------------------------------------------------------------
# The Long Count is not a year/month/day calendar at all -- it is a single
# elapsed-day count written in five positions, most significant first:
#
#     baktun . katun . tun . uinal . kin
#        x20     x20    x18    x20    x1     (radices, right to left)
#
# so 1 uinal = 20 kin, 1 tun = 18 uinal = 360 kin, 1 katun = 7200 kin, 1
# baktun = 144000 kin.  The count's zero point (0.0.0.0.0) is fixed by the
# Goodman-Martinez-Thompson correlation, GMT = 584283: JDN 584283 == proleptic
# Gregorian -3113-08-11.  Correlation constant and radices from Dershowitz &
# Reingold, "Calendrical Calculations" (Mayan calendars), which adopt GMT
# 584283.  Cross-check: 13.0.0.0.0 (the close of the 13th baktun) == JDN
# 2456283 == 2012-12-21 Gregorian.
#
# Registry contract note: the shared ``Calendar`` uses a three-field
# ``(y, m, d)`` shape, so the registered ``mayan_long_count`` entry exposes the
# two lowest positions as "months" (uinal, month_count 18) and "days" (kin)
# with everything at or above the tun collapsed into the first field -- a
# faithful bijection that round-trips through the JDN hub.  The full five-place
# Long Count is available through the standalone functions below, which the
# gold tests exercise directly.

_MAYAN_EPOCH_JDN = 584283          # 0.0.0.0.0, GMT correlation


def mayan_long_count_to_jdn(baktun: int, katun: int, tun: int,
                            uinal: int, kin: int) -> int:
    """Five-place Maya Long Count -> JDN (mixed radix 20/20/18/20/1)."""
    return (_MAYAN_EPOCH_JDN + baktun * 144000 + katun * 7200
            + tun * 360 + uinal * 20 + kin)


def mayan_long_count_from_jdn(jdn: int) -> Tuple[int, int, int, int, int]:
    """JDN -> five-place Maya Long Count ``(baktun, katun, tun, uinal, kin)``.

    Pre-epoch JDNs yield negative baktun values (a proleptic extension of the
    count); every position below baktun stays in range via floor division."""
    n = jdn - _MAYAN_EPOCH_JDN
    kin, n = n % 20, n // 20
    uinal, n = n % 18, n // 18
    tun, n = n % 20, n // 20
    katun, baktun = n % 20, n // 20
    return baktun, katun, tun, uinal, kin


def mayan_long_count_registry_to_jdn(tuncount: int, uinal: int,
                                     kin: int) -> int:
    """Three-field registry view: ``tuncount`` is the whole count at and above
    the tun position (= baktun*400 + katun*20 + tun), ``uinal`` the month-like
    18-radix position, ``kin`` the day."""
    return _MAYAN_EPOCH_JDN + tuncount * 360 + uinal * 20 + kin


def mayan_long_count_registry_from_jdn(jdn: int) -> Tuple[int, int, int]:
    n = jdn - _MAYAN_EPOCH_JDN
    kin, n = n % 20, n // 20
    uinal, tuncount = n % 18, n // 18
    return tuncount, uinal, kin


# --------------------------------------------------------------------------
# ISO 8601 week date (YYYY-Www-D).
# --------------------------------------------------------------------------
# A reckoning of the Gregorian calendar, not a separate era: every day belongs
# to an ISO week-numbering year, a week 1..52/53 and a weekday 1..7 (Monday=1
# .. Sunday=7).  ISO 8601 fixes week 1 as the week containing the year's first
# Thursday, equivalently the week containing 4 January.  A week-numbering year
# has 53 weeks when 4 January (or, equivalently, 31 December) falls such that
# the year has 53 Thursdays -- e.g. 2020 has W53.  Rule from ISO 8601;
# arithmetic built directly on the Gregorian JDN conversion above.  Weekday is
# ``jdn % 7 + 1`` because JDN 0 is a Monday.

def _iso_week1_monday_jdn(iso_year: int) -> int:
    """JDN of the Monday that starts ISO week 1 of ``iso_year`` (the Monday of
    the week containing 4 January)."""
    jan4 = gregorian_to_jdn(iso_year, 1, 4)
    return jan4 - jan4 % 7            # jan4 % 7 == (weekday of jan4) - 1


def iso_week_to_jdn(iso_year: int, week: int, weekday: int) -> int:
    """ISO (week-year, week, weekday 1=Mon..7=Sun) -> JDN."""
    return _iso_week1_monday_jdn(iso_year) + (week - 1) * 7 + (weekday - 1)


def iso_week_from_jdn(jdn: int) -> Tuple[int, int, int]:
    """JDN -> ISO ``(week-year, week, weekday)``.  The week-year is taken from
    the Thursday of the same ISO week, so it can differ from the Gregorian
    year at the year boundary."""
    weekday = jdn % 7 + 1
    thursday = jdn - (weekday - 1) + 3
    iso_year = jdn_to_gregorian(thursday)[0]
    week = (jdn - _iso_week1_monday_jdn(iso_year)) // 7 + 1
    return iso_year, week, weekday


# --------------------------------------------------------------------------
# Solar Hijri (arithmetic 33-year cycle).
# --------------------------------------------------------------------------
# CAVEAT -- APPROXIMATION.  The legal Iranian (Solar Hijri / Jalali) calendar
# is astronomical: 1 Farvardin is the day whose start is nearest the March
# equinox at the 52.5degE meridian, and it is NOT reducible to a fixed
# arithmetic rule.  This entry implements the *arithmetic* 33-year-cycle
# approximation (the family associated with Ahmad Birashk's tabulations):
# months 1..6 have 31 days, 7..11 have 30, month 12 has 29 (30 in a leap
# year), and a year is leap when ``year % 33`` is one of a fixed set of eight
# residues -- eight leap years per 33, mean year 365 + 8/33 = 365.2424 days.
# It tracks the legal calendar across the modern window but is known to
# diverge by +-1 day in scattered years; callers needing the legal date near a
# flagged year must consult an astronomical source.
#
# Leap residues -- VERIFICATION NOTE.  The 33-year cycle appears in the
# literature with two conventions differing in one residue: {1,5,9,13,17,22,
# 26,30} and {1,5,9,13,18,22,26,30} (17 vs 18).  Checked against twelve
# documented astronomical Nowruz dates (AP 1370..1408), the {..,18,..} form
# reproduces all twelve exactly while the {..,17,..} form diverges by one day
# at AP 1404 (Nowruz 2025).  This module therefore uses the {..,18,..} form.
#
# Epoch.  1 Farvardin AP 1 == JDN 1948320 == 21 March 622 proleptic Gregorian
# (the equinox / classical Nowruz) == 18 March 622 Julian.  Some references
# instead cite "19 March 622 Julian" (JDN 1948321); anchoring there shifts
# every modern Nowruz one day late, so the equinox anchor is used here.  Gold:
# Nowruz AP 1403 == 2024-03-20 Gregorian.

_SOLAR_HIJRI_EPOCH_JDN = 1948320
_SOLAR_HIJRI_LEAP_RESIDUES = frozenset({1, 5, 9, 13, 18, 22, 26, 30})


def _solar_hijri_leap(year: int) -> bool:
    return year % 33 in _SOLAR_HIJRI_LEAP_RESIDUES


def _solar_hijri_leaps_before(year: int) -> int:
    """Leap years counted from AP year 1 through ``year`` (monotonic, and
    consistent for proleptic ``year <= 0`` so round-trips still hold)."""
    full, rem = divmod(year, 33)
    return full * 8 + sum(1 for r in _SOLAR_HIJRI_LEAP_RESIDUES if r <= rem)


def _solar_hijri_year_day(month: int, day: int) -> int:
    before = 31 * (month - 1) if month <= 7 else 186 + 30 * (month - 7)
    return before + day


def solar_hijri_to_jdn(year: int, month: int, day: int) -> int:
    """Arithmetic Solar Hijri (year, month, day) -> JDN.  Proleptic for
    years <= 0.  Arithmetic approximation -- see module note."""
    if not 1 <= month <= 12:
        raise CalendarRangeError(
            f"solar_hijri_arithmetic month {month} out of range for year "
            f"{year}; expected 1..12")
    if month <= 6:
        length = 31
    elif month <= 11:
        length = 30
    else:
        length = 30 if _solar_hijri_leap(year) else 29
    if not 1 <= day <= length:
        raise CalendarRangeError(
            f"solar_hijri_arithmetic day {day} out of range for "
            f"{year}-{month}; expected 1..{length}")
    return (_SOLAR_HIJRI_EPOCH_JDN + 365 * (year - 1)
            + _solar_hijri_leaps_before(year - 1)
            + _solar_hijri_year_day(month, day) - 1)


def solar_hijri_from_jdn(jdn: int) -> Tuple[int, int, int]:
    year = _year_containing(jdn, lambda y: solar_hijri_to_jdn(y, 1, 1),
                            (jdn - _SOLAR_HIJRI_EPOCH_JDN) // 366 + 1, 367)
    yday = jdn - solar_hijri_to_jdn(year, 1, 1) + 1
    if yday <= 186:
        month = (yday - 1) // 31 + 1
    else:
        month = (yday - 187) // 30 + 7
    day = yday - _solar_hijri_year_day(month, 1) + 1
    return year, month, day


# --------------------------------------------------------------------------
# Tabulated calendars: bounded event tables loaded from data files.
# --------------------------------------------------------------------------
# Some calendars are not arithmetic: their month (or year) starts are fixed by
# an astronomical criterion -- crescent visibility (Umm al-Qura, observed
# Hijri), a lunisolar new-moon/solar-term computation (Chinese), or an observed
# equinox -- then *published as an official table*.  Such a calendar is exact
# only within the tabulated range and has no rule to extrapolate beyond it.
#
# A ``TabulatedCalendar`` wraps one such table, loaded from a data file in
# ``chronologia/calendar_data/`` (see ``_load_tabulated``).  Each data row
# names one month start: ``year month leap jdn_start``.  ``leap`` flags an
# intercalary/leap month; internally a leap month following ordinary month M is
# addressed as month ``M + 100`` (so ordinary months keep their number 1..N and
# a leap month is unmistakably ``> 100`` -- e.g. Chinese leap month 6 is 106).
# This encoding is chosen over a 13-slot renumbering because it keeps every
# ordinary month's number stable across leap and common years (a leap year does
# not renumber month 7 to slot 8), which the downstream span builder relies on.
# The final row of every table is a *terminal sentinel*: the start of the month
# after the last tabulated one, so the last real month's length is known.  It is
# not itself an addressable month.
#
# Same ``to_jdn``/``from_jdn`` integer contract as :class:`Calendar`; both raise
# :class:`CalendarRangeError` (a ``ValueError``) outside the table, and the
# error carries the calendar's declared ``fallback`` key so a caller can degrade
# to a rule-based calendar (Umm al-Qura -> ``islamic_civil``).  Registry entries
# expose a ``basis`` attribute -- ``"tabulated"`` (observed/published table) or
# ``"reconstructed"`` (scholarly reconstruction with per-entry uncertainty) vs
# the default ``"exact"`` on arithmetic calendars -- which downstream span
# construction consumes to widen a span to its stated uncertainty.
#
# Considered for the tabulated family, not shipped (a table is only worth
# shipping if a downloaded canonical source pins *both* the rule/table and
# datable gold; inventing the gap is worse than the omission):
#
# * **Javanese** ``aboge`` / ``asapon`` kurup variants.  The 8-year windu leap
#   positions (355-day Jemawal/Dal/Jimakir) and the 120-year kurup -1-day
#   correction that distinguishes the two conventions are reported
#   inconsistently across sources, and no single canonical source pins each
#   variant's leap table together with datable civil gold conversions.  (This
#   reaffirms the exclusion already documented in the module header, now with
#   the tabulated mechanism available: the blocker is the data, not the code.)
# * **Observed Saudi Hijri** (``islamic_observed_sa``).  ``umm_al_qura`` already
#   carries the official Saudi civil table; a *sighting-announced* table that
#   differs from it would need a citable archive of the dates actually announced
#   by the Saudi authority.  No such archive is available as a downloadable
#   canonical record (only forums / aggregators), so it is not shipped rather
#   than scraped.
# * **Roman republican** (``roman_republican_bennett``, a reconstruction demo).
#   Bennett's pre-Julian chronology is downloadable, but for the showcase 46 BC
#   445-day "year of confusion" his own reconstruction states that "the
#   individual lengths of each [intercalary] month are not known"
#   (instonebrewer.com/.../chron_rom_cal.htm).  The canonical source therefore
#   does not pin the intra-year structure the demo requires, so a faithful table
#   cannot be transcribed without inventing it.  The Roman civil calendar's
#   ante-diem (Kalends/Nones/Ides) reckoning is in any case the province of the
#   dedicated ``roman`` construction, not this ``(year, month, day)`` hub.

_CALENDAR_DATA_DIR = os.path.join(os.path.dirname(__file__), "calendar_data")


class CalendarRangeError(ValueError):
    """Raised when a tabulated/reconstructed calendar is queried outside its
    table.  ``fallback`` names a rule-based calendar key the caller may degrade
    to (or ``None`` if none is appropriate)."""

    def __init__(self, message: str, fallback: Optional[str] = None):
        super().__init__(message)
        self.fallback = fallback


# Optional ephemeris providers: a registered callable extends a tabulated
# calendar beyond its shipped table.  Core ships none (a table is exact and
# self-contained); an application that has an ephemeris may register one.
_EVENT_PROVIDERS: Dict[str, Callable[[int, int], Optional[Tuple[int, int]]]] = {}


def register_event_provider(
        calendar_key: str,
        provider: Callable[[int, int], Optional[Tuple[int, int]]]) -> None:
    """Register an ephemeris ``provider`` extending the tabulated calendar
    ``calendar_key`` beyond its shipped table.

    ``provider(year, month)`` (``month`` in the same ``M``/``M+100`` encoding the
    table uses) returns ``(jdn_start, month_length)`` for a month the table does
    not cover, or ``None`` to decline (the calendar then raises
    :class:`CalendarRangeError` as usual).  This is the documented
    optional-ephemeris entry point; the core registry ships no providers, so a
    tabulated calendar is exact-and-bounded unless an application opts in.
    """
    _EVENT_PROVIDERS[calendar_key] = provider


def _month_field(month: int, leap: int) -> int:
    return month + 100 if leap else month


# --------------------------------------------------------------------------
# Field validation: month/day bounds derived from each calendar's own rules.
# --------------------------------------------------------------------------
# A calendar's legal ``(year, month, day)`` triples are exactly the ones its
# own ``from_jdn`` hands back, so the bounds are *derived* rather than tabled:
# a triple is legal iff it survives the JDN round trip
# ``from_jdn(to_jdn(y, m, d)) == (y, m, d)``.  That is the same law the
# property tests assert, so nothing that round-trips today can be rejected
# here, and every irregular case comes out right for free -- the Hebrew 13th
# month of a leap year, the 5/6-day Coptic/Ethiopic and Armenian/Egyptian
# epagomenal month, the French Republican complementary days, Badí'
# Ayyám-i-Há, ISO week 53, and the 0-based Maya uinal/kin positions.
#
# The fast path is one round trip.  Only when that fails does the slow path
# probe the neighbourhood to report the concrete valid range in the message.

_PROBE_DAYS = range(-1, 42)         # widest plausible day/kin span, plus edges


def _accepts(cal, year: int, month: int, day: int) -> bool:
    """Whether ``cal`` genuinely represents ``(year, month, day)``."""
    try:
        jdn = cal.to_jdn(year, month, day)
        return cal.from_jdn(jdn) == (year, month, day)
    except Exception:               # out of domain / out of table / overflow
        return False


def _valid_months(cal, year: int) -> List[int]:
    """Month numbers ``cal`` accepts in ``year`` (probed, error path only)."""
    return [m for m in range(-1, cal.month_count + 2)
            if any(_accepts(cal, year, m, d) for d in _PROBE_DAYS)]


def _valid_days(cal, year: int, month: int) -> List[int]:
    return [d for d in _PROBE_DAYS if _accepts(cal, year, month, d)]


def _range_text(values: List[int]) -> str:
    return f"{values[0]}..{values[-1]}"


def _validate_fields(cal, year: int, month: int, day: int) -> None:
    """Raise ``ValueError`` unless ``(year, month, day)`` is a real date.

    Silent-wrong is the failure this prevents: without it a typo such as
    month 99 or day 0 flows straight through the arithmetic and yields a
    confident, plausible-looking -- and wrong -- Gregorian instant.
    """
    if _accepts(cal, year, month, day):
        return
    months = _valid_months(cal, year)
    if not months:
        raise ValueError(
            f"{cal.key} year {year} is outside the calendar's domain")
    if month not in months:
        raise ValueError(
            f"{cal.key} month {month} out of range for year {year}; "
            f"expected {_range_text(months)}")
    days = _valid_days(cal, year, month)
    if not days:                    # defensive: month listed but no legal day
        raise ValueError(
            f"{cal.key} month {month} out of range for year {year}; "
            f"expected {_range_text(months)}")
    raise ValueError(
        f"{cal.key} day {day} out of range for {year}-{month}; "
        f"expected {_range_text(days)}")


# --------------------------------------------------------------------------
# Friendly object facade: CalendarDate (objects in, objects out).
# --------------------------------------------------------------------------
# The JDN plumbing above is the internal architecture; callers should never
# have to thread raw integers through it.  ``CalendarDate`` is the object a
# calendar hands back, and every ``Calendar``/``TabulatedCalendar`` grows a
# ``date(...)`` / ``from_astro(...)`` pair so a round trip stays in objects.


def _gregorian_jdn_of(moment) -> int:
    """Proleptic-Gregorian JDN of any ``.year/.month/.day``-bearing instant.

    Accepts an :class:`~chronologia.astrodate.AstroDate`, a ``datetime.date``
    or a ``datetime.datetime`` interchangeably (time-of-day is ignored) — the
    single coercion point behind every ``from_astro`` facade below.
    """
    return gregorian_to_jdn(moment.year, moment.month, moment.day)


@dataclass(frozen=True)
class CalendarDate:
    """A civil date under a named calendar — the object a calendar hands back.

    ``calendar`` is a registry key (``"hebrew"``, ``"julian"`` …); ``year``,
    ``month`` and ``day`` are that calendar's own numbering.  The
    :attr:`astro` property crosses to the shared timeline as an
    :class:`~chronologia.astrodate.AstroDate` (the Gregorian-proleptic instant
    of day 1..length of the named date).

    ``str(cd)`` is deliberately **numeric** — ``"hebrew 5786-07-01"``, never
    ``"1 Tishri 5786"``.  Turning month numbers into names is language-aware
    and belongs to the NLP layer; this core stays i18n-free, so the string
    form prints the registry key and the raw ``(year, month, day)`` only.
    """

    calendar: str
    year: int
    month: int
    day: int

    @property
    def astro(self):
        """The Gregorian-proleptic instant of this date, as an ``AstroDate``."""
        from chronologia.astrodate import AstroDate
        cal = CALENDARS[self.calendar]
        # validate first: without this an impossible date (31 Ramadan, Adar II
        # of a non-leap Hebrew year, month 0) would flow straight into to_jdn
        # and come back a confident, plausible-looking -- and WRONG -- Gregorian
        # instant, the exact silent-wrong Calendar.date()/validate() exists to
        # prevent.  CalendarDate (incl. from_json on untrusted data) is a second
        # door to the same arithmetic and must share the same gate.
        cal.validate(self.year, self.month, self.day)
        return AstroDate(*jdn_to_gregorian(
            cal.to_jdn(self.year, self.month, self.day)))

    def __str__(self) -> str:
        return f"{self.calendar} {self.year}-{self.month:02d}-{self.day:02d}"

    def to_json(self) -> dict:
        """A ``json.dumps``-ready dict envelope (see :meth:`from_json`)."""
        return {"type": "CalendarDate", "calendar": self.calendar,
                "year": self.year, "month": self.month, "day": self.day}

    @classmethod
    def from_json(cls, data: dict) -> "CalendarDate":
        """Rebuild a :class:`CalendarDate` from a :meth:`to_json` envelope."""
        if data.get("type") != "CalendarDate":
            raise ValueError(
                f"not a CalendarDate envelope: {data.get('type')!r}")
        return cls(data["calendar"], data["year"], data["month"], data["day"])


@dataclass(frozen=True)
class TabulatedCalendar:
    """A calendar whose month starts come from a bounded published table.

    Duck-compatible with :class:`Calendar` (``key``/``month_count``/``to_jdn``/
    ``from_jdn``/``epoch_jdn``/``basis``) so it registers in the same
    ``CALENDARS`` dict.  ``fallback`` is the rule-based calendar key carried by
    :class:`CalendarRangeError` on out-of-range access; ``coverage`` is a
    human-readable range string from the data file header.  Months are addressed
    in the ``M``/``M+100`` (ordinary/leap) encoding documented above.
    """

    key: str
    month_count: int
    starts: Tuple[int, ...]                    # ascending JDN of each month start
    labels: Tuple[Tuple[int, int], ...]        # (year, month-field) per start
    pos: Mapping[Tuple[int, int], int]         # (year, month-field) -> index
    basis: str = "tabulated"
    fallback: Optional[str] = None
    coverage: str = ""

    @property
    def epoch_jdn(self) -> int:
        return self.starts[0]

    def _length(self, idx: int) -> Optional[int]:
        if idx + 1 < len(self.starts):
            return self.starts[idx + 1] - self.starts[idx]
        return None                            # terminal sentinel: length unknown

    def to_jdn(self, year: int, month: int, day: int) -> int:
        idx = self.pos.get((year, month))
        if idx is not None:
            length = self._length(idx)
            if length is not None:
                if not 1 <= day <= length:
                    raise CalendarRangeError(
                        f"{self.key}: day {day} outside the tabulated month "
                        f"length ({length}) of {year}-{month}", self.fallback)
                return self.starts[idx] + day - 1
            # sentinel month has no tabulated length: try a provider, else raise
        provider = _EVENT_PROVIDERS.get(self.key)
        if provider is not None:
            got = provider(year, month)
            if got is not None:
                start, length = got
                if not 1 <= day <= length:
                    raise CalendarRangeError(
                        f"{self.key}: day {day} outside provider month length "
                        f"({length}) of {year}-{month}", self.fallback)
                return start + day - 1
        raise CalendarRangeError(
            f"{self.key}: ({year}, {month}) outside the tabulated range "
            f"[{self.coverage}]", self.fallback)

    def from_jdn(self, jdn: int) -> Tuple[int, int, int]:
        starts = self.starts
        if starts[0] <= jdn < starts[-1]:
            lo, hi = 0, len(starts) - 1
            while hi - lo > 1:                 # starts[idx] <= jdn < starts[idx+1]
                mid = (lo + hi) // 2
                if starts[mid] <= jdn:
                    lo = mid
                else:
                    hi = mid
            year, field = self.labels[lo]
            return year, field, jdn - starts[lo] + 1
        provider = _EVENT_PROVIDERS.get(self.key)
        if provider is not None and jdn >= starts[-1]:
            found = self._provider_from_jdn(provider, jdn)
            if found is not None:
                return found
        raise CalendarRangeError(
            f"{self.key}: JDN {jdn} outside the tabulated range "
            f"[{self.coverage}]", self.fallback)

    def _provider_from_jdn(self, provider, jdn):
        # Walk ordinary months forward from the sentinel until the one whose
        # span contains jdn; the provider defines month starts past the table.
        year, field = self.labels[-1]
        while True:
            got = provider(year, field)
            if got is None:
                return None
            start, length = got
            if start <= jdn < start + length:
                return year, field, jdn - start + 1
            if jdn < start:
                return None
            field, year = self._next_month(year, field)

    def _next_month(self, year: int, field: int) -> Tuple[int, int]:
        month = field - 100 if field > 100 else field
        if month >= self.month_count:
            return 1, year + 1
        return month + 1, year

    # -- friendly object facade (objects in, objects out) ------------------
    def date(self, year: int, month: int, day: int):
        """The Gregorian-proleptic instant of this calendar date (AstroDate).

        Object-returning sugar for ``to_jdn`` + ``jdn_to_gregorian``; raises
        :class:`CalendarRangeError` outside the table, exactly as ``to_jdn``.
        """
        from chronologia.astrodate import AstroDate
        return AstroDate(*jdn_to_gregorian(self.to_jdn(year, month, day)))

    def validate(self, year: int, month: int, day: int) -> None:
        """Raise unless ``(year, month, day)`` is a real date in the table.

        The table *is* the bound here, so this is ``to_jdn``'s own check: an
        unknown month or a day past the tabulated month length raises
        :class:`CalendarRangeError` (a ``ValueError``)."""
        self.to_jdn(year, month, day)

    def from_astro(self, moment) -> "CalendarDate":
        """The :class:`CalendarDate` this calendar assigns to an instant.

        ``moment`` is any ``AstroDate``/``date``/``datetime``; raises
        :class:`CalendarRangeError` when the instant is outside the table.
        """
        y, m, d = self.from_jdn(_gregorian_jdn_of(moment))
        return CalendarDate(self.key, y, m, d)


def _load_tabulated(filename: str) -> TabulatedCalendar:
    """Parse a ``calendar_data/*.tab`` file into a :class:`TabulatedCalendar`.

    File format (``# tabulated-calendar v1``): ``#``-prefixed header lines carry
    provenance and the ``key``/``basis``/``fallback``/``month_count``/
    ``coverage`` metadata as ``# name: value``; each data row is
    ``year month leap jdn_start`` (whitespace-separated integers).
    """
    path = os.path.join(_CALENDAR_DATA_DIR, filename)
    meta: Dict[str, str] = {}
    starts: list = []
    labels: list = []
    pos: Dict[Tuple[int, int], int] = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                name, sep, value = line[1:].strip().partition(":")
                if sep and name.strip() in ("key", "basis", "fallback",
                                            "month_count", "coverage"):
                    meta.setdefault(name.strip(), value.strip())
                continue
            year, month, leap, jdn = (int(x) for x in line.split()[:4])
            field = _month_field(month, leap)
            pos[(year, field)] = len(starts)
            starts.append(jdn)
            labels.append((year, field))
    if starts != sorted(starts):
        raise ValueError(f"{filename}: month starts are not ascending")
    return TabulatedCalendar(
        key=meta["key"],
        month_count=int(meta["month_count"]),
        starts=tuple(starts),
        labels=tuple(labels),
        pos=pos,
        basis=meta.get("basis", "tabulated"),
        fallback=meta.get("fallback") or None,
        coverage=meta.get("coverage", ""),
    )


umm_al_qura = _load_tabulated("umm_al_qura.tab")

# Equinox-tabulated variants (suffixed-variant convention).  A calendar key with
# an explicit suffix (``_2015``, ``_equinox``) is the observational/tabulated
# sibling of the arithmetic calendar of the same stem: the arithmetic
# ``bahai``/``french_republican`` entries (Gregorian-locked / Romme rules) stay
# exact and untouched, while ``badi_2015`` and ``french_republican_equinox``
# read published equinox tables.  Both share the tabulated month-start
# mechanism: the equinox fixes each year start and the regular intra-year
# structure (19-day months + Ayyám-i-Há; 30-day months + complementary days)
# fills in the month starts stored in the table.
badi_2015 = _load_tabulated("badi_2015.tab")
french_republican_equinox = _load_tabulated("french_republican_equinox.tab")

# Chinese lunisolar calendar (Hong Kong Observatory published conversion tables,
# 1901..2099).  A leap month following ordinary month M is addressed as month
# ``M + 100`` (leap-6 of 2025 -> month 106).  No arithmetic fallback: the
# lunisolar month starts are astronomical (new moon + principal solar term) and
# do not reduce to a rule, so out-of-range access raises with ``fallback=None``.
chinese = _load_tabulated("chinese.tab")


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

    ``basis`` classifies how exact the conversion is: ``"exact"`` (the default
    -- an arithmetic rule, no error bar), ``"tabulated"`` (fixed by a published
    observation table), or ``"reconstructed"`` (a scholarly reconstruction with
    an uncertainty).  Downstream span construction consumes ``basis`` to decide
    whether a resolved date is a point or carries a width; ``fallback`` (unused
    by arithmetic calendars) names a calendar key a bounded calendar degrades to
    out of range.  :class:`TabulatedCalendar` is the ``basis != "exact"``
    counterpart with the same attribute surface.
    Consumers building a :class:`~chronologia.astrodate.DateSpan` from a
    calendar date may seed the span's ``basis`` from this attribute and
    combine it with other inputs' bases via
    :func:`~chronologia.astrodate.combine_basis`; that wiring lives at
    the call sites, not here.
    """
    key: str
    month_count: int
    to_jdn: Callable[[int, int, int], int]
    from_jdn: Callable[[int], Tuple[int, int, int]]
    epoch_jdn: int
    basis: str = "exact"
    fallback: Optional[str] = None

    # -- friendly object facade (objects in, objects out) ------------------
    def date(self, year: int, month: int, day: int):
        """The Gregorian-proleptic instant of this calendar date (AstroDate).

        Object-returning sugar over the ``to_jdn`` + ``jdn_to_gregorian``
        plumbing, so ``CALENDARS["hebrew"].date(5786, 7, 1)`` yields the
        AstroDate directly instead of a bare JDN.

        Raises ``ValueError`` naming the valid range when ``month`` or ``day``
        is not a real field of this calendar in ``year``.
        """
        from chronologia.astrodate import AstroDate
        self.validate(year, month, day)
        return AstroDate(*jdn_to_gregorian(self.to_jdn(year, month, day)))

    def validate(self, year: int, month: int, day: int) -> None:
        """Raise ``ValueError`` unless ``(year, month, day)`` is a real date in
        this calendar; bounds are derived from the calendar's own arithmetic
        (see :func:`_validate_fields`)."""
        _validate_fields(self, year, month, day)

    def from_astro(self, moment) -> "CalendarDate":
        """The :class:`CalendarDate` this calendar assigns to an instant.

        ``moment`` is any ``AstroDate``/``date``/``datetime`` (the Gregorian
        instant); returns the matching civil date in this calendar's numbering.
        """
        y, m, d = self.from_jdn(_gregorian_jdn_of(moment))
        return CalendarDate(self.key, y, m, d)


CALENDARS: Dict[str, Union[Calendar, TabulatedCalendar]] = {
    # tabular/civil Hijri: a deterministic arithmetic rule, hence ``exact``
    # as a conversion; its ±1-day divergence from sighting-based observation
    # is a documented model caveat, not a basis class.
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
    "coptic": Calendar(
        "coptic", 13, coptic_to_jdn, coptic_from_jdn, _COPTIC_EPOCH_JDN),
    "ethiopian": Calendar(
        "ethiopian", 13, ethiopic_to_jdn, ethiopic_from_jdn,
        _ETHIOPIC_EPOCH_JDN),
    "berber": Calendar(
        "berber", 12, berber_to_jdn, berber_from_jdn,
        berber_to_jdn(1, 1, 1)),
    "revised_julian": Calendar(
        "revised_julian", 12, revised_julian_to_jdn, revised_julian_from_jdn,
        revised_julian_to_jdn(1, 1, 1)),
    "armenian": Calendar(
        "armenian", 13, armenian_to_jdn, armenian_from_jdn,
        _ARMENIAN_EPOCH_JDN),
    "egyptian": Calendar(
        "egyptian", 13, egyptian_to_jdn, egyptian_from_jdn,
        _EGYPTIAN_EPOCH_JDN),
    "mayan_long_count": Calendar(
        "mayan_long_count", 18, mayan_long_count_registry_to_jdn,
        mayan_long_count_registry_from_jdn, _MAYAN_EPOCH_JDN),
    "iso_week": Calendar(
        "iso_week", 53, iso_week_to_jdn, iso_week_from_jdn,
        iso_week_to_jdn(1, 1, 1)),
    "solar_hijri_arithmetic": Calendar(
        "solar_hijri_arithmetic", 12, solar_hijri_to_jdn, solar_hijri_from_jdn,
        _SOLAR_HIJRI_EPOCH_JDN),
    "umm_al_qura": umm_al_qura,
    "badi_2015": badi_2015,
    "french_republican_equinox": french_republican_equinox,
    "chinese": chinese,
}
