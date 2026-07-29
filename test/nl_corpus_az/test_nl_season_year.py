# -*- coding: utf-8 -*-
"""Meteorological seasons + year, and season deixis, in Azerbaijani.

Season month-spans (independent arithmetic):
    yaz   (spring)  Mar 1 .. Jun 1
    yay   (summer)  Jun 1 .. Sep 1
    payız (autumn)  Sep 1 .. Dec 1
    qış   (winter)  Dec 1 .. Mar 1 (of the following year)

Anchor 2017-06-27 sits inside "yay 2017", so the demonstrative gold below is
the ordinary this/next/last reading a native speaker would give.
"""
from datetime import datetime
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end

A = datetime(2017, 6, 27, 13, 4)

# start-month, end-(year-offset, month)
_SEASON = {
    "yaz": (3, (0, 6)),
    "yay": (6, (0, 9)),
    "payız": (9, (0, 12)),
    "qış": (12, (1, 3)),
}


@pytest.mark.parametrize("y", [1918, 1969, 1999, 2000, 2018, 2020, 2027, 2030])
@pytest.mark.parametrize("season", ["yaz", "yay", "payız", "qış"])
def test_season_with_year(season, y):
    sm, (eo, em) = _SEASON[season]
    s, e = start_end("%s %d" % (season, y), A)
    assert s == AstroDate(y, sm, 1)
    assert e == AstroDate(y + eo, em, 1)


# Deixis: (text) -> (start_year, start_month, end_year, end_month)
_DEIXIS = [
    ("bu yaz", 2017, 3, 2017, 6),
    ("bu yay", 2017, 6, 2017, 9),
    ("bu payız", 2017, 9, 2017, 12),
    ("bu qış", 2017, 12, 2018, 3),
    ("gələn yaz", 2018, 3, 2018, 6),
    ("gələn yay", 2018, 6, 2018, 9),
    ("gələn payız", 2017, 9, 2017, 12),
    ("gələn qış", 2017, 12, 2018, 3),
    ("keçən yaz", 2017, 3, 2017, 6),
    ("keçən yay", 2016, 6, 2016, 9),
    ("keçən payız", 2016, 9, 2016, 12),
    ("keçən qış", 2016, 12, 2017, 3),
    ("ötən yay", 2016, 6, 2016, 9),
    ("ötən qış", 2016, 12, 2017, 3),
]


@pytest.mark.parametrize("text,sy,sm,ey,em", _DEIXIS)
def test_season_deixis(text, sy, sm, ey, em):
    s, e = start_end(text, A)
    assert s == AstroDate(sy, sm, 1)
    assert e == AstroDate(ey, em, 1)
