# -*- coding: utf-8 -*-
"""Second-pass sweep: fixed-date Indonesian national/religious holidays across
20 fresh years, extending ``test_nl_holiday_ref.py`` (which only pins the
anchor year plus one explicit-year case each for ``natal``/``paskah``).

Tahun Baru (New Year, Jan 1) and Hari Natal/``natal`` (Christmas, Dec 25) are
fixed-Gregorian-date holidays, so gold is trivial independent arithmetic --
verified correct by probing all 20 years before writing this file. Years
chosen avoid every year already exercised elsewhere in the id corpus
(2017/2018/2020/2019/2020 anchor+sweep years).

Hari Buruh (Labour Day, May 1) and Hari Kemerdekaan (Independence Day, Aug 17)
are NOT wired into the id holiday registry at all: bare mentions return no
match, and appending a year mis-resolves to the *whole calendar year* instead
of the single named day (the digits are consumed as a bare-year span and the
holiday name is left stranded). Pinned below as strict xfails with the
correct single-day gold, not swept, since they do not currently work for any
year. Anchor: mission Tuesday 2017-06-27 13:04.
"""
from datetime import datetime, timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import parse, span, start

A = datetime(2017, 6, 27, 13, 4)

_YEARS = [1985, 1995, 2021, 2022, 2023, 2024, 2025, 2026, 2028, 2029,
          2031, 2032, 2033, 2034, 2035, 2036, 2037, 2038, 2039, 2040]


def _cases():
    out = []
    for y in _YEARS:
        out.append((f"tahun baru {y}", AstroDate(y, 1, 1)))
        out.append((f"hari natal {y}", AstroDate(y, 12, 25)))
        out.append((f"natal {y}", AstroDate(y, 12, 25)))
    return out


@pytest.mark.parametrize("text,ymd", _cases())
def test_fixed_holiday_fresh_years(text, ymd):
    assert start(text, A) == ymd
    assert span(text, A).width == timedelta(days=1)


# -- unregistered holidays: bare form doesn't fold forward at all -------------
_UNREGISTERED_BARE = [
    ("hari buruh", AstroDate(2018, 5, 1)),        # next May 1 on/after anchor
    ("hari kemerdekaan", AstroDate(2017, 8, 17)),  # next Aug 17 on/after anchor
]


@pytest.mark.parametrize("text,gold", _UNREGISTERED_BARE)
def test_unregistered_holiday_bare_should_fold(text, gold):
    assert start(text, A) == gold


_UNREGISTERED_YEAR = [
    ("hari buruh 2022", AstroDate(2022, 5, 1)),
    ("hari kemerdekaan 2022", AstroDate(2022, 8, 17)),
]


@pytest.mark.parametrize("text,gold", _UNREGISTERED_YEAR)
def test_unregistered_holiday_with_year_should_be_single_day(text, gold):
    s = span(text, A)
    assert s.start == gold
    assert s.width == timedelta(days=1)
