# -*- coding: utf-8 -*-
"""Multi-mention in ar: extract_timespans -> all mentions in order."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "ar"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ('20 يونيو 2026 أو 4 أغسطس 2026', 2),
    ('أمس اليوم غد', 3),
    ('غد', 1),
    ('لا شيء زمني هنا', 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions('20 يونيو 2026 أو 4 أغسطس 2026')
    assert [m.text for m in ms] == ['20 يونيو 2026', '4 أغسطس 2026']


def test_three_named_days_present():
    ms = mentions('أمس اليوم غد')
    assert len(ms) == 3
