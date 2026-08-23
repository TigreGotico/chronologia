"""Adversarial Welsh cases plus the shared English semantic-parity block."""
import pytest

from ._corpus import ANCHOR, nomatch, parse

#: (Welsh, English) phrases that mean the same thing and must resolve to the
#: same span.  Read as a literal by ``parity.py`` and by
#: ``test_language_parity``.
PAIRS = [
    ("heddiw", "today"),
    ("yfory", "tomorrow"),
    ("ddoe", "yesterday"),
    ("echdoe", "the day before yesterday"),
    ("ymhen tair blynedd", "in three years"),
    ("tri diwrnod yn ôl", "three days ago"),
    ("dwy flynedd yn ôl", "two years ago"),
    ("pum mlynedd yn ôl", "five years ago"),
    ("ymhen dau fis", "in two months"),
    ("ymhen pum munud", "in five minutes"),
    ("ymhen dwy awr", "in two hours"),
    ("ymhen deg diwrnod", "in ten days"),
    ("ymhen tair wythnos", "in three weeks"),
    ("yr wythnos nesaf", "next week"),
    ("yr wythnos diwethaf", "last week"),
    ("yr wythnos hon", "this week"),
    ("y mis nesaf", "next month"),
    ("y mis diwethaf", "last month"),
    ("y mis hwn", "this month"),
    ("y flwyddyn nesaf", "next year"),
    ("y flwyddyn diwethaf", "last year"),
    ("dydd Llun", "monday"),
    ("dydd Gwener", "friday"),
    ("dydd Sadwrn", "saturday"),
    ("5 Mehefin 2027", "june 5th 2027"),
    ("y 3ydd o Orffennaf 1969", "3 july 1969"),
    ("25 Rhagfyr 2020", "25 december 2020"),
    ("Ionawr 2030", "january 2030"),
    ("Mehefin", "june"),
    ("1990", "1990"),
    ("hanner awr wedi naw", "half past nine"),
    ("chwarter wedi naw", "quarter past nine"),
    ("chwarter i ddeg", "quarter to ten"),
    ("pum munud wedi dau", "five past two"),
    ("deg munud i dri", "ten to three"),
    ("am dri o'r gloch", "at three o'clock"),
    ("canol nos", "midnight"),
    ("canol dydd", "noon"),
    ("15:30", "15:30"),
]


@pytest.mark.parametrize("text", [
    "", "   ", "sut mae heddwch", "qwerty zxcvb", "does dim dyddiad yma",
])
def test_junk_is_none(text):
    nomatch(text)


@pytest.mark.parametrize("text", [
    "tri diwrnod", "dwy flynedd", "pum mlynedd", "tair wythnos", "3 diwrnod",
])
def test_offset_without_marker(text):
    """A bare count of units is a quantity, not a point in time."""
    nomatch(text)


@pytest.mark.parametrize("text", ["ymhen", "yn ôl", "diwrnod", "ymhen ymhen"])
def test_incomplete_offset(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


@pytest.mark.parametrize("text", ["25:00", "15:99", "99:99"])
def test_impossible_clock(text):
    r = parse(text)
    if r is not None:
        assert 0 <= r[0].start.hour <= 23


@pytest.mark.parametrize("text", [
    "hace tres días", "in drei Tagen", "il y a trois jours", "tri dagar",
])
def test_other_languages_are_not_welsh(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


def test_bare_numeral_is_not_a_year():
    """A spelled numeral folds to a digit, but a small digit is not a year."""
    nomatch("dau ar hugain")


def test_english_month_is_not_welsh():
    """"june" is not a Welsh month name and must not read as Mehefin."""
    nomatch("june")
