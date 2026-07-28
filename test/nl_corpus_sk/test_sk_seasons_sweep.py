# -*- coding: utf-8 -*-
"""Slovak meteorological seasons + year: "jar 2020", "zima 2019".

Northern-hemisphere meteorological seasons: jar (spring) Mar-May, leto
(summer) Jun-Aug, jeseň (autumn) Sep-Nov, zima (winter) Dec-Feb.  Each names
a three-month span; winter straddles the year end.  A bare season falls in the
anchor's own year.  Bounds are fixed month firsts, computed here directly.
"""
import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end, ANCHOR

# season -> (start_month, span_months)
_SEASON = {"jar": (3, 3), "leto": (6, 3), "jeseň": (9, 3), "zima": (12, 3)}


def _season_span(name, y):
    sm, n = _SEASON[name]
    em = sm + n
    ey = y
    if em > 12:
        em -= 12
        ey += 1
    return AstroDate(y, sm, 1), AstroDate(ey, em, 1)


@pytest.mark.parametrize("year", [2017, 2018, 2019, 2020, 2021, 2022,
                                  2023, 2024, 2025, 2000, 2010, 2030])
@pytest.mark.parametrize("name", list(_SEASON))
def test_season_year(name, year):
    text = f"{name} {year}"
    assert start_end(text) == _season_span(name, year), text


@pytest.mark.parametrize("name", list(_SEASON))
def test_season_bare_current_year(name):
    """A bare season names it in the anchor's own year."""
    assert start_end(name) == _season_span(name, ANCHOR.year), name
