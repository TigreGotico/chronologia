# -*- coding: utf-8 -*-
"""Oracle sweep: a bare season word resolves within the anchor's own season
year.  الربيع/الصيف/الخريف wrap inside 2017; الشتاء (DJF) opens Dec 2017 and
closes March 2018.  Gold by independent arithmetic against the anchor year."""
from datetime import date

import pytest

from ._corpus import ANCHOR, AstroDate, start_end

# season -> (start month, (end year offset, end month))
BARE = {
    "الربيع": (3, (0, 6)),
    "الصيف": (6, (0, 9)),
    "الخريف": (9, (0, 12)),
    "الشتاء": (12, (1, 3)),
}


def _cases():
    y = ANCHOR.year
    out = []
    for name, (sm, (yo, em)) in BARE.items():
        out.append((name, date(y, sm, 1), date(y + yo, em, 1)))
    return out


@pytest.mark.parametrize("text,s,e", _cases())
def test_bare_season_sweep(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(s.year, s.month, s.day)
    assert ee == AstroDate(e.year, e.month, e.day)
