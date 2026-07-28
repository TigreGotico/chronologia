# -*- coding: utf-8 -*-
"""Turkish seasons (meteorological bands) -- bare, with year, and deictic.

The engine uses meteorological season edges: ilkbahar = Mar-Jun, yaz =
Jun-Sep, sonbahar = Sep-Dec, kış = Dec-(next) Mar.  Bare season resolves in
the anchor's own calendar year; "SEASON YYYY" pins the year.  Winter straddles
the year boundary, so its end is the following March.  Anchor: 2017-06-27.
"""
from datetime import datetime

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import start_end

A = datetime(2017, 6, 27, 13, 4)

# start-month, end-(month, +years) for each season.
_SEASON = {
    "ilkbahar": (3, 6, 0),
    "yaz": (6, 9, 0),
    "sonbahar": (9, 12, 0),
    "kış": (12, 3, 1),
}


def _season_span(name, y):
    sm, em, dy = _SEASON[name]
    return AstroDate(y, sm, 1), AstroDate(y + dy, em, 1)


def _year_cases():
    out = []
    for name in _SEASON:
        for y in (1999, 2012, 2019, 2025, 2033):
            out.append((f"{name} {y}", name, y))
    return out


@pytest.mark.parametrize("text,name,y", _year_cases())
def test_season_with_year(text, name, y):
    assert start_end(text, A) == _season_span(name, y)


@pytest.mark.parametrize("name", list(_SEASON))
def test_bare_season_current_year(name):
    # bare season resolves within the anchor's calendar year (2017).
    assert start_end(name, A) == _season_span(name, 2017)


# Deictic season, hand-verified against the anchor (summer 2017):
#   bu <season>     -> the current-year instance
#   gelecek <season>-> the next occurrence after the anchor
#   geçen <season>  -> the previous occurrence before the anchor
@pytest.mark.parametrize("text,s,e", [
    ("bu yaz", AstroDate(2017, 6, 1), AstroDate(2017, 9, 1)),
    ("gelecek yaz", AstroDate(2018, 6, 1), AstroDate(2018, 9, 1)),
    ("geçen kış", AstroDate(2016, 12, 1), AstroDate(2017, 3, 1)),
    ("gelecek kış", AstroDate(2017, 12, 1), AstroDate(2018, 3, 1)),
    ("geçen sonbahar", AstroDate(2016, 9, 1), AstroDate(2016, 12, 1)),
])
def test_deictic_season(text, s, e):
    assert start_end(text, A) == (s, e)
