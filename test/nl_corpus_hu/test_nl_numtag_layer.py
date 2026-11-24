"""Hungarian numbers read through numtag.

"hét" is seven before a unit of time or a clock noun, and the week
everywhere else.  The attributive "két" ends a compound count
("tizenkét nap").  Every expected value is written by hand or computed with
``timedelta`` from the anchor.
"""
import pytest

from ._corpus import ANCHOR, ad, datetime, parse, start, timedelta


@pytest.mark.parametrize("text,days", [
    ("hét nap múlva", 7),
    ("tizenkét nap múlva", 12),
    ("huszonkét nap múlva", 22),
    ("ezer nap múlva", 1000),
    ("ezerkétszáz nappal ezelőtt", -1200),
])
def test_count(text, days):
    assert start(text) == ad(ANCHOR + timedelta(days=days))


def test_seven_o_clock():
    # the anchor is 13:04, so the next seven o'clock is 19:00 the same day
    assert start("hét órakor") == ad(datetime(2017, 6, 27, 19, 0))


def test_hét_is_the_week():
    # "két hét múlva" counts two weeks; "hét" is the unit, not seven
    assert start("két hét múlva") == ad(ANCHOR + timedelta(weeks=2))
    assert start("két héttel ezelőtt") == ad(ANCHOR - timedelta(weeks=2))


@pytest.mark.parametrize("text,hours", [
    ("két és fél óra múlva", 2.5),
    ("két és negyed óra múlva", 2.25),
    ("három és háromnegyed óra múlva", 3.75),
])
def test_a_count_with_a_fraction(text, hours):
    # the clock fraction after "és" is a part of the count of hours
    assert start(text) == ad(ANCHOR + timedelta(hours=hours))


@pytest.mark.parametrize("text", ["két és", "száz és", "egy és"])
def test_a_number_and_a_joiner_at_the_end_read_no_date(text):
    # numtag 0.15.3a1 raises on these texts; the extractor
    # reads no date and does not raise
    assert parse(text) is None
