"""The Latvian spoken half hour, which counts toward the COMING hour.

"pusčetri" is half of the fourth hour -- 03:30, an hour earlier than the
English-shaped reading a reader might expect -- and Latvian writes it as one
word, the prefix "pus" fused onto the cardinal naming the hour being counted
toward.  Every case is pinned in BOTH directions: the right reading asserted
present and the additive reading ("half past four" = 04:30) asserted absent,
because a fold that inverted the direction would still produce a perfectly
plausible time.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, nomatch, start


def _next_time(h, mi):
    cand = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    return ad(cand)


#: (surface, the hour it means) -- the coming hour named by the word is one
#: MORE than the hour of the resulting time, written out by hand.
HALF_HOURS = [
    ("pusdivi", 1), ("pustrīs", 2), ("pusčetri", 3), ("puspieci", 4),
    ("pusseši", 5), ("pusseptiņi", 6), ("pusastoņi", 7), ("pusdeviņi", 8),
    ("pusdesmit", 9), ("pusvienpadsmit", 10), ("pusdivpadsmit", 11),
]


@pytest.mark.parametrize("text,hour", HALF_HOURS)
def test_half_names_the_coming_hour(text, hour):
    assert start(text) == _next_time(hour, 30)


@pytest.mark.parametrize("text,hour", HALF_HOURS)
def test_half_is_never_the_stated_hour(text, hour):
    """The additive reading -- "pusčetri" == 04:30 -- must never occur."""
    assert start(text).hour != hour + 1


def test_the_two_sourced_examples():
    """The worked pairs the rule was read off: "pusastoņi" is 7:30 and
    "pusčetri" is 3:30."""
    assert (start("pusastoņi").hour, start("pusastoņi").minute) == (7, 30)
    assert (start("pusčetri").hour, start("pusčetri").minute) == (3, 30)


def test_every_half_hour_lands_on_the_half():
    assert all(start(t).minute == 30 for t, _ in HALF_HOURS)


@pytest.mark.parametrize("text,h,mi", [
    ("15:30", 15, 30), ("09:05", 9, 5), ("00:00", 0, 0), ("23:59", 23, 59),
    ("07:30", 7, 30), ("12:00", 12, 0),
])
def test_digit_clock(text, h, mi):
    s = start(text)
    assert (s.hour, s.minute) == (h, mi)


@pytest.mark.parametrize("text,h", [("pusnakts", 0), ("pusnaktī", 0),
                                    ("pusdienlaikā", 12)])
def test_clock_landmarks(text, h):
    assert start(text).hour == h


@pytest.mark.parametrize("text", [
    "pus",              # a bare half with no hour
    "pusviens",         # the hour whose compound form no source attests
    "puse",             # the noun "half", not a clock reading
])
def test_incomplete_clock_is_not_a_time(text):
    nomatch(text)


def test_the_half_prefix_does_not_eat_a_noun():
    """"pusnakts" opens with the same three letters as the half-hour words and
    must stay the midnight landmark, not "half of a nakts"."""
    assert start("pusnakts").hour == 0
