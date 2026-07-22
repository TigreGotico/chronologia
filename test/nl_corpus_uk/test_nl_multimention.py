# -*- coding: utf-8 -*-
"""Multi-mention in uk: extract_timespans -> all mentions in order."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "uk"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ('20 червня 2026 або 4 серпня 2026', 2),
    ('вчора, сьогодні і завтра', 3),
    ('завтра', 1),
    ('нічого часового тут', 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions('20 червня 2026 або 4 серпня 2026')
    assert [m.text for m in ms] == ['20 червня 2026', '4 серпня 2026']


def test_three_named_days_in_order():
    ms = mentions('вчора, сьогодні і завтра')
    assert len(ms) == 3
