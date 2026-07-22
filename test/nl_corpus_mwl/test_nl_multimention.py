# -*- coding: utf-8 -*-
"""Multi-mention in mwl: extract_timespans -> all mentions in order."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "mwl"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ('5 de júnio ou 4 de júlio', 2),
    ('onte, hoije i manhana', 3),
    ('manhana', 1),
    ('nada temporal eiqui', 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions('5 de júnio ou 4 de júlio')
    assert [m.text for m in ms] == ['5 de júnio', '4 de júlio']


def test_three_named_days_in_order():
    ms = mentions('onte, hoije i manhana')
    assert len(ms) == 3
