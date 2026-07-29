"""fy: a bare weekday name resolves to its next occurrence (prefer-future),
a single-day span -- NOT a recurrence.  Anchor is a Tuesday, so the anchor's
own weekday (tiisdei) rolls a full week forward.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start, span, AstroDate


def _next_weekday(target):
    """target: Mon=0..Sun=6.  Prefer-future: today's weekday rolls +7."""
    base = ANCHOR.replace(hour=0, minute=0, second=0, microsecond=0)
    delta = (target - base.weekday()) % 7
    if delta == 0:
        delta = 7
    return base + timedelta(days=delta)


@pytest.mark.parametrize("text,target", [
    ('moandei', 0), ('tiisdei', 1), ('woansdei', 2), ('tongersdei', 3),
    ('freed', 4), ('sneon', 5), ('snein', 6),
])
def test_bare_weekday_next_occurrence(text, target):
    d = _next_weekday(target)
    assert start(text) == ad(d)
    assert span(text).width == timedelta(days=1)
