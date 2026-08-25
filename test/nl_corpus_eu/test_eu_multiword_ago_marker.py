# -*- coding: utf-8 -*-
"""The two-word Basque "ago" marker ``orain dela``.

``chronologia/locale/eu/marker_ago.voc`` ships two surfaces, ``duela`` and
``orain dela``; both introduce (or, postposed, close) a deep-time distance
and must read alike.  ``orain dela`` is also a two-word past-direction
surface, so the token stream carries it as one glued token by the time the
grammar looks for the marker.

Gold is independent arithmetic, not a parser reading: deep time is counted
from the 1950 "present" of the Before Present convention, and the span is
one whole scale unit wide -- 66 million years ago starts at
1950 - 66,000,000 and runs a million years.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, parse, span

BP_EPOCH = 1950


def _deep(count, scale):
    start = BP_EPOCH - count * scale
    return start, start + scale


DEEP_CASES = [
    ("orain dela 66 milioi urte", 66, 1_000_000),
    ("orain dela 3 milioi urte", 3, 1_000_000),
    ("orain dela 3 mila urte", 3, 1_000),
    ("66 milioi urte orain dela", 66, 1_000_000),
    ("3 milioi urte orain dela", 3, 1_000_000),
    ("3 mila urte orain dela", 3, 1_000),
]


@pytest.mark.parametrize("text,count,scale", DEEP_CASES)
def test_deep_time_orain_dela(text, count, scale):
    sp = span(text)
    assert (sp.start.year, sp.end.year) == _deep(count, scale)


@pytest.mark.parametrize("text", [t for t, _, _ in DEEP_CASES])
def test_deep_time_orain_dela_consumed(text):
    assert parse(text).remainder == ""


@pytest.mark.parametrize("pre,post", [
    ("orain dela 66 milioi urte", "duela 66 milioi urte"),
    ("orain dela 3 milioi urte", "duela 3 milioi urte"),
    ("orain dela 3 mila urte", "duela 3 mila urte"),
])
def test_marker_synonyms_agree(pre, post):
    a, b = span(pre), span(post)
    assert (a.start, a.end) == (b.start, b.end)


def test_near_relative_offset_unchanged():
    # the everyday reading of the same marker: three days back from the anchor
    sp = span("orain dela 3 egun")
    assert sp.start == ANCHOR - timedelta(days=3)
