# -*- coding: utf-8 -*-
"""Slovak day-ranges within a month: "od 5. do 12. júna", "medzi 3. a 8. novembrom".

Two framings name a closed run of days inside one month: "od D1. do D2.
<genitive-month>" and "medzi D1. a D2. <instrumental-month>".  The span runs
from D1 00:00 to the day after D2 (end-exclusive).  Without a year the month
takes the next-occurrence year: a month after the anchor's June stays in 2017,
one before it rolls to 2018 (June itself is left out to avoid the same-month
day ambiguity).  With an explicit year the roll is moot.  Bounds are computed
directly from the day pair.
"""
from datetime import date, timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end, ANCHOR

_GEN = [None, "januára", "februára", "marca", "apríla", "mája", "júna",
        "júla", "augusta", "septembra", "októbra", "novembra", "decembra"]
_INS = [None, "januárom", "februárom", "marcom", "aprílom", "májom", "júnom",
        "júlom", "augustom", "septembrom", "októbrom", "novembrom", "decembrom"]


def _roll_year(m):
    y = ANCHOR.year
    return y if m > ANCHOR.month else y + 1


def _range(y, m, d1, d2):
    lo = date(y, m, d1)
    hi = date(y, m, d2) + timedelta(days=1)
    return (AstroDate(lo.year, lo.month, lo.day),
            AstroDate(hi.year, hi.month, hi.day))


# (month, d1, d2); month != 6 so the year-roll is unambiguous.
_CASES = [(1, 1, 5), (2, 3, 7), (3, 10, 20), (4, 2, 9), (5, 4, 6),
          (7, 5, 12), (8, 1, 15), (9, 2, 9), (10, 1, 10), (11, 3, 8),
          (12, 5, 12)]


@pytest.mark.parametrize("m,d1,d2", _CASES)
def test_od_do_bare(m, d1, d2):
    text = f"od {d1}. do {d2}. {_GEN[m]}"
    assert start_end(text) == _range(_roll_year(m), m, d1, d2), text


@pytest.mark.parametrize("m,d1,d2", _CASES)
def test_medzi_a_bare(m, d1, d2):
    text = f"medzi {d1}. a {d2}. {_INS[m]}"
    assert start_end(text) == _range(_roll_year(m), m, d1, d2), text


@pytest.mark.parametrize("year", [2019, 2021, 2024])
@pytest.mark.parametrize("m,d1,d2", [(1, 1, 15), (6, 5, 12), (10, 1, 10)])
def test_od_do_with_year(m, d1, d2, year):
    text = f"od {d1}. do {d2}. {_GEN[m]} {year}"
    assert start_end(text) == _range(year, m, d1, d2), text
