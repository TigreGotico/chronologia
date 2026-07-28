# -*- coding: utf-8 -*-
"""Oracle sweep: meteorological season + year (bg).

The four seasons tile three-month blocks: пролет = Mar-Jun, лято = Jun-Sep,
есен = Sep-Dec, зима = Dec(year)-Mar(year+1).  Gold is the fixed block for the
named year; the parser is never consulted.

Anchor 2017-06-27 (Tuesday, 13:04).
"""
import pytest

from ._corpus import AstroDate, span

# season -> (start_month, end_month, end_year_offset)
SEASONS = {
    "пролет": (3, 6, 0),
    "лято": (6, 9, 0),
    "есен": (9, 12, 0),
    "зима": (12, 3, 1),
}
YEARS = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]

CASES = [(name, y) for y in YEARS for name in SEASONS]


@pytest.mark.parametrize("name,y", CASES, ids=[f"{n} {y}" for n, y in CASES])
def test_season_year(name, y):
    sm, em, eyo = SEASONS[name]
    phrase = f"{name} {y}"
    s = span(phrase)
    assert s.start == AstroDate(y, sm, 1), phrase
    assert s.end == AstroDate(y + eyo, em, 1), phrase


@pytest.mark.parametrize("name,sm,em", [("лято", 6, 9), ("есен", 9, 12)])
def test_bare_season_anchor_year(name, sm, em):
    # no year -> the season block of the anchor year (2017); both of these
    # start on/after the anchor month so no roll ambiguity.
    s = span(name)
    assert s.start == AstroDate(2017, sm, 1), name
    assert s.end == AstroDate(2017, em, 1), name
