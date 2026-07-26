"""Slovak fuzzy month parts ("early/mid/late March").

Order shape: Slavic genitive, no connector: PART MONTH(gen).  The early/mid/late third of the month (a ~10-day
span), sliced by :func:`chronologia.subdivide`; the fuzzy word must be
consumed (no residue).  Anchor: Tue 2017-06-27.
"""
import pytest

from ._corpus import start_end, AstroDate


@pytest.mark.parametrize("text,s,e", [
    ('začiatok marca', AstroDate(2017, 3, 1, 0, 0), AstroDate(2017, 3, 11, 8, 0)),
    ('polovica marca', AstroDate(2017, 3, 11, 8, 0), AstroDate(2017, 3, 21, 16, 0)),
    ('koniec marca', AstroDate(2017, 3, 21, 16, 0), AstroDate(2017, 4, 1, 0, 0)),
])
def test_month_fuzzy(text, s, e):
    assert start_end(text) == (s, e)
