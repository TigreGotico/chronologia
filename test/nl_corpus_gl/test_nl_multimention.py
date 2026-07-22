# -*- coding: utf-8 -*-
"""Multi-mention in gl: extract_timespans -> all mentions in order."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "gl"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ('5 de xuño ou 4 de xullo', 2),
    ('onte, hoxe e mañá', 3),
    ('mañá', 1),
    ('nada temporal aquí', 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions('5 de xuño ou 4 de xullo')
    assert [m.text for m in ms] == ['5 de xuño', '4 de xullo']


def test_three_named_days_in_order():
    ms = mentions('onte, hoxe e mañá')
    assert len(ms) == 3
