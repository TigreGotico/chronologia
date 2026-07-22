# -*- coding: utf-8 -*-
"""Multi-mention in hr: extract_timespans -> all mentions in order."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "hr"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ('20 lipnja 2026 ili 4 kolovoza 2026', 2),
    ('jučer, danas i sutra', 3),
    ('sutra', 1),
    ('ništa vremensko ovdje', 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions('20 lipnja 2026 ili 4 kolovoza 2026')
    assert [m.text for m in ms] == ['20 lipnja 2026', '4 kolovoza 2026']


def test_three_named_days_in_order():
    ms = mentions('jučer, danas i sutra')
    assert len(ms) == 3
