"""Czech fuzzy month parts ("early/mid/late March").

Order shape: Slavic genitive, no connector: PART MONTH(gen).  The early/mid/late third of the month (a ~10-day
span), sliced by :func:`chronologia.subdivide`; the fuzzy word must be
consumed (no residue).  With no year the part follows the month alone (next occurrence: a
month that has ended at the anchor is next year's; ruling 1, changed 26 November 2026).  Anchor: Tue 2017-06-27.
"""
import pytest

from ._corpus import start_end, AstroDate


@pytest.mark.parametrize("text,s,e", [
    # ruling 1 (changed 26 November 2026): a part of a month takes its month's year; March has ended at the anchor, so it is March 2018
    ('začátek března', AstroDate(2018, 3, 1, 0, 0), AstroDate(2018, 3, 11, 8, 0)),
    ('polovina března', AstroDate(2018, 3, 11, 8, 0), AstroDate(2018, 3, 21, 16, 0)),
    ('konec března', AstroDate(2018, 3, 21, 16, 0), AstroDate(2018, 4, 1, 0, 0)),
])
def test_month_fuzzy(text, s, e):
    assert start_end(text) == (s, e)
