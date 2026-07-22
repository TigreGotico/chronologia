# -*- coding: utf-8 -*-
"""The weekend -- this/next/last, a two-day Saturday-Sunday span.

Saturday-Sunday of the anchor's week, shifted a whole week per the relative
marker.  Expected spans come from independent calendar arithmetic -- never
pinned from the engine.  Week start index 5 (Saturday)."""
from datetime import timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, span

_SIDX = 5


def _expected(rel):
    base = ANCHOR.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = base - timedelta(days=(base.weekday() - _SIDX) % 7)
    sat = week_start + timedelta(days=(5 - _SIDX) % 7) + timedelta(weeks=rel)
    end = sat + timedelta(days=2)
    return (AstroDate(sat.year, sat.month, sat.day),
            AstroDate(end.year, end.month, end.day))


CASES = [
    ('آخر هفته', 0),
    ('آخر هفته آینده', 1),
    ('این آخر هفته', 0),
]


@pytest.mark.parametrize("text,rel", CASES)
def test_weekend(text, rel):
    sp = span(text)
    assert (sp.start, sp.end) == _expected(rel)
