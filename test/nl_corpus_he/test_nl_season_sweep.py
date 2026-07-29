# -*- coding: utf-8 -*-
"""Meteorological-band seasons with an explicit year, across many years.
Northern-hemisphere bands: אביב (spring) Mar-Jun, קיץ (summer) Jun-Sep,
סתיו (autumn) Sep-Dec, חורף (winter) Dec-Mar(+1).  Gold by arithmetic."""
import pytest

from ._corpus import AstroDate, start_end

_YEARS = (1955, 1975, 1995, 2011, 2029)

# name -> (start_month, end_month, end_year_delta)
_SEASONS = {
    "אביב": (3, 6, 0),
    "קיץ": (6, 9, 0),
    "סתיו": (9, 12, 0),
    "חורף": (12, 3, 1),
}


def _cases():
    out = []
    for y in _YEARS:
        for name, (sm, em, dy) in _SEASONS.items():
            out.append((f"{name} {y}", y, sm, y + dy, em))
    return out


@pytest.mark.parametrize("text,sy,sm,ey,em", _cases())
def test_season(text, sy, sm, ey, em):
    ss, ee = start_end(text)
    assert ss == AstroDate(sy, sm, 1)
    assert ee == AstroDate(ey, em, 1)
