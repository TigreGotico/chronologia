# -*- coding: utf-8 -*-
"""The second as a duration unit in Romanian.

``unit_second.voc`` closes the gap that left a phrase counting seconds
unparsed while the same phrase counting minutes resolved.  Every expected
span is the anchor shifted by the stated number of seconds, computed here
rather than read back from the engine.
"""
from datetime import datetime, timedelta

import pytest

from chronologia.extract import extract_duration

from ._corpus import ANCHOR, ad, parse

LANG = "ro"

#: (sentence, signed offset in seconds from the anchor)
_OFFSETS = [
    ("peste 15 secunde", 15),
    ("acum 30 de secunde", -30),
    ("în 1 secundă", 1),
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
    ("a doua săptămână din martie", (2017, 3, 13), (2017, 3, 20)),
    ("al doilea trimestru din 2018", (2018, 4, 1), (2018, 7, 1)),
]


@pytest.mark.parametrize("text,first,last", _ORDINALS)
def test_ordinal_reading_survives(text, first, last):
    res = parse(text)
    assert res is not None, f"{text!r} lost its ordinal reading"
    assert res[0].start == ad(datetime(*first))
    assert res[0].end == ad(datetime(*last))
