"""Second-pass resweep: intra-month day ranges with an explicit trailing
year ("5-12 <month> <year>", "1 to 10 <month> <year>") swept across all 12
months and a spread of years, with two different day-pairs per month to
vary the range width.

``test_nl_day_range_year.py`` proves the year/month-lending mechanism works
at all (a handful of hand-picked examples); this file sweeps the surface
across the full calendar and several years so every month's boundary
arithmetic (28/29/30/31-day widths) is independently exercised.  Gold is
plain ``date`` arithmetic -- the day-after-the-end civil date, never the
parser's own output.
"""
from datetime import date, timedelta

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import start_end

_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5,
    "june": 6, "july": 7, "august": 8, "september": 9, "october": 10,
    "november": 11, "december": 12,
}

_YEARS = (2010, 2013, 2016, 2019, 2022, 2025)

# (start day, end day) pairs -- kept within every month's shortest length (28)
_PAIRS = ((1, 10), (5, 12), (15, 20))


def _cases():
    out = []
    for year in _YEARS:
        for mname, m in _MONTHS.items():
            for d1, d2 in _PAIRS:
                out.append((f"{d1}-{d2} {mname} {year}", year, m, d1, d2))
    return out


@pytest.mark.parametrize("text,year,month,d1,d2", _cases())
def test_day_range_dash_year_sweep(text, year, month, d1, d2):
    s = date(year, month, d1)
    e = date(year, month, d2) + timedelta(days=1)
    assert start_end(text) == (AstroDate(s.year, s.month, s.day),
                               AstroDate(e.year, e.month, e.day))


def _cases_to():
    out = []
    for year in _YEARS:
        for mname, m in _MONTHS.items():
            d1, d2 = 1, 10
            out.append((f"{d1} to {d2} {mname} {year}", year, m, d1, d2))
    return out


@pytest.mark.parametrize("text,year,month,d1,d2", _cases_to())
def test_day_range_to_year_sweep(text, year, month, d1, d2):
    s = date(year, month, d1)
    e = date(year, month, d2) + timedelta(days=1)
    assert start_end(text) == (AstroDate(s.year, s.month, s.day),
                               AstroDate(e.year, e.month, e.day))
