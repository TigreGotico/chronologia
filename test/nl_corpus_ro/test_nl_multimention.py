# -*- coding: utf-8 -*-
"""Multi-mention in ro: extract_timespans -> all mentions in order."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "ro"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ('5 iunie sau 4 iulie', 2),
    ('ieri, azi și mâine', 3),
    ('mâine', 1),
    ('nimic temporal aici', 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions('5 iunie sau 4 iulie')
    assert [m.text for m in ms] == ['5 iunie', '4 iulie']


def test_three_named_days_in_order():
    ms = mentions('ieri, azi și mâine')
    assert len(ms) == 3
