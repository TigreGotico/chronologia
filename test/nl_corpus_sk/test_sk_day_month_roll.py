# -*- coding: utf-8 -*-
"""Slovak bare day-of-month "5. júna": the next future occurrence.

Without a year a Slovak speaker means the next time that calendar day comes
round.  Against the Tuesday-2017-06-27 anchor, a (day, month) still ahead of
(or on) the anchor stays in 2017; one already past rolls into 2018.  The gold
is that roll rule applied by ``date`` arithmetic, independent of the parser.
"""
from datetime import date, timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end, ANCHOR

_GEN = [None, "januára", "februára", "marca", "apríla", "mája", "júna",
        "júla", "augusta", "septembra", "októbra", "novembra", "decembra"]

_ANCHOR_D = ANCHOR.date()


def _roll(m, d):
    y = _ANCHOR_D.year
    if date(y, m, d) < _ANCHOR_D:
        y += 1
    start = date(y, m, d)
    end = start + timedelta(days=1)
    return (AstroDate(start.year, start.month, start.day),
            AstroDate(end.year, end.month, end.day))


# one representative day per month plus the anchor-boundary trio in June.
_DM = [(1, 1), (15, 2), (9, 3), (10, 4), (15, 5),
       (26, 6), (27, 6), (28, 6),
       (7, 7), (30, 8), (20, 9), (12, 10), (3, 11), (25, 12), (31, 12)]


@pytest.mark.parametrize("d,m", _DM)
def test_bare_day_month_rolls(d, m):
    text = f"{d}. {_GEN[m]}"
    assert start_end(text) == _roll(m, d), text
