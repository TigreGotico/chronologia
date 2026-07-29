# -*- coding: utf-8 -*-
"""Second-pass sweep: named Russian civil holidays with explicit year, fresh
years far beyond round 1/2's coverage.

``test_ru_named_holiday_year_sweep`` (round 2) pinned name+year for
2018..2024; ``test_ru_civic_dates_sweep`` pinned the numeric day-month-year
reading for 2018..2023.  This file re-sweeps the NAME reading across 20 fresh
years (2025..2044) that neither prior file touches, so nothing duplicates.

Each name resolves to its fixed civil date in the stated year -- a one-day
span [date, date+1).  Gold is the literal statutory date (hand-verified),
never the parser.  "Праздник весны и труда" (1 May) is deliberately excluded:
its name is not bound by the engine (see the prep-month bug file for the
adjacent silent-year failure mode), so it is not swept here either.
"""
import pytest
from datetime import timedelta

from ._corpus import AstroDate, span, start

_NAMED = {
    "новый год": (1, 1),
    "рождество": (1, 7),
    "день защитника отечества": (2, 23),
    "международный женский день": (3, 8),
    "день победы": (5, 9),
    "день россии": (6, 12),
    "день народного единства": (11, 4),
}

# 20 fresh years, disjoint from round 1/2 (2018..2024)
_YEARS = tuple(range(2025, 2045))


def _cases():
    out = []
    for name, (m, d) in _NAMED.items():
        for y in _YEARS:
            out.append((f"{name} {y}", y, m, d))
    return out


_CASES = _cases()


@pytest.mark.parametrize("text,y,m,d", _CASES, ids=[c[0] for c in _CASES])
def test_named_holiday_with_year_fresh(text, y, m, d):
    assert start(text) == AstroDate(y, m, d), text
    assert span(text).width == timedelta(days=1)
