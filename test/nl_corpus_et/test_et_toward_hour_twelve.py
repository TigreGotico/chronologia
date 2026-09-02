"""Estonian toward-hour spoken clock at the twelve boundary.

Estonian counts toward the coming hour for both the half and the quarters:
"pool üheksa" is 08:30, "veerand üheksa" 08:15, "kolmveerand üheksa" 08:45.
At the first hour the hour being counted from is twelve, so "pool üks" is
12:30 and "veerand üks" 12:15.  Citations, both with a worked numeric
example:
  - EKI Sõnaveeb, "veerand" sense 1.1: "(kellaaja kohta:) 45 minutit enne
    täistundi, 15 minutit pärast eelmist täistundi", with the example
    "Loeng algab veerand üks." -- the boundary surface itself.
  - Tatoeba sentence aligned to English: "Kell on pool üks." == "It's half
    past twelve."

Exact H:MM, hand-derived from the anchor.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, nomatch, parse, start


def _next_time(h, mi):
    cand = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    return ad(cand)


@pytest.mark.parametrize("text,h,mi", [
    ('pool üks', 12, 30),
    ('veerand üks', 12, 15),
    ('kolmveerand üks', 12, 45),
    ('pool üheksa', 8, 30),
    ('veerand üheksa', 8, 15),
    ('kolmveerand üheksa', 8, 45),
    ('pool kaksteist', 11, 30),
])
def test_toward_hour_fractions(text, h, mi):
    got = parse(text)
    assert got is not None, f"{text!r} did not parse"
    span, remainder = got
    assert span.start == _next_time(h, mi)
    assert remainder == ""


def test_half_toward_one_is_thirty_minutes_before_one_o_clock():
    # Direction pin at the twelve boundary: the half hour that names the
    # coming first hour sits 30 minutes BEFORE it, and lands on twelve rather
    # than falling off the bottom of the clock to 00:30.  The comparison hour
    # is an absolute literal, never read back from the parser's own reading of
    # the fraction.
    assert start('pool üks') == _next_time(12, 30)
    assert _next_time(13, 0) - start('pool üks') == timedelta(minutes=30)


def test_bare_fraction_without_hour_is_not_a_clock():
    nomatch('pool')


def test_plain_hour_is_untouched():
    # The whole-hour reading shares the resolver path the fraction fold sits
    # in; it must stay exactly where it was.
    assert start('kell üheksa') == _next_time(9, 0)
