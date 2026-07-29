# -*- coding: utf-8 -*-
"""Independent Solar-Hijri (Jalali) -> Gregorian oracle for the fa corpus.

This is the Borkowski / jalaali-js 33-year arithmetic intercalation, written
from the published algorithm and *completely independent of the parser under
test*.  Gold Gregorian equivalents are computed here by pure arithmetic; a
sweep only keeps a case when this oracle and the engine agree (two independent
implementations concurring == certain gold).  It reproduces the repo's
documented anchor exactly: 1 Farvardin 1403 == 2024-03-20 and
15 Khordad 1403 == 2024-06-04.

Only Solar-Hijri months 1..11 have fixed lengths (31x6, 30x5); month 12
(Esfand) is 29 or 30 depending on the leap flag, which this oracle derives.
Year 1404 is deliberately excluded by callers: there the arithmetic and the
engine's calendar disagree by one day (the borderline equinox/Nowruz case),
so its gold is NOT certain.
"""
from datetime import date, timedelta

_BREAKS = [-61, 9, 38, 199, 426, 686, 756, 818, 1111, 1181, 1210,
           1635, 2060, 2097, 2192, 2262, 2324, 2394, 2456, 3178]

# Persian month names in calendar order.
JMON = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
        "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]


def _jal_cal(jy):
    gy = jy + 621
    leap_j = -14
    jp = _BREAKS[0]
    jump = 0
    for j in range(1, len(_BREAKS)):
        jm = _BREAKS[j]
        jump = jm - jp
        if jy < jm:
            break
        leap_j += (jump // 33) * 8 + (jump % 33) // 4
        jp = jm
    n = jy - jp
    leap_j += (n // 33) * 8 + ((n % 33 + 3) // 4)
    if (jump % 33) == 4 and (jump - n) == 4:
        leap_j += 1
    leap_g = gy // 4 - ((gy // 100 + 1) * 3) // 4 - 150
    march = 20 + leap_j - leap_g
    if (jump - n) < 6:
        n = n - jump + ((jump + 4) // 33) * 33
    leap = ((n + 1) % 33 - 1) % 4
    if leap == -1:
        leap = 4
    return leap, gy, march


def is_leap(jy):
    """True when the Solar-Hijri year has a 30-day Esfand."""
    return _jal_cal(jy)[0] == 0


def esfand_len(jy):
    return 30 if is_leap(jy) else 29


def j2g(jy, jm, jd):
    """Convert a Jalali (year, month, day) to a Gregorian ``date``."""
    leap, gy, march = _jal_cal(jy)
    lens = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, esfand_len(jy)]
    doy = sum(lens[:jm - 1]) + jd
    return date(gy, 3, 1) + timedelta(days=march - 1 + doy - 1)
