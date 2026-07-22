# -*- coding: utf-8 -*-
"""Multi-mention in oc: extract_timespans -> all mentions in order."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "oc"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ('5 de junh o 4 de julhet', 2),
    ('ièr, uèi e deman', 3),
    ('deman', 1),
    ('pas res temporal aicí', 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions('5 de junh o 4 de julhet')
    assert [m.text for m in ms] == ['5 de junh', '4 de julhet']


def test_three_named_days_in_order():
    ms = mentions('ièr, uèi e deman')
    assert len(ms) == 3
