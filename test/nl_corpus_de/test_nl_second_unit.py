# -*- coding: utf-8 -*-
"""The second as a duration unit in German.

``unit_second.voc`` closes the gap that left a phrase counting seconds
unparsed while the same phrase counting minutes resolved.  Every expected
span is the anchor shifted by the stated number of seconds, computed here
rather than read back from the engine.
"""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

from ._corpus import ANCHOR, ad, parse

LANG = "de"

#: (sentence, signed offset in seconds from the anchor)
_OFFSETS = [
    ("in 15 sekunden", 15),
    ("vor 30 sekunden", -30),
    ("in einer sekunde", 1),
    ("in 90 sekunden", 90),
    ("in 30 sek", 30),
]


@pytest.mark.parametrize("text,secs", _OFFSETS)
def test_second_offset_span(text, secs):
    res = parse(text)
    assert res is not None, f"{text!r} did not parse as a span"
    assert res.remainder == "", f"{text!r} stranded {res.remainder!r}"
    assert res[0].start == ad(ANCHOR + timedelta(seconds=secs))
    assert res[0].end == ad(ANCHOR + timedelta(seconds=secs + 1))


@pytest.mark.parametrize("text,secs", _OFFSETS)
def test_second_offset_duration(text, secs):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not read as a duration"
    assert got[0] == timedelta(seconds=abs(secs))
