"""A bare hour before a daypart word is a clock, not the whole daypart.

The clock order required its at-marker, so an hour with no marker never bound
and the daypart alone came back: a six-hour band presented as the answer, with
the numeral left in the remainder. English ("five in the afternoon") and
Swedish ("fem på eftermiddagen") already read these, and their orders make the
marker optional.

The daypart word stays REQUIRED in the marker-less order. Without that a bare
numeral would become a clock, which is the invented reading the legacy
extractor produced and that this corpus pins as a refusal.
"""
import pytest

from ._corpus import nomatch, start


#: hour + daypart, read as a clock on the 12-hour reckoning.
DAYPART_HOUR = [
    ("fem om eftermiddagen", "2017-06-27T17:00:00"),
    ("tre om eftermiddagen", "2017-06-27T15:00:00"),
    ("fem om aftenen", "2017-06-27T17:00:00"),
    ("fem om morgenen", "2017-06-28T05:00:00"),
]

#: the marked form, which already worked and must not move.
MARKED = [("klokken fem om eftermiddagen", "2017-06-27T17:00:00")]

#: a bare numeral names no time at all; the legacy extractor invented one.
BARE = ["fem", "20"]


@pytest.mark.parametrize("text,expected", DAYPART_HOUR)
def test_the_daypart_binds_the_bare_hour(text, expected):
    assert str(start(text)) == expected


@pytest.mark.parametrize("text,expected", MARKED)
def test_the_marked_form_is_unchanged(text, expected):
    assert str(start(text)) == expected


@pytest.mark.parametrize("text", BARE)
def test_a_bare_numeral_is_not_a_clock(text):
    nomatch(text)
