# -*- coding: utf-8 -*-
"""Second-pass oracle re-sweep: SEASON YEAR, fresh years disjoint from
``test_nl_season_year_sweep`` (2018-2021).  الربيع=MAM, الصيف=JJA,
الخريف=SON, الشتاء=DJF (Dec of the named year through the following March).
Independent arithmetic gold."""
from datetime import date

import pytest

from ._corpus import AstroDate, start_end

SEASONS = {
    "الربيع": (3, (0, 6)),
    "الصيف": (6, (0, 9)),
    "الخريف": (9, (0, 12)),
    "الشتاء": (12, (1, 3)),
}

YEARS = (1965, 1979, 1988, 1996, 2005, 2013, 2027, 2038)


def _cases():
    out = []
    for name, (sm, (yo, em)) in SEASONS.items():
        for y in YEARS:
            s = date(y, sm, 1)
            e = date(y + yo, em, 1)
            out.append((f"{name} {y}", s, e))
    return out


@pytest.mark.parametrize("text,s,e", _cases())
def test_season_year_resweep(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(s.year, s.month, s.day)
    assert ee == AstroDate(e.year, e.month, e.day)
