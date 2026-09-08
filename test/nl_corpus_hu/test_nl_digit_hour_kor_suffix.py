"""The -kor telling-time suffix also attaches to an hour written in digits.

Hungarian glues -kor onto the spelled numeral ("nyolckor") and hyphenates it
onto the digits ("reggel 9-kor"), and the hyphen is what the spelling rules
require when a suffix follows a number written in figures. The tokenizer drops
the hyphen, so the suffix arrives as its own token behind the hour and is read
exactly like the glued form.

Attested in hu.wikipedia running prose: "1972. januar 14-en reggel 9-kor" (
Montana), "delutan 2-kor van" (Barcelona), "a nap ejjel 11-kor" kezdodik (Kinai
naptar), "reggel fel 8-kor" (Elso vilaghaboru).

Hungarian counts TOWARD the hour, so a leading clock fraction keeps its own
reading: "fel 8-kor" is 07:30, an hour earlier than the bare hour would give.
Those rows are controls, unchanged by this construction.
"""
import pytest

from ._corpus import ANCHOR, nomatch, parse, start

#: hour written in digits, read at the anchor's next occurrence of it.
DIGIT_HOUR = [
    ("8-kor", "2017-06-28T08:00:00"),
    ("reggel 9-kor", "2017-06-28T09:00:00"),
    ("délután 2-kor", "2017-06-27T14:00:00"),
    ("éjjel 11-kor", "2017-06-28T23:00:00"),
]

#: count-toward-the-hour fractions, which must NOT be read as the bare hour.
FRACTION_CONTROLS = [
    ("fél 8-kor", "2017-06-28T07:30:00"),
    ("negyed 9-kor", "2017-06-28T08:15:00"),
    ("háromnegyed 8-kor", "2017-06-28T07:45:00"),
]

#: the spelled forms, which this must leave exactly as they were.
SPELLED_CONTROLS = [
    ("nyolckor", "2017-06-28T08:00:00"),
    ("8 órakor", "2017-06-28T08:00:00"),
]


@pytest.mark.parametrize("text,expected", DIGIT_HOUR)
def test_digit_hour_with_kor_reads_the_hour(text, expected):
    assert str(start(text)) == expected


@pytest.mark.parametrize("text,expected", DIGIT_HOUR)
def test_digit_hour_with_kor_consumes_the_phrase(text, expected):
    # the suffix belongs to the hour: leaving "kor" -- or the whole "11-kor"
    # behind a daypart -- in the remainder is the half-read this pins against.
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text,expected", FRACTION_CONTROLS + SPELLED_CONTROLS)
def test_the_neighbouring_readings_are_unchanged(text, expected):
    assert str(start(text)) == expected


def test_an_impossible_hour_is_still_refused():
    nomatch("25-kor")
