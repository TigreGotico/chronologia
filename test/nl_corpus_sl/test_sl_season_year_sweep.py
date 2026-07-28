# -*- coding: utf-8 -*-
"""Season + year sweep (sl): meteorological three-month seasons.

pomlad = spring [Mar, Jun); poletje = summer [Jun, Sep); jesen = autumn
[Sep, Dec); zima = winter [Dec, next-Mar).  Winter straddles the year
boundary.  Gold is fixed month arithmetic computed here.  Anchor:
Tuesday 2017-06-27 13:04.
"""
import pytest

from ._corpus import AstroDate, start_end

# name -> (start_month, end_month, end_year_offset)
_SEASONS = {
    'pomlad': (3, 6, 0),
    'poletje': (6, 9, 0),
    'jesen': (9, 12, 0),
    'zima': (12, 3, 1),
}
_YEARS = [1900, 1955, 1999, 2016, 2020, 2050, 2088, 2101]

_CASES = [
    (f"{name} {y}", y, name) for y in _YEARS for name in _SEASONS
]


@pytest.mark.parametrize("text,y,name", _CASES)
def test_season_year(text, y, name):
    sm, em, eoff = _SEASONS[name]
    s, e = start_end(text)
    assert s == AstroDate(y, sm, 1)
    assert e == AstroDate(y + eoff, em, 1)
