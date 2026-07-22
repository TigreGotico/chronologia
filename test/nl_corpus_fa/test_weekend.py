# -*- coding: utf-8 -*-
"""The weekend -- this/next/last, a two-day span.

Persian rests Thursday-Friday, declared as the ``weekend_start`` fact (3 ==
Thursday); the week itself starts Saturday (index 5).  The weekend is the
two days from the anchor week's Thursday, shifted a whole week per the
relative marker.  Expected spans come from independent calendar arithmetic
against this corpus's anchor -- never pinned from the engine."""
from datetime import timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, span

_WEEK_START = 5      # Saturday
_WEEKEND_START = 3   # Thursday (Persian Thu-Fri weekend)


def _expected(rel):
    base = ANCHOR.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = base - timedelta(days=(base.weekday() - _WEEK_START) % 7)
    first = week_start + timedelta(days=(_WEEKEND_START - _WEEK_START) % 7) \
        + timedelta(weeks=rel)
    end = first + timedelta(days=2)
    return (AstroDate(first.year, first.month, first.day),
            AstroDate(end.year, end.month, end.day))


CASES = [
    ('آخر هفته', 0),          # this weekend
    ('آخر هفته آینده', 1),    # next weekend
    ('این آخر هفته', 0),      # this weekend (demonstrative)
]


@pytest.mark.parametrize("text,rel", CASES)
def test_weekend(text, rel):
    sp = span(text)
    assert (sp.start, sp.end) == _expected(rel)
