# -*- coding: utf-8 -*-
"""Oracle sweep: SEASON YEAR (meteorological, N-hemisphere as the engine models
Arabic).  الربيع=MAM, الصيف=JJA, الخريف=SON, الشتاء=DJF (Dec of the named year
through the following March).  Gold by independent arithmetic."""
from datetime import date

import pytest

from ._corpus import AstroDate, start_end

# season -> (start month, end-exclusive (year_offset, month))
SEASONS = {
    "الربيع": (3, (0, 6)),
    "الصيف": (6, (0, 9)),
    "الخريف": (9, (0, 12)),
    "الشتاء": (12, (1, 3)),
}


def _cases():
    out = []
    for name, (sm, (yo, em)) in SEASONS.items():
        for y in (2018, 2019, 2020, 2021):
            s = date(y, sm, 1)
            e = date(y + yo, em, 1)
            out.append((f"{name} {y}", s, e))
    return out


@pytest.mark.parametrize("text,s,e", _cases())
def test_season_year_sweep(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(s.year, s.month, s.day)
    assert ee == AstroDate(e.year, e.month, e.day)
