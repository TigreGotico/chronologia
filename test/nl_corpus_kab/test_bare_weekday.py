# -*- coding: utf-8 -*-
"""A bare weekday -- no marker -- names its next strictly-future occurrence.

The same prefer-future reckoning as an explicit "next": when the anchor is
already that weekday the span is seven days out.  A day-wide span; expected
values from independent arithmetic against this corpus's anchor."""
from datetime import timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, span


def _expected(idx):
    base = ANCHOR.replace(hour=0, minute=0, second=0, microsecond=0)
    ahead = (idx - base.weekday()) % 7 or 7
    s = base + timedelta(days=ahead)
    e = s + timedelta(days=1)
    return AstroDate(s.year, s.month, s.day), AstroDate(e.year, e.month, e.day)


CASES = [
    ('lǧemɛa', 4),
    ('letnayen', 0),
]


@pytest.mark.parametrize("text,idx", CASES)
def test_bare_weekday(text, idx):
    sp = span(text)
    assert (sp.start, sp.end) == _expected(idx)
