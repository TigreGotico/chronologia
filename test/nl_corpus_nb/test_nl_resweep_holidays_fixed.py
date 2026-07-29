"""nb: fixed-date civil/Christian holidays bound by name, second-pass resweep.

``test_nl_national_holidays_2.py`` only exercises Arbeidernes dag /
Grunnlovsdagen bare-form plus one explicit year (2019). This file sweeps six
fixed-date holidays across 30 fresh years (2052-2081), gold hand-derived from
the statutory calendar date -- never read back from the engine.
"""
from datetime import timedelta

import pytest

from ._corpus import AstroDate, span, start

_HOLIDAYS = [
    ("nyttårsdag", 1, 1),
    ("arbeidernes dag", 5, 1),
    ("grunnlovsdag", 5, 17),
    ("julaften", 12, 24),
    ("første juledag", 12, 25),
    ("andre juledag", 12, 26),
]


def _cases():
    out = []
    for y in range(2052, 2082):
        for name, m, d in _HOLIDAYS:
            out.append((f"{name} {y}", y, m, d))
    return out


@pytest.mark.parametrize("text,y,m,d", _cases())
def test_fixed_holiday_resweep(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)
    assert span(text).width == timedelta(days=1)
