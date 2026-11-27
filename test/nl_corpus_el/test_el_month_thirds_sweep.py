# -*- coding: utf-8 -*-
"""αρχές / μέσα / τέλη + genitive month = early / mid / late third of that
named calendar month. With no year the parent month takes the year the month
alone takes (ruling 1, changed 26 November 2026): a month that holds the anchor
is this year's, a month that has ended before it is next year's (2018 for
January to May, 2017 for June to December). The third is pure timedelta arithmetic over the parent's [first, next)
edges, identical to the shipped ``test_nl_fuzzy_period`` convention but applied
to a *named* month rather than "του μήνα".
"""
from datetime import datetime

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end

A = datetime(2017, 6, 27, 13, 4)

GEN = {
    1: "ιανουαρίου", 2: "φεβρουαρίου", 3: "μαρτίου", 4: "απριλίου",
    5: "μαΐου", 6: "ιουνίου", 7: "ιουλίου", 8: "αυγούστου",
    9: "σεπτεμβρίου", 10: "οκτωβρίου", 11: "νοεμβρίου", 12: "δεκεμβρίου",
}
PART = {"αρχές": "early", "μέσα": "mid", "τέλη": "late"}


def _third_dt(y, mo, part):
    s = datetime(y, mo, 1)
    e = datetime(y + 1, 1, 1) if mo == 12 else datetime(y, mo + 1, 1)
    w = (e - s) / 3
    return {"early": (s, s + w), "mid": (s + w, s + 2 * w),
            "late": (s + 2 * w, e)}[part]


def _third(y, mo, part):
    lo, hi = _third_dt(y, mo, part)
    return AstroDate.from_datetime(lo), AstroDate.from_datetime(hi)


def _year(mo, part):
    """Year a bare part of month ``mo`` takes against the anchor ``A``."""
    y = A.year + (mo < A.month)
    # ruling 1 (26 November 2026): a part of a month is read as a span; in the
    # anchor's own month, a part that has ended at the anchor (early and mid
    # June 2017) is next year's, a part that holds it (late June) stays
    if mo == A.month and _third_dt(y, mo, part)[1] <= A:
        y += 1
    return y


_CASES = [
    # ruling 1 (changed 26 November 2026): a part of a month takes its month's year; a month that has ended at the anchor is next year's
    (f"{word} {GEN[mo]}", _year(mo, part), mo, part)
    for mo in range(1, 13) for word, part in PART.items()
]


@pytest.mark.parametrize("text,y,mo,part", _CASES)
def test_month_third_sweep(text, y, mo, part):
    assert start_end(text, A) == _third(y, mo, part)
