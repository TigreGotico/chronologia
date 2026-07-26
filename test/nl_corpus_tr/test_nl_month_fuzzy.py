"""Turkish fuzzy month parts ("early/mid/late March").

Order shape: postposed possessive: MONTH PART (ay başı/ortası/sonu).  The early/mid/late third of the month (a ~10-day
span), sliced by :func:`chronologia.subdivide`; the fuzzy word must be
consumed (no residue).  Anchor: 2026-07-15.
"""
import pytest

from ._corpus import start_end, AstroDate


@pytest.mark.parametrize("text,s,e", [
    ('mart başı', AstroDate(2026, 3, 1, 0, 0), AstroDate(2026, 3, 11, 8, 0)),
    ('mart ortası', AstroDate(2026, 3, 11, 8, 0), AstroDate(2026, 3, 21, 16, 0)),
    ('mart sonu', AstroDate(2026, 3, 21, 16, 0), AstroDate(2026, 4, 1, 0, 0)),
])
def test_month_fuzzy(text, s, e):
    assert start_end(text) == (s, e)
