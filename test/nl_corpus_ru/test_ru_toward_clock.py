"""Russian ordinal-toward-hour spoken clock.

Colloquial Russian names the hour being APPROACHED with a genitive ordinal:
"половина девятого" / "полдевятого" == half OF the ninth == 08:30, "четверть
десятого" == a quarter OF the tenth == 09:15 (both counted toward the coming
hour).  The subtractive form names the REACHED hour: "без четверти десять" ==
without-a-quarter ten == 09:45.  Citation: gramota.ru (Russian State Language
reference service), telling the time.  Every edge hand-derived; exact H:MM.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start, nomatch


def _next_time(h, mi):
    cand = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    return ad(cand)


@pytest.mark.parametrize("text,h,mi", [
    ("половина девятого", 8, 30),   # half of the ninth
    ("полдевятого", 8, 30),         # contracted
    ("половина десятого", 9, 30),
    ("полдесятого", 9, 30),
    ("половина первого", 12, 30),   # half toward one -> 12:30 (12h reckoning)
    ("полвторого", 1, 30),
])
def test_half_toward_coming_hour(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,h,mi", [
    ("четверть десятого", 9, 15),   # a quarter of the tenth
    ("четверть девятого", 8, 15),
    ("четверть первого", 12, 15),
])
def test_quarter_toward_coming_hour(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,h,mi", [
    ("без четверти десять", 9, 45),  # a quarter to the reached hour ten
    ("без четверти девять", 8, 45),
    ("без четверти двенадцать", 11, 45),
])
def test_subtractive_to_reached_hour(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text", [
    "половина",         # bare half, no hour to count toward
    "четверть",
    "без четверти",     # a subtractive with no hour
])
def test_bare_fraction_without_hour_is_not_a_clock(text):
    nomatch(text)
