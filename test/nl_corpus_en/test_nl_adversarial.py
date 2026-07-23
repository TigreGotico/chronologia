"""Wave 1 -- adversarial: inputs written to break the parser.

Garbage, near-misses, lone numbers, markers without their number, empty
and whitespace, absurdly long input, and phrases that must NOT be read as
dates.  The contract: never raise, and never fabricate a date from noise.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, parse, start, nomatch


# -- must return None (no date in the noise) ------------------------------

_NOMATCH = [
    "", "   ", "\t\n", "\n\n  \t",
    "hello world", "banana", "xyzzy", "the meeting", "lorem ipsum dolor",
    "give him 5 he asked", "i owe you 5", "room 5", "chapter 12",
    "!!!", "...", "???", "@#$%^&*", "-", "--", "/",
    # lone numbers (no unit/month/era to anchor them)
    "5", "42", "1234567890", "123 456", "5 5 5", "3.14", "0",
    # markers stranded without their number/argument
    "in", "ago", "next", "last", "this", "at", "of", "of the", "from to",
    "between and", "quarter", "half", "o'clock", "pm", "am",
    # bare unit / era words with nothing to count
    "week", "day", "year", "decade", "century", "reiwa", "meiji",
    # near-misses that just miss a required slot ("in 2020" is now a real
    # bare-year reference -- see test_nl_calendar_dates.test_bare_year)
    "the 5th", "the nineteenth of",
    "five", "fifth", "twenty", "a", "an", "the",
]


@pytest.mark.parametrize("text", _NOMATCH)
def test_no_match(text):
    nomatch(text)


# -- never raises, whatever the input -------------------------------------

_FUZZ = [
    "june june june", "3pm 4pm 5pm noon", "bc ad bp",
    "quarter to to to", "the the the of of", "1 2 3 4 5 6 7 8 9",
    "31st of february of the year zero", "reiwa reiwa 99999999",
    "", "🎉📅🕐", "SELECT * FROM dates; DROP TABLE",
    "in -5 days", "in 999999999999 years", "-44 bc",
]


@pytest.mark.parametrize("text", _FUZZ)
def test_never_raises(text):
    parse(text)          # must not raise; value is irrelevant here


def test_absurdly_long_input_is_safe():
    assert parse("blah " * 20000) is None


def test_absurdly_long_with_trailing_date():
    text = ("noise " * 5000) + "tomorrow"
    r = parse(text)
    assert r is not None
    assert r[0].start == ad((ANCHOR + timedelta(days=1)).replace(
        hour=0, minute=0))


# -- ambiguity guards: an embedded real date is still found ---------------

def test_embedded_date_extracted_not_the_noise():
    # "tomorrow morning" is a date + daypart: the daypart narrows the day to
    # its morning band (CLDR 06:00-12:00), not the whole day, and both words
    # are consumed -- "the meeting" is the only noise left in the remainder.
    r = parse("the meeting tomorrow morning")
    assert r is not None
    assert r[0].start == ad((ANCHOR + timedelta(days=1)).replace(
        hour=6, minute=0))
    assert r[0].end == ad((ANCHOR + timedelta(days=1)).replace(
        hour=12, minute=0))
    assert "tomorrow" not in r[1] and "morning" not in r[1]


def test_number_in_non_date_context_ignored():
    # "give him 5 he asked" -- 5 is a quantity, not a date
    nomatch("give him 5 he asked")


def test_may_is_a_month_not_a_modal():
    # documented ambiguity: bare "may" reads as the month
    assert start("may").month == 5


def test_lone_weekday_resolves_next():
    # a bare weekday names its next strictly-future occurrence
    from datetime import timedelta
    from ._corpus import ANCHOR, span
    ahead = (0 - ANCHOR.weekday()) % 7 or 7          # 0 == Monday
    exp = (ANCHOR + timedelta(days=ahead)).date()
    s = span("monday").start
    assert (s.year, s.month, s.day) == (exp.year, exp.month, exp.day)


def test_marker_without_number_does_not_parse():
    for t in ("reiwa", "in", "ago", "quarter", "next"):
        nomatch(t)
