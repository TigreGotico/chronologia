"""Turkish fuzzy month parts ("early/mid/late March").

Order shape: postposed possessive: MONTH PART (ay başı/ortası/sonu).  The early/mid/late third of the month (a ~10-day
span), sliced by :func:`chronologia.subdivide`; the fuzzy word must be
consumed (no residue).  With no year the part follows the month alone (next occurrence: a
month that has ended at the anchor is next year's; ruling 1, changed 26 November 2026).  Anchor: 2026-07-15.
"""
import pytest

from ._corpus import start_end, AstroDate


@pytest.mark.parametrize("text,s,e", [
    # ruling 1 (changed 26 November 2026): a part of a month takes its month's year; March has ended at the anchor, so it is March 2027
    ('mart başı', AstroDate(2027, 3, 1, 0, 0), AstroDate(2027, 3, 11, 8, 0)),
    ('mart ortası', AstroDate(2027, 3, 11, 8, 0), AstroDate(2027, 3, 21, 16, 0)),
    ('mart sonu', AstroDate(2027, 3, 21, 16, 0), AstroDate(2027, 4, 1, 0, 0)),
])
def test_month_fuzzy(text, s, e):
    assert start_end(text) == (s, e)
