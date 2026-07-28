# -*- coding: utf-8 -*-
"""Meteorological seasons with an explicit year for Galician.

The four seasons are the three-month northern-hemisphere meteorological bands
(primavera=MAM, verán=JJA, outono=SON, inverno=DJF).  Naming a year pins the
band to that year; inverno famously opens in December of the named year and
runs into the following March.  Gold start/end are built by hand -- (year,
month, 1) and +3 months -- never by the parser.  Anchor Tue 2017-06-27."""
from datetime import datetime

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import parse, start_end, ad

# (season-word, first-month-of-band)
_SEASONS = [("primavera", 3), ("verán", 6), ("outono", 9), ("inverno", 12)]
_YEARS = [2018, 2019, 2020, 2021, 2022]

_CASES = [(s, m, y) for s, m in _SEASONS for y in _YEARS]


@pytest.mark.parametrize("season,month,year", _CASES)
def test_season_of_year(season, month, year):
    phrase = f"{season} de {year}"
    s, e = start_end(phrase)
    d0 = datetime(year, month, 1)
    assert s == ad(d0)
    assert e == ad(d0 + relativedelta(months=3))
    assert parse(phrase)[1] == ""
