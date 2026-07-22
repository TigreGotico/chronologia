"""Wave 2 -- the weekend: this/next/last weekend, a named two-day span.

The Saturday-Sunday of the anchor's week, shifted a whole week per the
relative marker.  Expected spans come from independent calendar
arithmetic against this corpus's anchor -- never by pinning the parser.
"""
from datetime import timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, span


def _expected(rel):
    base = ANCHOR.replace(hour=0, minute=0, second=0, microsecond=0)
    sat = (base - timedelta(days=base.weekday())
           + timedelta(days=5) + timedelta(weeks=rel))
    end = sat + timedelta(days=2)
    return (AstroDate(sat.year, sat.month, sat.day),
            AstroDate(end.year, end.month, end.day))


CASES = [
    ('denne helga', 0),
    ('neste helg', 1),
]


@pytest.mark.parametrize("text,rel", CASES)
def test_weekend(text, rel):
    sp = span(text)
    assert (sp.start, sp.end) == _expected(rel)
