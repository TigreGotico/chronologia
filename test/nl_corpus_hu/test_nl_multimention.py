# -*- coding: utf-8 -*-
"""Multi-mention in hu: extract_timespans -> all mentions in order."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "hu"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ('2026. június 20. vagy 2026. augusztus 4.', 2),
    ('tegnap, ma és holnap', 3),
    ('holnap', 1),
    ('semmi időbeli itt', 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions('2026. június 20. vagy 2026. augusztus 4.')
    assert [m.text for m in ms] == ['2026. június 20.', '2026. augusztus 4.']


def test_three_named_days_in_order():
    ms = mentions('tegnap, ma és holnap')
    assert len(ms) == 3
