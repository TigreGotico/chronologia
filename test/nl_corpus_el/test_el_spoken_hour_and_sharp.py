"""The everyday spellings of seven, eight and nine on the clock ("στις οχτώ"
= at eight) and "ακριβώς" (sharp) closing the hour.

Wiktionary: εφτά and οχτώ, "alternative spelling of" επτά / οκτώ, with the
clock example "Η ώρα είναι οχτώ το βράδυ"; εννιά "nine"; ακριβώς, "Το
λεωφορείο φεύγει στις 9 π.μ. ακριβώς" (the bus leaves at 9 am sharp).

Anchor: Tuesday 2017-06-27 13:04; a clock names its next occurrence.
"""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

from ._corpus import ANCHOR, ad, nomatch, parse


def _next(h):
    cand = ANCHOR.replace(hour=h, minute=0, second=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    return ad(cand)


@pytest.mark.parametrize("text,h,rem", [
    ("στις οχτώ", 8, ""),
    ("στις οκτώ", 8, ""),
    ("στις εφτά", 7, ""),
    ("στις επτά", 7, ""),
    ("στις εννιά", 9, ""),
    ("στις οχτώ ακριβώς", 8, ""),
    ("στις 9 ακριβώς", 9, ""),
    ("βάλε ξυπνητήρι στις οχτώ ακριβώς", 8, "βάλε ξυπνητήρι"),
])
def test_spoken_hour(text, h, rem):
    res = parse(text)
    assert res is not None, f"{text!r} did not parse"
    assert res.remainder == rem
    assert res[0].start == _next(h)
    assert res[0].end == _next(h) + timedelta(minutes=1)


def test_spoken_eight_in_the_morning_is_eight_not_the_band():
    res = parse("στις οχτώ το πρωί")
    assert res is not None and res.remainder == ""
    assert res[0].start == _next(8)


def test_a_timer_length_is_not_an_instant():
    """"βάλε χρονόμετρο για 5 λεπτά" (set a timer for 5 minutes) names a length."""
    nomatch("για 5 λεπτά")
    got = extract_duration("βάλε χρονόμετρο για 5 λεπτά", "el")
    assert got is not None and got.duration == timedelta(minutes=5)
