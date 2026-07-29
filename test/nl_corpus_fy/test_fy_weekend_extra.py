"""fy: further weekend references not in the base weekend block.

'ôfrûne wykein' = last weekend (the previous Sat-Sun).  'kommend wykein' =
the coming weekend, which from a mid-week (Tuesday) anchor is this week's
Sat-Sun (rel 0).  Spans from independent calendar arithmetic.
"""
from datetime import timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, span


def _weekend(rel):
    base = ANCHOR.replace(hour=0, minute=0, second=0, microsecond=0)
    sat = (base - timedelta(days=base.weekday())
           + timedelta(days=5) + timedelta(weeks=rel))
    end = sat + timedelta(days=2)
    return (AstroDate(sat.year, sat.month, sat.day),
            AstroDate(end.year, end.month, end.day))


@pytest.mark.parametrize("text,rel", [
    ('ôfrûne wykein', -1),
    ('kommend wykein', 0),
])
def test_weekend_ref(text, rel):
    sp = span(text)
    assert (sp.start, sp.end) == _weekend(rel)
