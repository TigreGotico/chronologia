# -*- coding: utf-8 -*-
"""Multi-mention in az: extract_timespans -> all mentions in order."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "az"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ('20 iyun 2026 və ya 4 avqust 2026', 2),
    ('dünən bugün sabah', 3),
    ('sabah', 1),
    ('burada vaxt yoxdur', 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions('20 iyun 2026 və ya 4 avqust 2026')
    assert [m.text for m in ms] == ['20 iyun 2026', '4 avqust 2026']


def test_three_named_days_present():
    ms = mentions('dünən bugün sabah')
    assert len(ms) == 3
