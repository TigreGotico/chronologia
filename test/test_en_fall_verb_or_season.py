"""English "fall" is the season only behind a licensing word, a year or alone.

"fall" is also a common verb, so "how far will the temperature fall on Friday
night" names Friday night and no season.  An article, "this", "next", "last" or
a preposition such as "in", "before" or "since" licenses the season ("in the
fall", "from spring to fall"), and so does a year, a noun or a predicate word
after it ("fall semester", "fall is my favorite season"), another season beside
it ("spring and fall") or the word on its own.  The
season is the meteorological autumn of the northern hemisphere, 1 September to
1 December.  Every date is worked out by hand from the anchor, Tuesday
2017-06-27 13:04: Friday is 2017-06-30.
"""
from datetime import date, datetime

import pytest

from chronologia import extract_timespan, extract_timespans

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


LISTED = [
    "before fall", "after fall", "around fall", "for fall", "since fall", "through fall", "till fall", "into fall",
    "toward fall", "come fall we move", "fall semester", "fall break", "fall weather", "fall colors",
    "fall festival", "fall term", "fall foliage", "fall is my favorite season", "fall starts in september",
    "spring and fall", "fall and winter", "summer or fall", "fall or winter",
]


@pytest.mark.parametrize("text", LISTED)
def test_a_licensed_fall_is_listed_as_a_mention(text):
    mentions = extract_timespans(text, "en", ANCHOR)
    assert any("fall" in m.text.lower().split() for m in mentions)


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


@pytest.mark.parametrize("text", [
    "I fall asleep at 10", "prices fall on monday", "will the leaves fall in october", "don't fall",
    "the temperature will fall tomorrow", "if you fall call me", "they fall in love every summer",
    "do not fall behind", "stocks fall again", "rain will fall during the night",
])
def test_a_verb_fall_is_no_season_mention(text):
    assert not any("fall" in m.text.lower().split() for m in extract_timespans(text, "en", ANCHOR))


def test_fall_for_a_trick_reads_no_season():
    assert extract_timespan("fall for the trick", "en", ANCHOR) is None
