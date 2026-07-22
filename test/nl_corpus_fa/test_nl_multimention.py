# -*- coding: utf-8 -*-
"""Multi-mention in fa: extract_timespans -> all mentions in order."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "fa"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ('20 ژوئن 2026 یا 4 اوت 2026', 2),
    ('دیروز امروز فردا', 3),
    ('فردا', 1),
    ('اینجا چیز زمانی نیست', 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions('20 ژوئن 2026 یا 4 اوت 2026')
    assert [m.text for m in ms] == ['20 ژوئن 2026', '4 اوت 2026']


def test_three_named_days_present():
    ms = mentions('دیروز امروز فردا')
    assert len(ms) == 3
