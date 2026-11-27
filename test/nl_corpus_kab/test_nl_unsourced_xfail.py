# -*- coding: utf-8 -*-
"""Kabyle forms that no source in hand attests.

Each one waits for the kab native reviewer
(https://github.com/TigreGotico/chronologia/issues/1485).  Gold is calendar
arithmetic from the anchor, Tuesday 2017-06-27 13:04.
"""
import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR, LANG

ISSUE = "kab form without a source, TigreGotico/chronologia#1485"


def _day(text):
    r = extract_timespan(text, LANG, ANCHOR)
    s = r.span.start if r else None
    return s and (s.year, s.month, s.day)


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=ISSUE)
@pytest.mark.parametrize("text,day", [
    ("Ad d-yas seld yiwen wass.", (2017, 6, 28)),      # in one day
    ("Ad d-yas deffir yiwen wass.", (2017, 6, 28)),    # in one day
    ("Ass n lḥed yezrin.", (2017, 6, 25)),             # last Sunday
    ("Larbeɛ yezrin.", (2017, 6, 21)),                 # last Wednesday
])
def test_unsourced_day(text, day):
    assert _day(text) == day


# Native answer, chronologia#1489 (comment 7218700864):
# "seg letnayen alamma d lexmis" = "seg letnayen ar lexmis".
def test_alamma_d_range_end():
    r = extract_timespan("seg letnayen alamma d lexmis", LANG, ANCHOR)
    assert r is not None and (r.span.end.month, r.span.end.day) == (7, 7)


# "ukkuẓ" is the annexed form of "kuẓ" (four): Tatoeba sentence 11394104
# "Sin ternuḍ sin, ɣur-k ukkuẓ." (two and two make four).
def test_in_four_days_annexed_kuz():
    assert _day("Ad d-yuɣal deg ukkuẓ n wussan.") == (2017, 7, 1)
