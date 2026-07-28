# -*- coding: utf-8 -*-
""""a primavera de 2019", "o inverno de 2024": a named season pinned to an
explicit year.

Meteorological seasons, northern hemisphere, three whole months each:

    primavera : Mar 1 .. Jun 1
    verão     : Jun 1 .. Sep 1
    outono    : Sep 1 .. Dec 1
    inverno   : Dec 1 (named year) .. Mar 1 (following year)

Winter is the wrap-around case: "o inverno de 2019" opens in December 2019 and
closes at the start of March 2020, so its end year is the named year plus one.
Every edge is computed from that table; the parser supplies no gold.

[[EP vs BP]]: season names and this three-month meteorological reading are
shared by both norms.  The definite article ("a primavera de", "o verão de")
is the ordinary EP form and is optional; the bare "primavera de 2019" parses
just the same.  Anchor 2017-06-27 is immaterial once the year is explicit.
"""
import pytest

from ._corpus import AstroDate, start_end

#: season -> (start month, span in months)
_SEASON = {"primavera": 3, "verão": 6, "outono": 9, "inverno": 12}


def _edges(season, year):
    sm = _SEASON[season]
    s = AstroDate(year, sm, 1)
    em = sm + 3
    ey = year
    if em > 12:
        em -= 12
        ey += 1
    return s, AstroDate(ey, em, 1)


def _cases():
    out = []
    for season in _SEASON:
        for year in (2018, 2019, 2021, 2024, 2030):
            for lead in ("a " if season in ("primavera",) else "o ", ""):
                out.append((f"{lead}{season} de {year}", season, year))
    return out


@pytest.mark.parametrize("text,season,year", _cases())
def test_season_of_explicit_year(text, season, year):
    gs, ge = _edges(season, year)
    s, e = start_end(text)
    assert s == gs, f"{text!r} start {s}"
    assert e == ge, f"{text!r} end {e}"


def test_winter_wraps_into_the_next_year():
    s, e = start_end("o inverno de 2019")
    assert s == AstroDate(2019, 12, 1)
    assert e == AstroDate(2020, 3, 1)
