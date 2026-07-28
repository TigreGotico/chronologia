# -*- coding: utf-8 -*-
"""Oracle sweep: bare month + year (bg).

"март 2019" spans the whole calendar month: [year-month-1, next-month-1).
Gold is pure relativedelta arithmetic over every (month, year) pair; the
parser is never consulted.

Anchor 2017-06-27 (Tuesday, 13:04).
"""
import pytest

from ._corpus import AstroDate, span

MONTHS = ["", "януари", "февруари", "март", "април", "май", "юни", "юли",
          "август", "септември", "октомври", "ноември", "декември"]
YEARS = [2018, 2019, 2021, 2023, 2025, 2030, 2020, 2022, 2024, 2026]

CASES = [(m, y) for y in YEARS for m in range(1, 13)]


@pytest.mark.parametrize("m,y", CASES, ids=[f"{MONTHS[m]} {y}" for m, y in CASES])
def test_month_year(m, y):
    phrase = f"{MONTHS[m]} {y}"
    s = span(phrase)
    assert s.start == AstroDate(y, m, 1), phrase
    ey, em = (y + 1, 1) if m == 12 else (y, m + 1)
    assert s.end == AstroDate(ey, em, 1), phrase
