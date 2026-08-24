"""The Georgian spoken clock, which names the hour it is APPROACHING.

"ორის ნახევარი" is the half toward two -- 01:30, an hour earlier than the
English-shaped reading a reader might expect; Wiktionary glosses that exact
phrase "half past one".  The hour stands in the GENITIVE and nothing else in
the phrase says "past" or "to", so the case marking is the whole signal: a
nominative before ნახევარი names no time at all.  Every direction is pinned
adversarially -- the wrong reading is asserted absent, not merely the right
one asserted present.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, nomatch, start


def _next_time(h, mi):
    cand = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    return ad(cand)


@pytest.mark.parametrize("text,h,mi", [
    ("ორის ნახევარი", 1, 30),
    ("სამის ნახევარი", 2, 30),
    ("ოთხის ნახევარი", 3, 30),
    ("ხუთის ნახევარი", 4, 30),
    ("ექვსის ნახევარი", 5, 30),
    ("შვიდის ნახევარი", 6, 30),
    ("ათის ნახევარი", 9, 30),
    ("თერთმეტის ნახევარი", 10, 30),
    ("თორმეტის ნახევარი", 11, 30),
])
def test_half_names_the_coming_hour(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,wrong_hour", [
    ("ორის ნახევარი", 2),
    ("სამის ნახევარი", 3),
    ("ოთხის ნახევარი", 4),
    ("ათის ნახევარი", 10),
    ("თორმეტის ნახევარი", 12),
])
def test_half_is_not_the_stated_hour(text, wrong_hour):
    """The additive reading ("half past three" == 03:30) must never occur."""
    assert start(text).hour != wrong_hour


@pytest.mark.parametrize("text,other", [
    ("ორის ნახევარი", "სამის ნახევარი"),
    ("სამის ნახევარი", "ოთხის ნახევარი"),
])
def test_neighbouring_hours_are_an_hour_apart(text, other):
    assert start(other) - start(text) == timedelta(hours=1)


@pytest.mark.parametrize("text", [
    "ორი ნახევარი", "სამი ნახევარი", "ათი ნახევარი", "თორმეტი ნახევარი",
])
def test_a_nominative_hour_is_not_a_time(text):
    """The genitive is the only thing that makes the phrase a clock reading,
    so the nominative must not be read as one -- least of all as the same
    time its genitive would name."""
    nomatch(text)


@pytest.mark.parametrize("text", [
    "ერთის ნახევარი", "პირველის ნახევარი", "რვის ნახევარი", "ცხრის ნახევარი",
])
def test_unattested_genitive_hours_refuse(text):
    """One o'clock is named by the ordinal პირველი rather than by ერთი, and
    no source consulted spells the genitive of either that ordinal or the
    vowel-final რვა (8) and ცხრა (9), so those three hours are absent rather
    than composed."""
    nomatch(text)


@pytest.mark.parametrize("text,h,mi", [
    ("15:30", 15, 30), ("09:05", 9, 5), ("00:00", 0, 0), ("23:59", 23, 59),
])
def test_digit_clock(text, h, mi):
    s = start(text)
    assert (s.hour, s.minute) == (h, mi)


@pytest.mark.parametrize("text,h", [
    ("შუაღამე", 0), ("შუაღამეს", 0), ("შუადღე", 12), ("შუადღეს", 12),
])
def test_clock_landmarks(text, h):
    assert start(text).hour == h


@pytest.mark.parametrize("text", ["ნახევარი", "ორის", "სამის"])
def test_incomplete_clock_is_not_a_time(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["25:00", "15:99", "99:99"])
def test_impossible_clock(text):
    from ._corpus import parse
    r = parse(text)
    if r is not None:
        assert 0 <= r[0].start.hour <= 23
