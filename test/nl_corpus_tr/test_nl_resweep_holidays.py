# -*- coding: utf-8 -*-
"""RESWEEP: Turkish fixed-Gregorian-date holidays with explicit year, ×20
fresh years.

Every holiday swept here is a fixed Gregorian month/day regardless of year
(no lunar/Islamic or equinox-dependent holiday is included, since those need
a published table per year rather than pure arithmetic -- see
``test_nl_holiday_ref.py`` for those, gold from Umm al-Qura tables).  Gold is
independent construction: ``AstroDate(year, month, day)``, span one day.

Surfaces and their fixed dates (see
``chronologia/holiday_data/i18n/well_known.tab``):
  yılbaşı (New Year)                                -> 1 Jan
  sevgililer günü (Valentine's Day)                 -> 14 Feb
  ulusal egemenlik ve çocuk bayramı (Nat'l Sov./Children's Day) -> 23 Apr
  atatürk'ü anma gençlik ve spor bayramı (Youth/Sports Day)     -> 19 May
  zafer bayramı (Victory Day)                       -> 30 Aug
  cadılar bayramı (Halloween)                       -> 31 Oct
  cumhuriyet bayramı (Republic Day)                 -> 29 Oct
  noel (Christmas)                                  -> 25 Dec

Years are disjoint from every year already used for these holidays in
``test_nl_national_holidays_2.py`` and ``test_nl_holiday_ref.py``.
Anchor: Tuesday 2017-06-27 13:04 (explicit years, so the anchor is inert).
"""
from datetime import datetime, timedelta

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import span, start

A = datetime(2017, 6, 27, 13, 4)

_FIXED = {
    "yılbaşı": (1, 1),
    "sevgililer günü": (2, 14),
    "ulusal egemenlik ve çocuk bayramı": (4, 23),
    "atatürk'ü anma gençlik ve spor bayramı": (5, 19),
    "zafer bayramı": (8, 30),
    "cadılar bayramı": (10, 31),
    "cumhuriyet bayramı": (10, 29),
    "noel": (12, 25),
}

_YEARS = [1900, 1915, 1928, 1937, 1949, 1958, 1966, 1973, 1982, 1991,
          1997, 2003, 2009, 2014, 2021, 2029, 2036, 2041, 2047, 2053]


def _cases():
    out = []
    for name, (m, d) in _FIXED.items():
        for y in _YEARS:
            out.append((f"{name} {y}", y, m, d))
    return out


@pytest.mark.parametrize("text,y,m,d", _cases())
def test_fixed_holiday_explicit_year_resweep(text, y, m, d):
    assert start(text, A) == AstroDate(y, m, d)
    assert span(text, A).width == timedelta(days=1)
