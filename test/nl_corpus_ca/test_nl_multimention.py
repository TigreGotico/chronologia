# -*- coding: utf-8 -*-
"""Multi-mention in ca: extract_timespans -> all mentions in order."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "ca"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ('5 de juny o 4 de juliol', 2),
    ('ahir, avui i demà', 3),
    ('demà', 1),
    ('res temporal aquí', 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions('5 de juny o 4 de juliol')
    assert [m.text for m in ms] == ['5 de juny', '4 de juliol']


def test_three_named_days_in_order():
    ms = mentions('ahir, avui i demà')
    assert len(ms) == 3
