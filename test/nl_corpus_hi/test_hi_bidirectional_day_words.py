"""कल and परसों name a day in EITHER direction, so they are refused.

Hindi has one word for yesterday and tomorrow (कल) and one for the day before
yesterday and the day after tomorrow (परसों).  Only the verb's tense separates
the two readings, and this engine parses noun phrases, not verbs, so there is
nothing in a bare कल that could pick a direction.

Two independent primary sources say so.  CLDR 47 maps locale hi's
relative-type--1 AND relative-type-1 to the same string कल, and its -2 and +2
to the same string परसों.  en.wiktionary.org lists "yesterday" and "tomorrow"
as separate senses of the one entry कल, and "day after tomorrow" and "day
before yesterday" as separate senses of परसों.

The contract is therefore refusal: guessing a direction would be wrong half
the time and silently so.  आज, which is unambiguous, resolves normally.
"""
import pytest

from ._corpus import ANCHOR, ad, nomatch, parse, span, start


def test_today_resolves():
    assert start("आज") == ad(ANCHOR.replace(hour=0, minute=0))


def test_today_is_one_day_wide():
    s = span("आज")
    assert (s.end - s.start).days == 1


@pytest.mark.parametrize("text", ["कल", "परसों"])
def test_a_bidirectional_day_word_is_refused(text):
    nomatch(text)


@pytest.mark.parametrize("text", [
    "कल सुबह", "कल शाम", "परसों दोपहर", "कल रात",
])
def test_a_bidirectional_day_word_never_anchors_a_daypart(text):
    """The daypart still resolves on the anchor day; what must not happen is
    the day word silently shifting it a day either way."""
    r = parse(text)
    assert r is not None
    assert (r[0].start.year, r[0].start.month,
            r[0].start.day) == (ANCHOR.year, ANCHOR.month, ANCHOR.day)
    assert text.split()[0] in r[1]


@pytest.mark.parametrize("text,forbidden_offset", [
    ("कल", 1), ("कल", -1), ("परसों", 2), ("परसों", -2),
])
def test_no_direction_is_ever_guessed(text, forbidden_offset):
    """Neither the future nor the past reading may be produced -- the point of
    the refusal is that BOTH are equally available and neither is chosen."""
    r = parse(text)
    assert r is None
