"""Indonesian toward-hour spoken clock at the twelve boundary.

Indonesian "setengah sembilan" is 08:30 -- half of the way to nine, not half
past it.  At the first hour the hour being counted from is twelve, so
"setengah satu" is 12:30.  Citations, both with a worked numeric example:
  - Tatoeba sentence aligned to English: "Sekarang jam setengah satu." ==
    "It's half past twelve."
  - en.wiktionary.org/wiki/half_past, translations table keyed to the worked
    example "half past one" (1:30): Indonesian "setengah dua", where "dua"
    (two) is the coming hour.

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
    ('setengah satu', 12, 30),
    ('setengah sembilan', 8, 30),
    ('setengah dua belas', 11, 30),
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
    assert start('setengah satu') == _next_time(12, 30)
    assert _next_time(13, 0) - start('setengah satu') == timedelta(minutes=30)


def test_bare_fraction_without_hour_is_not_a_clock():
    nomatch('setengah')


def test_plain_hour_is_untouched():
    # The whole-hour reading shares the resolver path the fraction fold sits
    # in; it must stay exactly where it was.
    assert start('jam sembilan') == _next_time(9, 0)
