# -*- coding: utf-8 -*-
"""Eras and deep time: ق.م (BC), م (AD), ق.ح (BP), and numeric deep time
(قبل N مليون سنة).  BC/AD/BP expected years come from independent arithmetic
against the same era conventions the English reference uses."""
import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR, AstroDate, start_end


# each ar era phrase must resolve to the SAME span as its English twin
@pytest.mark.parametrize("ar,en", [
    ("44 ق.م", "44 bc"),
    ("753 ق.م", "753 bc"),
    ("1 ق.م", "1 bc"),
    ("1492 م", "1492 ad"),
    ("2024 م", "2024 ad"),
    ("2000 ق.ح", "2000 bp"),
    ("5000 ق.ح", "5000 bp"),
    ("قبل 66 مليون سنة", "66 million years ago"),
    ("قبل 4 مليار سنة", "4 billion years ago"),
    ("قبل 12 ألف سنة", "12 thousand years ago"),
])
def test_era_matches_en(ar, en):
    a = extract_timespan(ar, "ar", ANCHOR)
    b = extract_timespan(en, "en", ANCHOR)
    assert a is not None, f"{ar!r} did not parse"
    assert b is not None, f"{en!r} did not parse"
    assert (a[0].start, a[0].end) == (b[0].start, b[0].end)


@pytest.mark.parametrize("text,y0,y1", [
    ("44 ق.م", -43, -42),
    ("1492 م", 1492, 1493),
])
def test_era_absolute(text, y0, y1):
    ss, ee = start_end(text)
    assert ss == AstroDate(y0, 1, 1) and ee == AstroDate(y1, 1, 1)
