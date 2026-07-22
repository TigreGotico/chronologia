# -*- coding: utf-8 -*-
"""Multi-mention in kab: extract_timespans -> all mentions in order."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "kab"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ('20 yunyu 2026 neɣ 4 ɣuct 2026', 2),
    ('iḍelli assa azekka', 3),
    ('azekka', 1),
    ('ulac akud dagi', 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions('20 yunyu 2026 neɣ 4 ɣuct 2026')
    assert [m.text for m in ms] == ['20 yunyu 2026', '4 ɣuct 2026']


def test_three_named_days_present():
    ms = mentions('iḍelli assa azekka')
    assert len(ms) == 3
