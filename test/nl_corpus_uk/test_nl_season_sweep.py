# -*- coding: utf-8 -*-
"""Meteorological season + year sweep (uk), northern hemisphere.

весна = Mar-Jun, літо = Jun-Sep, осінь = Sep-Dec, зима = Dec(Y)-Mar(Y+1).
Each edge is the first day of the boundary month, derived independently of the
parser.  Anchor Tue 2017-06-27 13:04.
"""
import pytest

from ._corpus import AstroDate, start_end

# name -> (start_month, end_month, end_year_offset)
_SEASONS = {
    "весна": (3, 6, 0),
    "літо": (6, 9, 0),
    "осінь": (9, 12, 0),
    "зима": (12, 3, 1),
}

_YEARS = range(2015, 2031)

_CASES = []
for _name, (_sm, _em, _off) in _SEASONS.items():
    for _y in _YEARS:
        _CASES.append((f"{_name} {_y}", _y, _sm, _y + _off, _em))


@pytest.mark.parametrize("phrase,sy,sm,ey,em", _CASES)
def test_season(phrase, sy, sm, ey, em):
    s, e = start_end(phrase)
    assert s == AstroDate(sy, sm, 1), phrase
    assert e == AstroDate(ey, em, 1), phrase


@pytest.mark.parametrize("text,s,e", [
    # Genitive singular ("весни", "літа", "осені", "зими") per *Український
    # правопис* (2019) declension tables; mirrors the ru fix for the same
    # gap.  "весна" (2nd decl., hard a-stem) -> gen. весни; "літо" (2nd decl.
    # neuter) -> gen. літа; "осінь" (3rd decl., soft) -> gen./dat./loc. all
    # осені; "зима" (hard a-stem) -> gen. зими.  No collision: uk unit_year
    # ("рік") never uses these forms.
    ("весни 2027", AstroDate(2027, 3, 1), AstroDate(2027, 6, 1)),
    ("літа 2027", AstroDate(2027, 6, 1), AstroDate(2027, 9, 1)),
    ("осені 2027", AstroDate(2027, 9, 1), AstroDate(2027, 12, 1)),
    ("зими 2027", AstroDate(2027, 12, 1), AstroDate(2028, 3, 1)),
    # controls: nominative unchanged
    ("весна 2027", AstroDate(2027, 3, 1), AstroDate(2027, 6, 1)),
])
def test_season_genitive_case(text, s, e):
    ss, ee = start_end(text)
    assert ss == s and ee == e
