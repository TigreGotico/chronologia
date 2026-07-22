# -*- coding: utf-8 -*-
"""Multi-mention in ast: extract_timespans -> all mentions in order."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "ast"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ('5 de xunu o 4 de xunetu', 2),
    ('ayeri, güei y mañana', 3),
    ('mañana', 1),
    ('nada temporal equí', 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions('5 de xunu o 4 de xunetu')
    assert [m.text for m in ms] == ['5 de xunu', '4 de xunetu']


def test_three_named_days_in_order():
    ms = mentions('ayeri, güei y mañana')
    assert len(ms) == 3
