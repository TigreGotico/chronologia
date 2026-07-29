# -*- coding: utf-8 -*-
"""sv (second-pass resweep): year-qualified intra-month day ranges.

``test_sv_day_ranges_sweep.py`` swept bare (no-year) ranges with day pairs
``(5,12),(3,8),(1,15),(10,20),(14,22)`` across all months, relying on
prefer-future to pick the year. ``test_sv_day_range_year.py`` pinned exactly
one year-qualified example. This resweep takes fresh day pairs
``(2,9),(6,18),(11,25),(20,28),(4,10)`` -- none reused from the first sweep
-- crossed with explicit years 2022-2026 across all 12 months, in both the
bare-hyphen and "från N till M" forms. The gold span is [D1, D2] inclusive,
so the exclusive end is D2+1, computed by INDEPENDENT date arithmetic.

Anchor Tuesday 2017-06-27 13:04 (irrelevant here since every phrase carries
an explicit year).
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import AstroDate, start_end, parse

_MONTHS = {
    1: "januari", 2: "februari", 3: "mars", 4: "april", 5: "maj", 6: "juni",
    7: "juli", 8: "augusti", 9: "september", 10: "oktober", 11: "november",
    12: "december",
}
_PAIRS = [(2, 9), (6, 18), (11, 25), (20, 28), (4, 10)]
_YEARS = [2022, 2023, 2024, 2025, 2026]
_FORMS = [
    lambda d1, d2, m, y: f"{d1}-{d2} {m} {y}",
    lambda d1, d2, m, y: f"från {d1} till {d2} {m} {y}",
]


def _build():
    cases = []
    for mo in range(1, 13):
        for d1, d2 in _PAIRS:
            for yr in _YEARS:
                gs = AstroDate(yr, mo, d1)
                e = datetime(yr, mo, d2) + timedelta(days=1)
                ge = AstroDate(e.year, e.month, e.day)
                for form in _FORMS:
                    cases.append((form(d1, d2, _MONTHS[mo], yr), gs, ge))
    return cases


_CASES = _build()


@pytest.mark.parametrize("text,gs,ge", _CASES, ids=[c[0] for c in _CASES])
def test_day_range_year_resweep(text, gs, ge):
    assert start_end(text) == (gs, ge)
    assert parse(text)[1] == ""
