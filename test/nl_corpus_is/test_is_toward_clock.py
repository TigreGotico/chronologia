"""The Icelandic spoken clock, which counts toward the COMING hour.

"hálf tvö" is half of the second hour -- 01:30, an hour earlier than the
English-shaped reading a reader might expect.  "kortér yfir tvö" counts up
from two (02:15) and "kortér í þrjú" counts down to three (02:45), and a
minute count reads the same way with the unit noun spoken between the count
and the direction ("fimmtán mínútur yfir eitt").  Every direction is pinned
adversarially: the wrong reading is asserted absent, not merely the right
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
    ("hálf tvö", 1, 30),
    ("hálf þrjú", 2, 30),
    ("hálf fjögur", 3, 30),
    ("hálf fimm", 4, 30),
    ("hálf sjö", 6, 30),
    ("hálf átta", 7, 30),
    ("hálf níu", 8, 30),
    ("hálf tíu", 9, 30),
    ("hálf ellefu", 10, 30),
    ("hálf tólf", 11, 30),
    ("hálf eitt", 12, 30),
])
def test_half_names_the_coming_hour(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,wrong_hour", [
    ("hálf tvö", 2), ("hálf þrjú", 3), ("hálf átta", 8), ("hálf tólf", 12),
])
def test_half_is_not_the_stated_hour(text, wrong_hour):
    """The additive reading ("half past three" = 03:30) must never occur."""
    assert start(text).hour != wrong_hour


def test_half_toward_one_reads_as_twelve():
    """Rolling back from one o'clock surfaces as twelve, not zero."""
    assert start("hálf eitt").hour == 12


@pytest.mark.parametrize("text,h,mi", [
    ("kortér yfir tvö", 2, 15),
    ("korter yfir tvö", 2, 15),
    ("kortér yfir eitt", 1, 15),
    ("kortér yfir sjö", 7, 15),
])
def test_quarter_past_counts_up(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,h,mi", [
    ("kortér í þrjú", 2, 45),
    ("kortér í sjö", 6, 45),
    ("kortér í tólf", 11, 45),
])
def test_quarter_to_counts_down(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("past,to", [
    ("kortér yfir tvö", "kortér í tvö"),
    ("kortér yfir sjö", "kortér í sjö"),
])
def test_past_and_to_are_not_the_same_time(past, to):
    """"yfir" and "í" are the two halves of one opposition; reading either as
    the other moves the answer half an hour and an hour."""
    assert start(past) != start(to)


@pytest.mark.parametrize("text,h,mi", [
    ("fimmtán mínútur yfir eitt", 1, 15),
    ("fimm mínútur yfir tvö", 2, 5),
    ("tíu mínútur yfir þrjú", 3, 10),
    ("tuttugu mínútur yfir fjögur", 4, 20),
    ("fimm mínútur í tvö", 1, 55),
    ("tíu mínútur í þrjú", 2, 50),
    ("fimmtán mínútur í tvö", 1, 45),
])
def test_minutes_past_and_to(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,wrong_hour", [
    ("fimm mínútur í tvö", 2), ("tíu mínútur í þrjú", 3),
])
def test_minutes_to_rolls_the_hour_back(text, wrong_hour):
    assert start(text).hour != wrong_hour


@pytest.mark.parametrize("text,h", [
    ("klukkan eitt", 1), ("klukkan tvö", 2), ("klukkan þrjú", 3),
    ("klukkan fjögur", 4), ("klukkan fimm", 5), ("klukkan ellefu", 11),
])
def test_klukkan_names_a_bare_hour(text, h):
    """The hour after "klukkan" is the NEUTER numeral -- eitt, tvö, þrjú,
    fjögur -- not the masculine citation form."""
    assert start(text).hour == h


@pytest.mark.parametrize("text,h,mi", [
    ("15:30", 15, 30), ("09:05", 9, 5), ("00:00", 0, 0), ("23:59", 23, 59),
])
def test_digit_clock(text, h, mi):
    s = start(text)
    assert (s.hour, s.minute) == (h, mi)


@pytest.mark.parametrize("text,h", [("miðnætti", 0), ("hádegi", 12)])
def test_clock_landmarks(text, h):
    assert start(text).hour == h


@pytest.mark.parametrize("text", [
    "hálf",              # a bare half with no hour
    "yfir",              # a bare direction with nothing to count from
    "kortér",            # a quarter with no direction and no hour
    "kortér yfir",       # a direction with no hour named
])
def test_incomplete_clock_is_not_a_time(text):
    nomatch(text)
