"""Finnish toward-hour spoken clock at the twelve boundary.

Finnish "puoli yhdeksän" is 08:30, half an hour short of nine.  At the first
hour the hour short of one is twelve, so "puoli yksi" is 12:30.  Citations,
both with a worked numeric example:
  - Tatoeba sentences aligned to English: "Kello on puoli yksi." == "It's
    half past twelve." and "Kello löi puoli yksi." == "The clock struck half
    past 12."
  - fi.wiktionary.org/wiki/puoli illustrates the sense with a clock face
    reading 01:30 captioned "Kello on puoli kaksi".

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
    ('puoli yksi', 12, 30),
    ('puoli yhdeksän', 8, 30),
    ('puoli kaksitoista', 11, 30),
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
    assert start('puoli yksi') == _next_time(12, 30)
    assert _next_time(13, 0) - start('puoli yksi') == timedelta(minutes=30)


def test_bare_fraction_without_hour_is_not_a_clock():
    nomatch('puoli')


def test_plain_hour_is_untouched():
    # The whole-hour reading shares the resolver path the fraction fold sits
    # in; it must stay exactly where it was.
    assert start('kello yhdeksän') == _next_time(9, 0)
