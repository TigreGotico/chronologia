"""The clock.  Hausa reads the Western hour, and *ƙarfe* leads its number.

Every expected value below is the hour written in the source that attests the
phrasing, not a reading taken back off the parser.  The band words are fixed
by worked examples on ha.wikipedia.org: "ƙarfe 1:00 na rana (12:00 GMT)" is
13:00 because Nigeria runs an hour ahead of GMT; a school day of "ƙarfe 7:30
zuwa 11:30 na safe, sai kuma 2:30 zuwa 6:00 na yamma" runs 07:30-11:30 and
again 14:30-18:00.
"""
import pytest

from ._corpus import minute_at, nomatch, parse, remainder, start_end


@pytest.mark.parametrize("text,expected", [
    ("ƙarfe 7:59 na safe", (2027, 5, 13, 7, 59)),
    ("ƙarfe 7:59 na safiya", (2027, 5, 13, 7, 59)),
    ("ƙarfe 09:00 na safe", (2027, 5, 13, 9, 0)),
    ("ƙarfe 1:45 na safiya", (2027, 5, 13, 1, 45)),
])
def test_na_safe_is_the_morning(text, expected):
    assert start_end(text) == minute_at(*expected)
    assert remainder(text) == ""


@pytest.mark.parametrize("text,expected", [
    ("ƙarfe 1:00 na rana", (2027, 5, 13, 13, 0)),
    ("ƙarfe 1:30 na rana", (2027, 5, 12, 13, 30)),
    ("ƙarfe 2 na rana", (2027, 5, 12, 14, 0)),
    ("ƙarfe 2:30 na rana", (2027, 5, 12, 14, 30)),
    ("ƙarfe 3:00 na yamma", (2027, 5, 12, 15, 0)),
    ("ƙarfe 6:00 na yamma", (2027, 5, 12, 18, 0)),
])
def test_na_rana_and_na_yamma_are_the_afternoon(text, expected):
    assert start_end(text) == minute_at(*expected)
    assert remainder(text) == ""


def test_twelve_na_rana_is_noon():
    assert start_end("ƙarfe 12 na rana") == minute_at(2027, 5, 13, 12, 0)


@pytest.mark.parametrize("text,expected", [
    ("ƙarfe 1:00 na dare", (2027, 5, 13, 1, 0)),
    ("ƙarfe 2 na dare", (2027, 5, 13, 2, 0)),
    ("ƙarfe 9:05 na dare", (2027, 5, 12, 21, 5)),
    ("ƙarfe 9:50 na dare", (2027, 5, 12, 21, 50)),
    ("ƙarfe 7:45 na dare", (2027, 5, 12, 19, 45)),
    ("ƙarfe 11:30 na dare", (2027, 5, 12, 23, 30)),
])
def test_na_dare_crosses_midnight(text, expected):
    """The small hours stay morning and the late evening becomes afternoon.

    ha.wikipedia.org writes "ƙarfe 2 na dare" for a death in the small hours
    and "ƙarfe 11:30 na dare" for the fall of the Berlin Wall at 23:30, so
    the word is a band, not a uniform twelve-hour shift.
    """
    assert start_end(text) == minute_at(*expected)


@pytest.mark.parametrize("text,expected", [
    ("ƙarfe 13:00 na rana", (2027, 5, 13, 13, 0)),
    ("ƙarfe 22:00", (2027, 5, 12, 22, 0)),
    ("ƙarfe 03:00", (2027, 5, 13, 3, 0)),
    ("15:30", (2027, 5, 12, 15, 30)),
    ("07:59", (2027, 5, 13, 7, 59)),
])
def test_the_twenty_four_hour_literal(text, expected):
    assert start_end(text) == minute_at(*expected)
    assert remainder(text) == ""


def test_the_hooked_k_may_be_written_plain():
    assert start_end("karfe 8 na safe") == start_end("ƙarfe 8 na safe")


@pytest.mark.parametrize("text,expected", [
    ("ƙarfe biyu na rana", (2027, 5, 12, 14, 0)),
    ("ƙarfe goma na safe", (2027, 5, 13, 10, 0)),
    ("ƙarfe goma sha biyu na rana", (2027, 5, 13, 12, 0)),
])
def test_a_spelled_hour(text, expected):
    assert start_end(text) == minute_at(*expected)


def test_a_bare_hour_word_needs_the_clock_noun():
    """"biyu na rana" is two of something in the afternoon, not two o'clock."""
    nomatch("biyu na rana")


def test_a_lone_clock_noun_is_not_a_time():
    nomatch("ƙarfe")


@pytest.mark.parametrize("text", ["saa tatu", "saa sita"])
def test_the_swahili_spoken_hour_is_not_hausa(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["25:00", "15:99", "99:99"])
def test_an_impossible_clock_never_yields_an_impossible_hour(text):
    r = parse(text)
    if r is not None:
        assert 0 <= r[0].start.hour <= 23


@pytest.mark.parametrize("text,expected", [
    ("ƙarfe 2 na rana da rabi", (2027, 5, 12, 14, 0)),
    ("ƙarfe 8 na safe da rabi", (2027, 5, 13, 8, 0)),
])
def test_the_half_hour_is_refused_and_left_visible(text, expected):
    """No source consulted reads *da rabi* on a clock, so it is not read.

    *da rabi* is well attested on a DURATION ("awa daya da rabi" is an hour
    and a half), but nothing attests it on a time of day, and a fraction read
    in the wrong direction is wrong by half an hour in every reading while
    looking entirely normal.  The hour therefore stands unchanged and the
    fraction stays in the remainder, where a caller can see it was not
    consumed.
    """
    assert start_end(text) == minute_at(*expected)
    assert "rabi" in remainder(text)
