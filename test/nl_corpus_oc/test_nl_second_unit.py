# -*- coding: utf-8 -*-
"""The second as a duration unit in Occitan.

``unit_second.voc`` closes the gap that left a phrase counting seconds
unparsed while the same phrase counting minutes resolved.  Every expected
span is the anchor shifted by the stated number of seconds, computed here
rather than read back from the engine.
"""
from datetime import datetime, timedelta

import pytest

from chronologia.extract import extract_duration

from ._corpus import ANCHOR, ad, parse

LANG = "oc"

#: (sentence, signed offset in seconds from the anchor)
_OFFSETS = [
    ("dins 15 segondas", 15),
    ("fa 30 segondas", -30),
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


# -- the unit word is also the ordinal "second"; the ordinal readings that
# -- already worked must be untouched by admitting the unit.

#: (sentence, expected span start, expected span end) as date triples
_ORDINALS = [
    ("la segonda setmana de març", (2017, 3, 13), (2017, 3, 20)),
    ("lo segond diluns de març", (2017, 3, 13), (2017, 3, 14)),
]


@pytest.mark.parametrize("text,first,last", _ORDINALS)
def test_ordinal_reading_survives(text, first, last):
    res = parse(text)
    assert res is not None, f"{text!r} lost its ordinal reading"
    assert res[0].start == ad(datetime(*first))
    assert res[0].end == ad(datetime(*last))


# -- a COUNT of exactly one, spelled with the surface the ordinal shares:
# -- "the second one" reads as readily as "one second", so the engine
# -- declines rather than pick, and no fabricated one-second span appears.

@pytest.mark.parametrize("text", [
    "dins 1 segonda",
])
def test_count_one_stays_refused(text):
    assert parse(text) is None, f"{text!r} fabricated a span"
    assert extract_duration(text, LANG) is None
