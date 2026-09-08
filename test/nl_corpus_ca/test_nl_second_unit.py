# -*- coding: utf-8 -*-
"""The second as a duration unit in Catalan.

``unit_second.voc`` closes the gap that left a phrase counting seconds
unparsed while the same phrase counting minutes resolved.  Every expected
span is the anchor shifted by the stated number of seconds, computed here
rather than read back from the engine.
"""
from datetime import datetime, timedelta

import pytest

from chronologia.extract import extract_duration

from ._corpus import ANCHOR, ad, parse

LANG = "ca"

#: (sentence, signed offset in seconds from the anchor)
_OFFSETS = [
    ("en 15 segons", 15),
    ("fa 30 segons", -30),
    ("dins de 15 segons", 15),
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
    ("el segon dilluns de març", (2017, 3, 13), (2017, 3, 14)),
    ("la segona setmana de març", (2017, 3, 13), (2017, 3, 20)),
    ("el segon trimestre de 2018", (2018, 4, 1), (2018, 7, 1)),
]


@pytest.mark.parametrize("text,first,last", _ORDINALS)
def test_ordinal_reading_survives(text, first, last):
    res = parse(text)
    assert res is not None, f"{text!r} lost its ordinal reading"
    assert res[0].start == ad(datetime(*first))
    assert res[0].end == ad(datetime(*last))


# -- a COUNT of exactly one, spelled with the surface the ordinal shares.
# -- After a count the word has one reading, the unit: "1 second" is a length
# -- and never "1 2nd".  The offset is the anchor shifted by one second; a bare
# -- count names a length and no point in time.

@pytest.mark.parametrize("text,secs", [
    ('un segon', None),
    ('1 segon', None),
])
def test_count_one_is_one_second(text, secs):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not read as a duration"
    assert got[0] == timedelta(seconds=1)
    res = parse(text)
    if secs is None:
        assert res is None, f"{text!r} fabricated a span from a bare length"
    else:
        assert res is not None, f"{text!r} did not parse as a span"
        assert res.remainder == ""
        assert res[0].start == ad(ANCHOR + timedelta(seconds=secs))
        assert res[0].end == ad(ANCHOR + timedelta(seconds=secs + 1))
