"""Spelled ordinal day of the month -- the ordinary spoken date.

Slovak puts the day in the genitive of the ordinal beside a genitive month
name (JULS SAV, Morfologia slovenskeho jazyka), and declines both elements of
a compound day.

Expected values are plain calendar facts about the corpus anchor, never the
parser's own output.
"""
import pytest

from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, nomatch, span, start


@pytest.mark.parametrize("text,y,m,d", [
    ('tretieho decembra', 2017, 12, 3),
    ('prvého januára', 2018, 1, 1),
    ('desiateho novembra', 2017, 11, 10),
    ('dvadsiateho decembra', 2017, 12, 20),
])
def test_spelled_ordinal_day(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


@pytest.mark.parametrize("text", [
    'tretieho decembra',
    'prvého januára',
])
def test_spelled_ordinal_day_is_one_day_wide(text):
    s = span(text)
    assert (s.end - s.start).days == 1


@pytest.mark.parametrize("text,y,m,d", [
    ('dvadsiateho tretieho decembra', 2017, 12, 23),
    ('tridsiateho prvého decembra', 2017, 12, 31),
])
def test_compound_day_keeps_its_tens(text, y, m, d):
    """The tens element must survive: answering the third when the speaker
    said the twenty-third is the silent-wrong this table exists to prevent."""
    assert start(text) == AstroDate(y, m, d)


@pytest.mark.parametrize("text,months", [
    ('decembra', 1),
    ('januára', 1),
])
def test_bare_month_is_still_the_whole_month(text, months):
    s = span(text)
    assert s.start.day == 1 and (s.end - s.start).days >= 28 * months


@pytest.mark.parametrize("text", [
    'tretieho',
    'dvadsiateho tretieho',
    'asdf qwerty',
    '',
])
def test_no_date_without_a_month(text):
    """An ordinal with nothing to attach to, and outright garbage, must fail
    honestly rather than inventing a day."""
    nomatch(text)


@pytest.mark.parametrize("text,y,m,d", [
    ('3. decembra', 2017, 12, 3),
    ('23. decembra', 2017, 12, 23),
])
def test_cardinal_reading_survives(text, y, m, d):
    """Adding ordinal surfaces must not disturb the cardinal ones."""
    assert start(text) == AstroDate(y, m, d)
