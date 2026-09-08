"""A bare hour before a daypart word is a clock, not the whole daypart.

The clock order required its at-marker, so an hour with no marker never bound
and the daypart alone came back: a six-hour band presented as the answer, with
the numeral left in the remainder. English ("five in the afternoon") and
Swedish ("fem på eftermiddagen") already read these, and their orders make the
marker optional.

"nachts" reads as the am half of the 12-hour clock, so "drei nachts" is 03:00.
It is the one night word among these adverbs, and it also names a daypart band,
so the band cases below pin that the clock reading does not swallow it.

The daypart word stays REQUIRED in the marker-less order. Without that a bare
numeral would become a clock, which is the invented reading the legacy
extractor produced and that this corpus pins as a refusal.
"""
import pytest

from ._corpus import nomatch, start


#: hour + daypart adverb, read as a clock on the 12-hour reckoning.
DAYPART_HOUR = [
    ("fünf nachmittags", "2017-06-27T17:00:00"),
    ("drei nachmittags", "2017-06-27T15:00:00"),
    ("fünf abends", "2017-06-27T17:00:00"),
    ("sieben morgens", "2017-06-28T07:00:00"),
    ("drei nachts", "2017-06-28T03:00:00"),
]

#: the marked form, which already worked and must not move.
MARKED = [("um fünf nachmittags", "2017-06-27T17:00:00")]

#: a bare numeral names no time at all.
BARE = ["fünf"]

#: the daypart band itself, which the clock reading must not swallow.
BANDS = [
    ("nachts", "2017-06-27T00:00:00"),
    ("heute nacht", "2017-06-27T00:00:00"),
]


@pytest.mark.parametrize("text,expected", DAYPART_HOUR)
def test_the_daypart_binds_the_bare_hour(text, expected):
    assert str(start(text)) == expected


@pytest.mark.parametrize("text,expected", MARKED)
def test_the_marked_form_is_unchanged(text, expected):
    assert str(start(text)) == expected


@pytest.mark.parametrize("text", BARE)
def test_a_bare_numeral_is_not_a_clock(text):
    nomatch(text)


@pytest.mark.parametrize("text,expected", BANDS)
def test_the_daypart_alone_is_still_a_band(text, expected):
    assert str(start(text)) == expected
