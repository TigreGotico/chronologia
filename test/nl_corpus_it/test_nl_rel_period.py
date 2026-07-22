"""Italian calendar-relative periods (next/last/this week/month/year) and
the weekend as a named two-day span. Calendar-aligned one-unit widths, hand
-derived against the Tuesday 2017-06-27 anchor.
"""
import pytest

from ._corpus import start_end, nomatch, AstroDate


@pytest.mark.parametrize("text,s,e", [
    ('la settimana prossima', AstroDate(2017, 7, 3), AstroDate(2017, 7, 10)),
    ('la settimana scorsa', AstroDate(2017, 6, 19), AstroDate(2017, 6, 26)),
    ('questa settimana', AstroDate(2017, 6, 26), AstroDate(2017, 7, 3)),
    ('il mese prossimo', AstroDate(2017, 7, 1), AstroDate(2017, 8, 1)),
    ('il mese scorso', AstroDate(2017, 5, 1), AstroDate(2017, 6, 1)),
    ('questo mese', AstroDate(2017, 6, 1), AstroDate(2017, 7, 1)),
    ("l'anno prossimo", AstroDate(2018, 1, 1), AstroDate(2019, 1, 1)),
    ('lo scorso anno', AstroDate(2016, 1, 1), AstroDate(2017, 1, 1)),
    ('questo fine settimana', AstroDate(2017, 7, 1), AstroDate(2017, 7, 3)),
    ('il fine settimana prossimo', AstroDate(2017, 7, 8), AstroDate(2017, 7, 10)),
    ('il prossimo weekend', AstroDate(2017, 7, 8), AstroDate(2017, 7, 10)),
])
def test_rel_period_and_weekend(text, s, e):
    assert start_end(text) == (s, e)


def test_bare_marker_is_not_a_period():
    nomatch('prossima')
