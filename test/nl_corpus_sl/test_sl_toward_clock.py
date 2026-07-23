"""Slovenian ordinal-toward-hour spoken clock.

Slovenian names the coming hour with a genitive-plural ordinal: "pol devetih"
== half toward the ninth == 08:30, "ob pol enih" == half toward one == 12:30
(the "ob" is the ordinary "at" connector; twelve-hour reckoning, so the hour
before one is spoken as twelve).  Citation: ZRC SAZU Jezikovna svetovalnica
(ISJFR / Fran), telling the time.  Exact H:MM, hand-derived.
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
    ("pol devetih", 8, 30),      # half toward the ninth
    ("pol desetih", 9, 30),
    ("pol osmih", 7, 30),
    ("ob pol enih", 12, 30),     # half toward one -> 12:30
    ("pol dvanajstih", 11, 30),
])
def test_half_toward_coming_hour(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text", [
    "pol",              # bare half, no hour
    "ob pol",           # half toward nothing
])
def test_bare_fraction_without_hour_is_not_a_clock(text):
    nomatch(text)
