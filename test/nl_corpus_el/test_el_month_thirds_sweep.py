# -*- coding: utf-8 -*-
"""αρχές / μέσα / τέλη + genitive month = early / mid / late third of that
named calendar month. The parent month resolves within the anchor year
(2017); the third is pure timedelta arithmetic over the parent's [first, next)
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


def _third(y, mo, part):
    s = datetime(y, mo, 1)
    e = datetime(y + 1, 1, 1) if mo == 12 else datetime(y, mo + 1, 1)
    w = (e - s) / 3
    lo, hi = {"early": (s, s + w), "mid": (s + w, s + 2 * w),
              "late": (s + 2 * w, e)}[part]
    return AstroDate.from_datetime(lo), AstroDate.from_datetime(hi)


_CASES = [
    (f"{word} {GEN[mo]}", 2017, mo, part)
    for mo in range(1, 13) for word, part in PART.items()
]


@pytest.mark.parametrize("text,y,mo,part", _CASES)
def test_month_third_sweep(text, y, mo, part):
    assert start_end(text, A) == _third(y, mo, part)
