# -*- coding: utf-8 -*-
"""SECOND-PASS resweep: Polish holidays NOT covered by
``test_pl_holiday_year_sweep.py`` (which sweeps nowy rok / trzech króli /
wszystkich świętych / boże narodzenie / wigilia / walentynki / halloween /
wielkanoc / poniedziałek wielkanocny / wielki piątek across 2020-2025).

This module adds four FIXED-date state/religious holidays --
Święto Pracy (May 1), Święto Konstytucji 3 Maja (May 3), Wniebowzięcie
(Aug 15), Święto Niepodległości (Nov 11) -- swept across TWENTY fresh years
(2010-2019 and 2026-2035, none overlapping the first-pass 2020-2025 window).

It also documents two known engine gaps as strict xfails with independently
correct gold: "boże ciało" (Corpus Christi, Easter + 60 days by the Western
computus) and "drugi dzień świąt" / "drugi dzień bożego narodzenia" (Boxing
Day, Dec 26) do not resolve against an explicit year -- the engine falls back
to a bare-year parse and leaves the holiday phrase as unconsumed residual
text.

Anchor: Tuesday 2017-06-27 13:04.
"""
from datetime import date, timedelta

import pytest
from dateutil.easter import easter

from ._corpus import AstroDate, parse, span, start

_FIXED = {
    "święto pracy": (5, 1),
    "święto konstytucji 3 maja": (5, 3),
    "wniebowzięcie": (8, 15),
    "święto niepodległości": (11, 11),
}

#: fresh years -- disjoint from the first-pass 2020-2025 window.
_YEARS = list(range(2010, 2020)) + list(range(2026, 2036))


def _cases():
    out = []
    for y in _YEARS:
        for h, (m, d) in _FIXED.items():
            out.append((f"{h} {y}", date(y, m, d)))
    return out


_CASES = _cases()


@pytest.mark.parametrize("text,gold", _CASES, ids=[c[0] for c in _CASES])
def test_holiday_year_resweep(text, gold):
    assert start(text) == AstroDate(gold.year, gold.month, gold.day)
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text,gold", _CASES[::13], ids=[c[0] for c in _CASES[::13]])
def test_holiday_resweep_is_one_day(text, gold):
    assert span(text).width == timedelta(days=1)


# -- known gaps: correct gold, engine does not bind these against a year ---

_GAP_YEARS = (2011, 2018, 2027, 2033)


def _boze_cialo_gap_cases():
    out = []
    for y in _GAP_YEARS:
        gold = easter(y) + timedelta(days=60)
        out.append((f"boże ciało {y}", date(gold.year, gold.month, gold.day)))
    return out


_BOZE_CIALO_GAPS = _boze_cialo_gap_cases()


@pytest.mark.xfail(strict=True, reason="known pl gap: 'boże ciało' + explicit "
                    "year does not bind -- engine falls back to a bare-year "
                    "parse and leaves the phrase as residual text")
@pytest.mark.parametrize("text,gold", _BOZE_CIALO_GAPS, ids=[c[0] for c in _BOZE_CIALO_GAPS])
def test_boze_cialo_year_gap(text, gold):
    assert start(text) == AstroDate(gold.year, gold.month, gold.day)
    assert parse(text)[1] == ""


_BOXING_DAY_GAPS = [(f"drugi dzień świąt {y}", date(y, 12, 26)) for y in _GAP_YEARS] + \
    [(f"drugi dzień bożego narodzenia {y}", date(y, 12, 26)) for y in _GAP_YEARS]


@pytest.mark.xfail(strict=True, reason="known pl gap: Boxing Day idioms + "
                    "explicit year do not bind -- engine falls back to a "
                    "bare-year parse and leaves the phrase as residual text")
@pytest.mark.parametrize("text,gold", _BOXING_DAY_GAPS, ids=[c[0] for c in _BOXING_DAY_GAPS])
def test_boxing_day_year_gap(text, gold):
    assert start(text) == AstroDate(gold.year, gold.month, gold.day)
    assert parse(text)[1] == ""
