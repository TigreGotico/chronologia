"""Occitan calendar-relative periods (next/last/this week/month/year) and
the weekend as a named two-day span. Calendar-aligned one-unit widths, hand
-derived against the Tuesday 2017-06-27 anchor.
"""
import pytest

from ._corpus import start_end, nomatch, AstroDate


@pytest.mark.parametrize("text,s,e", [
    ('la setmana que ven', AstroDate(2017, 7, 3), AstroDate(2017, 7, 10)),
    ('la setmana passada', AstroDate(2017, 6, 19), AstroDate(2017, 6, 26)),
    ('lo mes passat', AstroDate(2017, 5, 1), AstroDate(2017, 6, 1)),
    ("l'an passat", AstroDate(2016, 1, 1), AstroDate(2017, 1, 1)),
    ('aquesta dimenjada', AstroDate(2017, 7, 1), AstroDate(2017, 7, 3)),
    ('la dimenjada que ven', AstroDate(2017, 7, 8), AstroDate(2017, 7, 10)),
    ('aquesta setmana', AstroDate(2017, 6, 26), AstroDate(2017, 7, 3)),
    ('lo mes que ven', AstroDate(2017, 7, 1), AstroDate(2017, 8, 1)),
    ("l'an que ven", AstroDate(2018, 1, 1), AstroDate(2019, 1, 1)),
    ('la dimenjada passada', AstroDate(2017, 6, 24), AstroDate(2017, 6, 26)),
])
def test_rel_period_and_weekend(text, s, e):
    assert start_end(text) == (s, e)


def test_bare_marker_is_not_a_period():
    nomatch('que ven')
