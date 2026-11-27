"""Bengali সওয়া / সোয়া "a quarter past" before a clock hour.

Samsad Bengali-English Dictionary (DSAL), p. 963, সওয়া2: "সওয়া তিনটে বাজে
it is a quarter past three o'clock."  সোয়া is the spoken spelling.

bn clocks have ``prefer_future``: a 12-hour reading is the next H:MM after the
anchor (Tuesday 2017-06-27 13:04).  Gold is that rule on the anchor in plain
Python, never a parser output.
"""
from datetime import timedelta

import pytest

from chronologia import extract_duration

from ._corpus import ANCHOR, ad, start


def next_clock(h, mi):
    """The first h:mi (12-hour, AM or PM) after the anchor."""
    for day in range(2):
        base = (ANCHOR + timedelta(days=day)).replace(second=0)
        for hour in (h % 12, h % 12 + 12):
            t = base.replace(hour=hour, minute=mi)
            if t > ANCHOR:
                return ad(t)


@pytest.mark.parametrize("text,h", [
    ("সওয়া তিনটে বাজে", 3),
    ("সোয়া তিনটে বাজে", 3),
    ("সোয়া পাঁচটায়", 5),
    ("সওয়া পাঁচটায়", 5),
    ("সোয়া তিনটায় দেখা হবে", 3),
    ("সওয়া তিনটায় দেখা হবে", 3),
    ("সওয়া একটায় বাস ছাড়বে।", 1),
    ("সওয়া বারোটায় ট্রেন আসবে।", 12),
])
def test_quarter_past(text, h):
    assert start(text) == next_clock(h, 15)


@pytest.mark.parametrize("text,h", [
    ("তিনটে বাজে", 3),
    ("তিনটা বাজে", 3),
    ("চারটে বাজে", 4),
])
def test_hour_classifier_strikes(text, h):
    # numtag reads "তিনটে" as one number; the classifier must stay a word
    assert start(text) == next_clock(h, 0)


def test_quarter_past_gold_is_clock_arithmetic():
    assert next_clock(5, 15) == ad(ANCHOR.replace(hour=17, minute=15))
    assert next_clock(1, 15) == ad(ANCHOR.replace(hour=13, minute=15))
    assert next_clock(12, 15) == ad((ANCHOR + timedelta(days=1)).replace(
        hour=0, minute=15))


@pytest.mark.xfail(strict=True, reason=(
    "extract_duration has no additive pre-count fraction: সওয়া N ঘণ্টা is "
    "N + 1/4 hours, and the engine reads only proper fractions and a "
    "trailing 'and a half'; ঘন্টা (Samsad spelling) is also not a unit word"))
@pytest.mark.parametrize("text,minutes", [
    ("সওয়া ঘন্টা", 75),
    ("সোয়া দুই ঘণ্টা", 135),
])
def test_quarter_past_duration(text, minutes):
    r = extract_duration(text, "bn")
    assert r is not None and r.duration == timedelta(minutes=minutes)
