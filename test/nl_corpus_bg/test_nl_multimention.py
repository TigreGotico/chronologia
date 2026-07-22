# -*- coding: utf-8 -*-
"""Multi-mention in bg: extract_timespans -> all mentions in order."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "bg"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ('20 юни 2026 или 4 август 2026', 2),
    ('вчера, днес и утре', 3),
    ('утре', 1),
    ('нищо времево тук', 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions('20 юни 2026 или 4 август 2026')
    assert [m.text for m in ms] == ['20 юни 2026', '4 август 2026']


def test_three_named_days_in_order():
    ms = mentions('вчера, днес и утре')
    assert len(ms) == 3
