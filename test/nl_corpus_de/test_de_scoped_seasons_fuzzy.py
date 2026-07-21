"""German scoped ordinals ("die erste Woche des Oktober"), centuries/
millennia as scope units ("das dritte Jahrhundert", "das 21. Jahrhundert"),
half-periods ("die erste Hälfte von 2020"), hemisphere-aware seasons
(northern -- summer is Jun-Aug) and fuzzy month parts (Anfang/Mitte/Ende).
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, start, start_end, span, nomatch, AstroDate


# -- scoped ordinal weeks within a month ----------------------------------

def test_first_week_of_october():
    assert start_end("die erste woche des oktober 2020") == (
        AstroDate(2020, 10, 5), AstroDate(2020, 10, 12))


# -- centuries as scope units (ordinal-dot and spelled) -------------------

@pytest.mark.parametrize("text,y0,y1", [
    ("das dritte jahrhundert", 200, 300),
    ("das erste jahrhundert", 1, 101),
    ("das 21. jahrhundert", 2000, 2100),
    ("das 20. jahrhundert", 1900, 2000),
    ("das zweite jahrtausend", 1000, 2000),
])
def test_scope_units(text, y0, y1):
    assert start_end(text) == (AstroDate(y0, 1, 1), AstroDate(y1, 1, 1))


# -- half periods ---------------------------------------------------------

@pytest.mark.parametrize("text,s,e", [
    ("die erste hälfte von 2020", (2020, 1, 1), (2020, 7, 1)),
    ("die zweite hälfte von 2020", (2020, 7, 1), (2021, 1, 1)),
    ("die erste hälfte des jahrhunderts", (2000, 1, 1), (2050, 1, 1)),
])
def test_half_period(text, s, e):
    assert start_end(text) == (AstroDate(*s), AstroDate(*e))


# -- seasons (northern hemisphere: summer = Jun-Aug) ----------------------

@pytest.mark.parametrize("text,s,e", [
    ("sommer 2020", (2020, 6, 1), (2020, 9, 1)),
    ("frühling 2021", (2021, 3, 1), (2021, 6, 1)),
    ("winter 2020", (2020, 12, 1), (2021, 3, 1)),
    ("herbst 2019", (2019, 9, 1), (2019, 12, 1)),
])
def test_season_of_year(text, s, e):
    assert start_end(text) == (AstroDate(*s), AstroDate(*e))


@pytest.mark.parametrize("text,s,e", [
    ("nächster sommer", (2018, 6, 1), (2018, 9, 1)),
    ("nächster winter", (2017, 12, 1), (2018, 3, 1)),
    ("im herbst", (2017, 9, 1), (2017, 12, 1)),
])
def test_season_relative(text, s, e):
    assert start_end(text) == (AstroDate(*s), AstroDate(*e))


# -- fuzzy month parts: Anfang / Mitte / Ende -----------------------------

def test_anfang_juni():
    s = span("anfang juni")
    assert s.start == AstroDate(2017, 6, 1)
    assert s.end <= AstroDate(2017, 6, 15)


def test_ende_dezember():
    s = span("ende dezember")
    assert s.end == AstroDate(2018, 1, 1)
    assert s.start >= AstroDate(2017, 12, 15)


# -- adversarial: an ordinal with no scope is not a span ------------------

@pytest.mark.parametrize("text", ["die dritte", "erste woche"])
def test_incomplete_scope(text):
    from ._corpus import parse
    parse(text)   # must not raise
