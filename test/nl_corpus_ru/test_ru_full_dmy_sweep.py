# -*- coding: utf-8 -*-
"""Full day-month-year sweep (ru), all twelve genitive months x years x forms.

Russian writes a date day-first with a genitive month name after the cardinal
day: "5 июня 2020".  This file sweeps a fixed set of days across every month
and several years, then exercises two idiomatic variants that also bind:

  * the genitive-ordinal day form  "3-го марта 2020"  (lit. "on the 3rd of...")
  * the trailing year-noun form    "5 июня 2020 года" (lit. "...of the year")

Each is a one-day span [date, date+1).  Gold is the literal calendar date,
computed independently.  Days are kept <= 28 so every (day, month) pair is
valid in every year.  Anchor 2017-06-27.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, start_end

_MONTHS_GEN = [None, "января", "февраля", "марта", "апреля", "мая", "июня",
               "июля", "августа", "сентября", "октября", "ноября", "декабря"]

_DAYS = (3, 10, 17, 24, 28)
_YEARS = (2018, 2019, 2020, 2021, 2023, 2025)


def _end(y, m, d):
    nxt = date(y, m, d) + timedelta(days=1)
    return AstroDate(nxt.year, nxt.month, nxt.day)


def _dmy_cases():
    out = []
    for m in range(1, 13):
        for d in _DAYS:
            for y in _YEARS:
                out.append((f"{d} {_MONTHS_GEN[m]} {y}", y, m, d))
    return out


_DMY = _dmy_cases()


@pytest.mark.parametrize("text,y,m,d", _DMY, ids=[c[0] for c in _DMY])
def test_full_dmy(text, y, m, d):
    st, en = start_end(text)
    assert st == AstroDate(y, m, d), text
    assert en == _end(y, m, d), text


# genitive-ordinal day form: "3-го марта 2020"
def _go_cases():
    out = []
    for m in range(1, 13):
        for d in (1, 15, 28):
            for y in (2019, 2020, 2021):
                out.append((f"{d}-го {_MONTHS_GEN[m]} {y}", y, m, d))
    return out


_GO = _go_cases()


@pytest.mark.parametrize("text,y,m,d", _GO, ids=[c[0] for c in _GO])
def test_genitive_ordinal_day(text, y, m, d):
    st, en = start_end(text)
    assert st == AstroDate(y, m, d), text
    assert en == _end(y, m, d), text


# trailing year-noun form: "5 июня 2020 года"
def _goda_cases():
    out = []
    for m in range(1, 13):
        for y in (2019, 2020, 2022):
            out.append((f"12 {_MONTHS_GEN[m]} {y} года", y, m, 12))
    return out


_GODA = _goda_cases()


@pytest.mark.parametrize("text,y,m,d", _GODA, ids=[c[0] for c in _GODA])
def test_trailing_year_noun(text, y, m, d):
    st, en = start_end(text)
    assert st == AstroDate(y, m, d), text
    assert en == _end(y, m, d), text
