"""Spelled ordinal day of the month -- the ordinary spoken date.

Ukrainian puts the day in the genitive of the ordinal beside a genitive month
name (Ukrainskyi pravopys, 2019), and inflects only the last element of a
compound day -- the tens stays a bare cardinal.

Expected values are plain calendar facts about the corpus anchor, never the
parser's own output.
"""
import pytest

from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, nomatch, span, start


@pytest.mark.parametrize("text,y,m,d", [
    ('третього грудня', 2017, 12, 3),
    ('першого травня', 2018, 5, 1),
    ('десятого листопада', 2017, 11, 10),
    ('двадцятого грудня', 2017, 12, 20),
])
def test_spelled_ordinal_day(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


@pytest.mark.parametrize("text", [
    'третього грудня',
    'першого травня',
])
def test_spelled_ordinal_day_is_one_day_wide(text):
    s = span(text)
    assert (s.end - s.start).days == 1


@pytest.mark.parametrize("text,y,m,d", [
    ('двадцять третього грудня', 2017, 12, 23),
    ('тридцять першого грудня', 2017, 12, 31),
])
def test_compound_day_keeps_its_tens(text, y, m, d):
    """The tens element must survive: answering the third when the speaker
    said the twenty-third is the silent-wrong this table exists to prevent."""
    assert start(text) == AstroDate(y, m, d)


@pytest.mark.parametrize("text,months", [
    ('грудня', 1),
    ('травня', 1),
])
def test_bare_month_is_still_the_whole_month(text, months):
    s = span(text)
    assert s.start.day == 1 and (s.end - s.start).days >= 28 * months


@pytest.mark.parametrize("text", [
    'третього',
    'двадцять третього',
    'asdf qwerty',
    '',
])
def test_no_date_without_a_month(text):
    """An ordinal with nothing to attach to, and outright garbage, must fail
    honestly rather than inventing a day."""
    nomatch(text)


@pytest.mark.parametrize("text,y,m,d", [
    ('3 грудня', 2017, 12, 3),
    ('23 грудня', 2017, 12, 23),
])
def test_cardinal_reading_survives(text, y, m, d):
    """Adding ordinal surfaces must not disturb the cardinal ones."""
    assert start(text) == AstroDate(y, m, d)
