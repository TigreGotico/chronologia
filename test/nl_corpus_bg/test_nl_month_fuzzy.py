"""Bulgarian fuzzy month parts ("early/mid/late March").

Order shape: prepositional: PART на MONTH (на = 'of').  The early/mid/late third of the month (a ~10-day
span), sliced by :func:`chronologia.subdivide`; the fuzzy word must be
consumed (no residue).  Anchor: Tue 2017-06-27.
"""
import pytest

from ._corpus import start_end, AstroDate


@pytest.mark.parametrize("text,s,e", [
    ('началото на март', AstroDate(2017, 3, 1, 0, 0), AstroDate(2017, 3, 11, 8, 0)),
    ('средата на март', AstroDate(2017, 3, 11, 8, 0), AstroDate(2017, 3, 21, 16, 0)),
    ('краят на март', AstroDate(2017, 3, 21, 16, 0), AstroDate(2017, 4, 1, 0, 0)),
])
def test_month_fuzzy(text, s, e):
    assert start_end(text) == (s, e)
