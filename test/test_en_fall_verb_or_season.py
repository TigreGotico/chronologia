"""English "fall" is the season only behind a licensing word, a year or alone.

"fall" is also a common verb, so "how far will the temperature fall on Friday
night" names Friday night and no season.  An article, "this", "next", "last" or
a preposition such as "in" or "to" licenses the season ("in the fall", "from
spring to fall"), and so does a year after it or the word on its own.  The
season is the meteorological autumn of the northern hemisphere, 1 September to
1 December.  Every date is worked out by hand from the anchor, Tuesday
2017-06-27 13:04: Friday is 2017-06-30.
"""
from datetime import date, datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)

SEASON = [
    "this fall", "next fall", "in the fall", "fall 2017",
    "from spring to fall", "weather fall 2017", "rain in fall", "heat during fall", "fall", "the fall of 2018",
]

VERB = [
    ("how far will the temperature fall on Friday night", date(2017, 6, 30)),
    ("how much will it fall tomorrow", date(2017, 6, 28)),
]


@pytest.mark.parametrize("text", SEASON)
def test_fall_is_the_season_when_licensed(text):
    found = extract_timespan(text, "en", ANCHOR)
    assert found is not None and found.span.start.datetime().month in (3, 9)
    assert found.span.end.datetime().month == 12


@pytest.mark.parametrize("text,day", VERB)
def test_fall_as_a_verb_names_no_season(text, day):
    found = extract_timespan(text, "en", ANCHOR)
    assert found.span.start.datetime().date() == day
    assert "fall" in found.remainder.split()


def test_autumn_is_the_season_whatever_stands_before_it():
    found = extract_timespan("the leaves go yellow in autumn", "en", ANCHOR)
    assert found.span.start.datetime() == datetime(2017, 9, 1)


def test_a_modal_before_fall_alone_reads_no_date():
    assert extract_timespan("will fall", "en", ANCHOR) is None


def test_fall_for_a_trick_reads_no_season():
    assert extract_timespan("fall for the trick", "en", ANCHOR) is None
