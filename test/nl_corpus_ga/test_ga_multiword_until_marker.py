"""The two-word Irish until-marker ``go dtí``.

``go dtí`` is both the until/to connector and the language's spoken-clock
"to" direction, so the token stream carries it as a single glued token.
Every frame that reads it -- the open "until <point>" span, the closed
year range, and the clock -- keeps its reading.

Gold is independent arithmetic against the Tuesday 2017-06-27 anchor.
"""
from datetime import datetime

from ._corpus import ANCHOR, ad, parse


def _span_rem(text):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    return (r[0].start, r[0].end), r[1]


def test_until_year_runs_from_the_anchor():
    (start, end), rem = _span_rem("go dtí 2020")
    assert (start, end) == (ad(ANCHOR), ad(datetime(2021, 1, 1)))
    assert rem == ""


def test_until_next_weekday():
    # the Monday after the Tuesday anchor is 2017-07-03; "until" reaches the
    # end of that day
    (start, end), rem = _span_rem("go dtí Dé Luain")
    assert (start, end) == (ad(ANCHOR), ad(datetime(2017, 7, 4)))
    assert rem == ""


def test_until_month():
    (start, end), rem = _span_rem("go dtí Iúil")
    assert (start, end) == (ad(ANCHOR), ad(datetime(2017, 8, 1)))
    assert rem == ""


def test_spoken_clock_to_the_hour():
    # "a quarter to three": the clock runs toward the coming hour
    (start, _), rem = _span_rem("ceathrú go dtí a trí")
    assert (start.hour, start.minute) == (2, 45)
    assert rem == ""
