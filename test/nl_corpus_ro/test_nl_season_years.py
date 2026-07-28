# -*- coding: utf-8 -*-
"""Romanian meteorological seasons scoped to an explicit year.

Northern-hemisphere season -> month band (start month inclusive, end month
exclusive), as fixed by this locale:
  * primăvara : Mar 1 .. Jun 1
  * vara      : Jun 1 .. Sep 1
  * toamna    : Sep 1 .. Dec 1
  * iarna     : Dec 1 .. Mar 1 (of the following year)

Gold is the calendar band itself, computed here across a wide spread of years
(including the winter year-roll) and never read from the parser.
"""
import pytest

from ._corpus import start_end, AstroDate


# season -> (start month, end month, end-year offset)
_SEASON = {
    "primăvara": (3, 6, 0),
    "vara": (6, 9, 0),
    "toamna": (9, 12, 0),
    "iarna": (12, 3, 1),
}


def _cases():
    out = []
    for y in (1901, 1950, 1969, 1985, 1999, 2000, 2008, 2019,
              2020, 2021, 2025, 2033, 2048):
        for name, (sm, em, off) in _SEASON.items():
            out.append((f"{name} {y}", y, sm, y + off, em))
    return out


@pytest.mark.parametrize("text,sy,sm,ey,em", _cases())
def test_season_year(text, sy, sm, ey, em):
    s, e = start_end(text)
    assert s == AstroDate(sy, sm, 1), text
    assert e == AstroDate(ey, em, 1), text
