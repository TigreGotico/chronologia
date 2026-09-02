"""Hungarian toward-hour spoken clock at the twelve boundary.

Hungarian names how far the clock has travelled toward the coming hour:
"negyed kilenc" is 08:15, "fél kilenc" 08:30, "háromnegyed kilenc" 08:45.
At the first hour the quarter, half and three-quarters all belong to twelve,
so they are 12:15, 12:30 and 12:45.  Citation with a worked numeric example
for each of the three fractions at exactly this boundary:
  - en.wiktionary.org/wiki/egykor, Hungarian: "negyed egykor" == "at a
    quarter past twelve", "fél egykor" == "at half past twelve",
    "háromnegyed egykor" == "at a quarter to one".

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
    ('fél egy', 12, 30),
    ('negyed egy', 12, 15),
    ('háromnegyed egy', 12, 45),
    ('fél kilenc', 8, 30),
    ('negyed kilenc', 8, 15),
    ('háromnegyed kilenc', 8, 45),
    ('fél tizenkettő', 11, 30),
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
    assert start('fél egy') == _next_time(12, 30)
    assert _next_time(13, 0) - start('fél egy') == timedelta(minutes=30)


def test_bare_fraction_without_hour_is_not_a_clock():
    nomatch('fél')


def test_plain_hour_is_untouched():
    # The whole-hour reading shares the resolver path the fraction fold sits
    # in; it must stay exactly where it was.
    assert start('kilenc órakor') == _next_time(9, 0)
