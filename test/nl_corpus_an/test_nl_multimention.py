# -*- coding: utf-8 -*-
"""Multi-mention in an: extract_timespans -> all mentions in order."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "an"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ('5 de chunyo u 4 de chuliol', 2),
    ('ayere, hue y demán', 3),
    ('demán', 1),
    ('cosa temporal aquí', 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions('5 de chunyo u 4 de chuliol')
    assert [m.text for m in ms] == ['5 de chunyo', '4 de chuliol']


def test_three_named_days_in_order():
    ms = mentions('ayere, hue y demán')
    assert len(ms) == 3
