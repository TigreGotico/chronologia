"""Bengali clock hours: বাজে, the colloquial ছটা and দুটো, and N-টার সময়.

Samsad Bengali-English Dictionary (DSAL):
p. 738, বাজা: "ঘড়িতে একটা বাজে the clock strikes one, it is one o'clock."
p. 374, ছ: "coll. corrup. of ছয়"; the same page has the homograph ছটা
"glow, shine, lustre ... a series", so a bare ছটা is no time.
p. 421, -টা: "sfx. used in Bengali to serve the purpose of the definite
article".
p. 985, সময়: "the time of the clock ( দুটোর সময় )".

Gold is the bn ``prefer_future`` rule on the anchor (Tuesday 2017-06-27
13:04) in plain Python, never a parser output.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, day, nomatch, parse, span, start


def next_clock(h, mi=0):
    """The first h:mi (12-hour, AM or PM) after the anchor."""
    for d in range(2):
        base = (ANCHOR + timedelta(days=d)).replace(second=0)
        for hour in (h % 12, h % 12 + 12):
            t = base.replace(hour=hour, minute=mi)
            if t > ANCHOR:
                return ad(t)


@pytest.mark.parametrize("text,h", [
    ("ঘড়িতে একটা বাজে", 1),
    ("একটা বাজে", 1),
    ("ছটা বাজে", 6),
    ("দুটো বাজে", 2),
    ("পাঁচটার সময়", 5),
    ("দুটোর সময়", 2),
    ("পাঁচটার সময় আসব", 5),
])
def test_clock_hour(text, h):
    assert start(text) == next_clock(h)


def test_gold_is_clock_arithmetic():
    assert next_clock(1) == day(1, 1)
    assert next_clock(2) == day(0, 14)
    assert next_clock(6) == day(0, 18)


@pytest.mark.parametrize("text,gold", [
    ("বিকেল ছটায়", day(0, 18)),
    ("সকাল ছটায়", day(1, 6)),
    ("আজ সন্ধ্যা সওয়া ছটায়", day(0, 18, 15)),
])
def test_six_beside_a_daypart(text, gold):
    assert start(text) == gold


@pytest.mark.parametrize("text", [
    "ছটা",
    "রোদের ছটা",
    "দুটো",
    "দুটো আপেল",
    "সন্ধ্যার সময়",
    "সারাদিন",
])
def test_no_date(text):
    nomatch(text)


def test_all_day_needs_a_day_word():
    # like en "all day", a bare সারাদিন names no day; আজ names it
    s = span("আজ সারাদিন")
    assert (s.start, s.end) == (day(0), day(1))


@pytest.mark.xfail(strict=True, reason=(
    "a bare N-টা range endpoint is no clock: the range split cuts "
    "থেকে/পর্যন্ত off the endpoint slices, and the slice N-টা alone must stay "
    "a count (ছটা is also 'glow'), so the grammar needs an endpoint-only "
    "clock order"))
def test_bare_hour_range():
    r = parse("ছটা থেকে আটটা পর্যন্ত")
    assert r is not None
    assert (r[0].start, r[0].end) == (day(0, 18), day(0, 20, 1))
