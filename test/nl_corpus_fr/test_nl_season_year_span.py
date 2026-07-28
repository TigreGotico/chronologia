# -*- coding: utf-8 -*-
"""Season + explicit year, full span, over several years (fr).

French seasons here are meteorological and month-aligned on the northern
hemisphere: printemps = [Mar, Jun), été = [Jun, Sep), automne = [Sep, Dec),
hiver = [Dec, next-Mar).  This file pins the *entire* span (both edges) for
each season across many years and for the several written forms a French
speaker uses -- bare ("printemps 2019"), with article ("le printemps 2019",
"l'été 2020") and with the partitive "de" ("l'été de 2020", "au printemps de
2019").

Expected edges are built here from the month-alignment rule, not read from the
parser.  Anchor Tuesday 2017-06-27 13:04 only fixes the locale; every case
names its own year.
"""
import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end


# season -> (start-month, end-month, end-year-offset)
_SEASON = {
    "printemps": (3, 6, 0),
    "été": (6, 9, 0),
    "automne": (9, 12, 0),
    "hiver": (12, 3, 1),
}

_YEARS = [2018, 2019, 2020, 2021, 2022, 2023, 2025]


def _expected(season, year):
    sm, em, eyo = _SEASON[season]
    return AstroDate(year, sm, 1), AstroDate(year + eyo, em, 1)


# article-carrying forms, keyed by the elision the season triggers
def _forms(season):
    art = "l'" if season in ("été", "automne", "hiver") else "le "
    prep = "au " if season == "printemps" else ("en " if season == "hiver"
                                                else "en ")
    return [
        f"{season} {{y}}",            # bare
        f"{art}{season} {{y}}",       # with definite article
        f"{art}{season} de {{y}}",    # partitive "de"
    ]


def _cases():
    out = []
    for season in _SEASON:
        for tmpl in _forms(season):
            for y in _YEARS:
                out.append((tmpl.format(y=y), season, y))
    return out


@pytest.mark.parametrize("text,season,year", _cases())
def test_season_year_full_span(text, season, year):
    want = _expected(season, year)
    got = start_end(text)
    assert got == want, f"{text!r} -> {got}, want {want}"
