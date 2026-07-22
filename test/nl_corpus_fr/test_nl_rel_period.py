"""French calendar-relative periods (next/last/this week/month/year) and
the weekend as a named two-day span. Calendar-aligned one-unit widths, hand
-derived against the Tuesday 2017-06-27 anchor.
"""
import pytest

from ._corpus import start_end, nomatch, AstroDate


@pytest.mark.parametrize("text,s,e", [
    ('la semaine prochaine', AstroDate(2017, 7, 3), AstroDate(2017, 7, 10)),
    ('la semaine dernière', AstroDate(2017, 6, 19), AstroDate(2017, 6, 26)),
    ('cette semaine', AstroDate(2017, 6, 26), AstroDate(2017, 7, 3)),
    ('le mois prochain', AstroDate(2017, 7, 1), AstroDate(2017, 8, 1)),
    ('le mois dernier', AstroDate(2017, 5, 1), AstroDate(2017, 6, 1)),
    ('ce mois', AstroDate(2017, 6, 1), AstroDate(2017, 7, 1)),
    ("l'année prochaine", AstroDate(2018, 1, 1), AstroDate(2019, 1, 1)),
    ("l'année dernière", AstroDate(2016, 1, 1), AstroDate(2017, 1, 1)),
    ('ce week-end', AstroDate(2017, 7, 1), AstroDate(2017, 7, 3)),
    ('le week-end prochain', AstroDate(2017, 7, 8), AstroDate(2017, 7, 10)),
    ('le week-end dernier', AstroDate(2017, 6, 24), AstroDate(2017, 6, 26)),
])
def test_rel_period_and_weekend(text, s, e):
    assert start_end(text) == (s, e)


def test_bare_marker_is_not_a_period():
    nomatch('prochaine')
