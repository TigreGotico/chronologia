"""A day word in the genitive-locative -ko before an absolutive daypart noun
("atzoko gaua" = last night, "biharko goiza" = tomorrow morning), "gau
honetan" (tonight), and the digit hour with the inessive glued on ("3etan").

Each -ko phrase names the same stretch as its inessive twin ("atzo gauean"),
so the twin is the independent gold; the day itself is anchor arithmetic.

Sources.  Wiktionary: atzoko ("yesterday's"), biharko ("tomorrow's"), gaua
(absolutive of gau), goiz and arratsalde (declension: goiza, arratsaldea),
egun (declension: eguneko), honetan (inessive of hau, "in this").
eu.wikipedia running text: "gaurko Algeria ekialdean" (X. mendea), "gaurko
eta herenegungo frantsesen abestien" (Éva Gauthier), "gau honetan sorginak
bildu ohi baitziren" (Walpurgis gaua), "Iluntzea, arratsa edo ilunsentia"
(Iluntze).  Euskaltzaindia Araua 37 "Data nola adierazi" writes the case
suffix onto the digit ("1995eko martxoaren 7an"), which is what "3etan" does.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, parse


def _same_span(text, twin, day_offset):
    a, b = parse(text), parse(twin)
    assert a is not None, f"{text!r} did not parse"
    assert b is not None, f"{twin!r} did not parse"
    assert a.remainder == "" and b.remainder == ""
    assert a[0].start == b[0].start and a[0].end == b[0].end
    assert a[0].start.day == (ANCHOR + timedelta(days=day_offset)).day


@pytest.mark.parametrize("text,twin,day_offset", [
    ("atzoko gaua", "atzo gauean", -1),
    ("herenegungo gaua", "herenegun gauean", -2),
    ("gaurko gaua", "gaur gauean", 0),
    ("biharko goiza", "bihar goizean", 1),
    ("atzoko arratsaldea", "atzo arratsaldean", -1),
    ("biharko iluntzea", "bihar iluntzean", 1),
])
def test_ko_day_with_absolutive_daypart(text, twin, day_offset):
    _same_span(text, twin, day_offset)


def test_tonight():
    _same_span("gau honetan", "gaur gauean", 0)


def test_last_night_is_a_night_band_yesterday():
    res = parse("atzoko gaua")
    assert res[0].start == ad(ANCHOR.replace(hour=21, minute=0) - timedelta(days=1))
    assert res[0].end == ad(ANCHOR.replace(hour=0, minute=0))


@pytest.mark.parametrize("text,h", [("3etan", 3), ("15etan", 15)])
def test_digit_hour_with_glued_inessive(text, h):
    res = parse(text)
    assert res is not None and res.remainder == ""
    cand = ANCHOR.replace(hour=h, minute=0, second=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    assert res[0].start == ad(cand)
    assert res[0].start == parse("hiruretan")[0].start if h == 3 else True
