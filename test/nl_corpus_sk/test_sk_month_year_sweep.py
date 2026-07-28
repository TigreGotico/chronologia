# -*- coding: utf-8 -*-
"""Slovak nominative month + year: "marec 2020" names the whole month.

A bare nominative month name followed by a four-digit year is the everyday way
a Slovak speaker writes a calendar month ("január 2020", "december 2025").  The
span is the whole month: first day 00:00 up to the first of the following
month.  Expected bounds come from calendar arithmetic on ``datetime`` alone --
the parser is never consulted for the gold.
"""
import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end

#: nominative month names, index 1..12.
_NOM = [None, "január", "február", "marec", "apríl", "máj", "jún", "júl",
        "august", "september", "október", "november", "december"]

_YEARS = [2000, 2005, 2010, 2015, 2018, 2019, 2020, 2021, 2022, 2023,
          2024, 2025, 2027, 2030, 1999]


def _month_span(y, m):
    ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
    return AstroDate(y, m, 1), AstroDate(ny, nm, 1)


@pytest.mark.parametrize("year", _YEARS)
@pytest.mark.parametrize("m", range(1, 13))
def test_month_year(m, year):
    text = f"{_NOM[m]} {year}"
    assert start_end(text) == _month_span(year, m), text
