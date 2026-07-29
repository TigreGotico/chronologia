# -*- coding: utf-8 -*-
"""RESWEEP: Turkish seasons ("<season> <year>"), fresh years disjoint from
``test_tr_season_sweep.py``'s [1999, 2012, 2019, 2025, 2033].

Meteorological season edges: ilkbahar = Mar-Jun, yaz = Jun-Sep, sonbahar =
Sep-Dec, kış = Dec-(next) Mar. Anchor: 2017-06-27.
"""
from datetime import datetime

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import start_end

A = datetime(2017, 6, 27, 13, 4)

_SEASON = {
    "ilkbahar": (3, 6, 0),
    "yaz": (6, 9, 0),
    "sonbahar": (9, 12, 0),
    "kış": (12, 3, 1),
}

_YEARS = [1908, 1921, 1944, 1963, 1979, 1992, 2006, 2017, 2038, 2049]


def _season_span(name, y):
    sm, em, dy = _SEASON[name]
    return AstroDate(y, sm, 1), AstroDate(y + dy, em, 1)


def _cases():
    out = []
    for name in _SEASON:
        for y in _YEARS:
            out.append((f"{name} {y}", name, y))
    return out


@pytest.mark.parametrize("text,name,y", _cases())
def test_season_with_year_resweep(text, name, y):
    assert start_end(text, A) == _season_span(name, y)
