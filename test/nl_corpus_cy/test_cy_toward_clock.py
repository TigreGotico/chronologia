"""The Welsh spoken clock, which counts from the hour just NAMED.

"hanner awr wedi tri" is half an hour past three -- 03:30, the English
direction and the opposite of the Icelandic "half of the third hour".  "wedi"
counts up from the named hour and "i" counts down to it, so "chwarter wedi
naw" is 09:15 while "chwarter i ddeg" is 09:45; "i" also soft-mutates the hour
it governs, which is why the four reads "bedwar" and the three "dri".  Every
direction is pinned adversarially: the wrong reading is asserted absent, not
merely the right one asserted present.

The five-minute table below is the one a Welsh course teaches, transcribed
whole (en.wikibooks.org, "Welsh/Mynediad/Lesson 8"): past up to the half hour,
to after it.
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
    ("pum munud wedi dau", 2, 5),
    ("deg munud wedi dau", 2, 10),
    ("chwarter wedi dau", 2, 15),
    ("ugain munud wedi dau", 2, 20),
    ("pum munud ar hugain wedi dau", 2, 25),
    ("hanner awr wedi dau", 2, 30),
    ("pum munud ar hugain i dri", 2, 35),
    ("ugain munud i dri", 2, 40),
    ("chwarter i dri", 2, 45),
    ("deg munud i dri", 2, 50),
    ("pum munud i dri", 2, 55),
])
def test_the_taught_five_minute_table(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,h", [
    ("hanner awr wedi un", 1), ("hanner awr wedi tri", 3),
    ("hanner awr wedi pedwar", 4), ("hanner awr wedi saith", 7),
    ("hanner awr wedi naw", 9), ("hanner awr wedi deg", 10),
    ("hanner awr wedi deuddeg", 12),
])
def test_half_past_names_the_hour_just_gone(text, h):
    s = start(text)
    assert (s.hour, s.minute) == (h, 30)


@pytest.mark.parametrize("text,wrong_hour", [
    ("hanner awr wedi tri", 2), ("hanner awr wedi naw", 8),
    ("hanner awr wedi deuddeg", 11), ("hanner awr wedi un", 12),
])
def test_half_past_is_never_the_coming_hour(text, wrong_hour):
    """The Icelandic reading -- half OF the next hour, an hour earlier -- must
    never occur here."""
    assert start(text).hour != wrong_hour


def test_bare_hanner_is_the_same_idiom():
    """The lesson gives the half hour with and without the noun."""
    assert start("hanner awr wedi tri") == _next_time(3, 30)
    assert start("hanner wedi tri") == start("hanner awr wedi tri")


@pytest.mark.parametrize("text,h", [
    ("chwarter wedi naw", 9), ("chwarter wedi un", 1),
    ("chwarter wedi saith", 7), ("chwarter wedi deuddeg", 12),
])
def test_quarter_past_counts_up(text, h):
    s = start(text)
    assert (s.hour, s.minute) == (h, 15)


@pytest.mark.parametrize("text,h,mi", [
    ("chwarter i dri", 2, 45),
    ("chwarter i bedwar", 3, 45),
    ("chwarter i chwech", 5, 45),
    ("chwarter i saith", 6, 45),
    ("chwarter i ddeg", 9, 45),
    ("chwarter i ddeuddeg", 11, 45),
])
def test_quarter_to_counts_down_across_the_mutated_hour(text, h, mi):
    """"i" soft-mutates the hour it governs: tri -> dri, pedwar -> bedwar,
    deg -> ddeg, while chwech and saith cannot mutate at all."""
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("past,to", [
    ("chwarter wedi tri", "chwarter i dri"),
    ("chwarter wedi saith", "chwarter i saith"),
])
def test_past_and_to_are_not_the_same_time(past, to):
    assert start(past) != start(to)


@pytest.mark.parametrize("text,wrong_hour", [
    ("chwarter i dri", 3), ("chwarter i bedwar", 4), ("chwarter i ddeg", 10),
])
def test_quarter_to_rolls_the_hour_back(text, wrong_hour):
    assert start(text).hour != wrong_hour


@pytest.mark.parametrize("text,h", [
    ("am un o'r gloch", 1), ("am ddau o'r gloch", 2), ("am dri o'r gloch", 3),
    ("am bedwar o'r gloch", 4), ("am bump o'r gloch", 5),
    ("am chwech o'r gloch", 6), ("am naw o'r gloch", 9),
    ("am ddeg o'r gloch", 10), ("am ddeuddeg o'r gloch", 12),
])
def test_am_names_a_bare_hour_and_mutates_it(text, h):
    """"am" (at) is itself a soft-mutation trigger, so the hour after it
    carries its mutated surface -- "am dri", not "am tri"."""
    assert start(text).hour == h


@pytest.mark.parametrize("text,h", [
    ("un o'r gloch", 1), ("tri o'r gloch", 3), ("deg o'r gloch", 10),
])
def test_oclock_without_the_preposition(text, h):
    assert start(text).hour == h


@pytest.mark.parametrize("text,h,mi", [
    ("15:30", 15, 30), ("09:05", 9, 5), ("00:00", 0, 0), ("23:59", 23, 59),
])
def test_digit_clock(text, h, mi):
    s = start(text)
    assert (s.hour, s.minute) == (h, mi)


@pytest.mark.parametrize("text,h", [("canol nos", 0), ("canol dydd", 12)])
def test_clock_landmarks(text, h):
    assert start(text).hour == h


@pytest.mark.parametrize("text", [
    "hanner awr",        # a bare half with no hour
    "wedi",              # a bare direction with nothing to count from
    "chwarter wedi",     # a direction with no hour named
])
def test_incomplete_clock_is_not_a_time(text):
    nomatch(text)
