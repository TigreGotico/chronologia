"""Polish spoken clock -- a split system.

The HALF counts TOWARD the coming hour: "wpół do dziewiątej" == half toward
nine == 08:30 (the "do" is the ordinary "to" connector).  The QUARTER, by
contrast, uses the ordinary past/to reading like English: "kwadrans po
dziewiątej" == a quarter PAST nine == 09:15, "za kwadrans dziesiąta" == a
quarter TO ten == 09:45.  So the half is toward-hour while the quarter is not
-- modelled separately (bare_half_to set, bare_quarter_to deliberately NOT).
Citation: Poradnia Językowa PWN (sjp.pwn.pl); PAN wsjp.pl.  Exact H:MM.
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
    ("wpół do dziewiątej", 8, 30),   # half toward nine
    ("wpół do dziesiątej", 9, 30),
    ("wpół do ósmej", 7, 30),
    ("wpół do pierwszej", 12, 30),   # half toward one -> 12:30
])
def test_half_toward_coming_hour(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,h,mi", [
    ("kwadrans po dziewiątej", 9, 15),   # a quarter past nine (ordinary)
    ("kwadrans po dziesiątej", 10, 15),
])
def test_quarter_past_ordinary(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,h,mi", [
    ("za kwadrans dziesiąta", 9, 45),    # a quarter to ten (ordinary)
    ("za kwadrans dziewiąta", 8, 45),
])
def test_quarter_to_ordinary(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text", [
    "wpół",             # bare half, no hour
    "kwadrans",         # bare quarter, no hour
    "wpół do",          # half toward nothing
])
def test_bare_fraction_without_hour_is_not_a_clock(text):
    nomatch(text)
