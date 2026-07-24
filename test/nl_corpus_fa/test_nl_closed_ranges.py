# -*- coding: utf-8 -*-
"""Closed ranges written with «تا» (fa).

«از ... تا ...» is the ordinary Persian bounded interval, and «تا» is the same
word Persian uses for the open "until" reading (Dehkhoda and Sokhan, s.v. «تا»
-- حرف اضافه, حد و پایان زمان).  It was declared only as the open marker, so a
closed range said with it silently degraded into the open one: «از ۵ ژوئن» to
the anchor instant, a strictly wider span than was uttered, with «تا ۱۲ ژوئن»
left in the remainder.  A language's "until" word is its closed-range
terminator too, exactly as English "until" is.

Anchor 2017-06-27 13:04; every edge hand-derived."""
import pytest

from ._corpus import AstroDate, ANCHOR, ad, parse, start_end


@pytest.mark.parametrize("text", [
    "از 5 ژوئن تا 12 ژوئن",
    "از 5 تا 12 ژوئن",
])
def test_ta_range_ends_after_the_named_day(text):
    ss, ee = start_end(text)
    assert ss == AstroDate(2018, 6, 5)
    assert ee == AstroDate(2018, 6, 13)


def test_ta_range_crosses_the_month():
    ss, ee = start_end("از 28 ژوئن تا 3 ژوئیه")
    assert ss == AstroDate(2017, 6, 28) and ee == AstroDate(2017, 7, 4)


def test_ta_range_consumes_its_framing_words():
    assert parse("از 5 ژوئن تا 12 ژوئن").remainder == ""


# -- adversarial: the OPEN reading must survive intact.  A leading «تا» has no
# left endpoint to split on, so it is still read as "until <date>", starting at
# the anchor instant; «از <year>» is still the open-ended "since".
def test_leading_ta_is_still_the_open_until():
    s, e = start_end("تا 12 ژوئن")
    assert s == ad(ANCHOR) and e == AstroDate(2018, 6, 13)


def test_az_year_is_still_the_open_since():
    s, e = start_end("از 2019")
    assert s == AstroDate(2017, 1, 1) and e == ad(ANCHOR)


@pytest.mark.parametrize("text", ["تا", "از تا", "از 5 تا"])
def test_ta_garbage_never_raises(text):
    parse(text)
