"""Romanian calendar-relative periods (next/last/this week/month/year) and
the weekend as a named two-day span. Calendar-aligned one-unit widths, hand
-derived against the Tuesday 2017-06-27 anchor.
"""
import pytest

from ._corpus import start_end, nomatch, AstroDate


@pytest.mark.parametrize("text,s,e", [
    ('săptămâna viitoare', AstroDate(2017, 7, 3), AstroDate(2017, 7, 10)),
    ('săptămâna trecută', AstroDate(2017, 6, 19), AstroDate(2017, 6, 26)),
    ('luna viitoare', AstroDate(2017, 7, 1), AstroDate(2017, 8, 1)),
    ('luna trecută', AstroDate(2017, 5, 1), AstroDate(2017, 6, 1)),
    ('luna aceasta', AstroDate(2017, 6, 1), AstroDate(2017, 7, 1)),
    ('anul viitor', AstroDate(2018, 1, 1), AstroDate(2019, 1, 1)),
    ('anul trecut', AstroDate(2016, 1, 1), AstroDate(2017, 1, 1)),
    ('acest weekend', AstroDate(2017, 7, 1), AstroDate(2017, 7, 3)),
    ('weekendul viitor', AstroDate(2017, 7, 8), AstroDate(2017, 7, 10)),
])
def test_rel_period_and_weekend(text, s, e):
    assert start_end(text) == (s, e)


def test_bare_marker_is_not_a_period():
    nomatch('viitoare')
