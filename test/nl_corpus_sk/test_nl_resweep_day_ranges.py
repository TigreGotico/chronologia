# -*- coding: utf-8 -*-
"""Second-pass sweep: Slovak day-ranges "od D. do D. <gen-month> <year>" /
"medzi D. a D. <ins-month> <year>", fresh day-pairs, months and years.

test_sk_ranges_sweep.py covers the bare-year (roll) form for one day-pair per
month plus a small explicit-year grid (3 day-pairs x 3 years). This sweep
always carries an explicit year and uses a fresh day-pair per month (none
overlapping the earlier file's pairs) across four fresh years. The span runs
from D1 00:00 to the day after D2 (end-exclusive); bounds are plain ``date``
arithmetic, independent of the parser."""
from datetime import date, timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end

_GEN = [None, "januára", "februára", "marca", "apríla", "mája", "júna",
        "júla", "augusta", "septembra", "októbra", "novembra", "decembra"]
_INS = [None, "januárom", "februárom", "marcom", "aprílom", "májom", "júnom",
        "júlom", "augustom", "septembrom", "októbrom", "novembrom", "decembrom"]

_YEARS = (2016, 2022, 2026, 2028)

# (month, d1, d2); day-pairs distinct from test_sk_ranges_sweep.py's grid.
_CASES = [(1, 7, 20), (2, 10, 18), (3, 5, 22), (4, 12, 27), (5, 2, 14),
          (6, 3, 19), (7, 9, 25), (8, 6, 21), (9, 4, 16), (10, 8, 28),
          (11, 1, 13), (12, 10, 24)]


def _range(y, m, d1, d2):
    lo = date(y, m, d1)
    hi = date(y, m, d2) + timedelta(days=1)
    return (AstroDate(lo.year, lo.month, lo.day),
            AstroDate(hi.year, hi.month, hi.day))


@pytest.mark.parametrize("year", _YEARS)
@pytest.mark.parametrize("m,d1,d2", _CASES)
def test_od_do_with_year_fresh(m, d1, d2, year):
    text = f"od {d1}. do {d2}. {_GEN[m]} {year}"
    assert start_end(text) == _range(year, m, d1, d2), text


@pytest.mark.parametrize("year", _YEARS)
@pytest.mark.parametrize("m,d1,d2", _CASES)
def test_medzi_a_with_year_fresh(m, d1, d2, year):
    text = f"medzi {d1}. a {d2}. {_INS[m]} {year}"
    assert start_end(text) == _range(year, m, d1, d2), text
