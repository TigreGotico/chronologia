# -*- coding: utf-8 -*-
"""Multi-mention in ru: extract_timespans -> all mentions in order."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "ru"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ('20 июня 2026 или 4 августа 2026', 2),
    ('вчера, сегодня и завтра', 3),
    ('завтра', 1),
    ('ничего временного здесь', 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions('20 июня 2026 или 4 августа 2026')
    assert [m.text for m in ms] == ['20 июня 2026', '4 августа 2026']


def test_three_named_days_in_order():
    ms = mentions('вчера, сегодня и завтра')
    assert len(ms) == 3
