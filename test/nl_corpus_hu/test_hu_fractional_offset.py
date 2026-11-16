"""Hungarian "fél óra múlva": a fraction of a unit counted from now.

"fél" is a half and "negyed" a quarter (en.wiktionary, s.v. fél, numeral
sense), so "fél óra múlva" is 30 minutes after the 13:04 anchor, 13:34, and
"negyed óra múlva" is 13:19.  "fél órával ezelőtt" is 30 minutes before,
12:34.  The quantifier is part of the offset, so it does not stay in the
remainder.

"másfél" is one and a half and "két és fél" two and a half (en.wiktionary,
s.v. másfél), so "másfél óra múlva" is 14:34 and "két és fél óra múlva" is
15:34.  The whole count is read, and no number word stays in the remainder.
"""
from datetime import timedelta

import pytest

from chronologia import extract_duration

from ._corpus import ANCHOR, ad, parse


@pytest.mark.parametrize("text,hour,minute", [
    ("fél óra múlva", 13, 34),
    ("negyed óra múlva", 13, 19),
    ("fél órával ezelőtt", 12, 34),
])
def test_fraction_of_an_hour(text, hour, minute):
    r = parse(text)
    assert r is not None
    assert r.span.start == ad(ANCHOR.replace(hour=hour, minute=minute))
    assert r.remainder == ""


@pytest.mark.parametrize("text,hour,minute", [
    ("két és fél óra múlva", 15, 34),
    ("másfél óra múlva", 14, 34),
])
def test_whole_and_a_half_hours(text, hour, minute):
    r = parse(text)
    assert r is not None
    assert r.span.start == ad(ANCHOR.replace(hour=hour, minute=minute))
    assert r.remainder == ""


@pytest.mark.parametrize("text,seconds", [
    ("két és fél óra", 9000),                 # 2.5 * 3600
    ("másfél óra", 5400),                     # 1.5 * 3600
    ("a film két és fél óra hosszú", 9000),   # the film is 2.5 hours long
    ("két és fél óra alatt", 9000),           # within 2.5 hours
])
def test_a_count_with_a_half_is_a_length_not_a_clock(text, seconds):
    # The clock says half past two as "fél három", never "két és fél óra",
    # so the phrase names a length and no point in time.
    assert parse(text) is None
    assert extract_duration(text, "hu").duration == timedelta(seconds=seconds)
