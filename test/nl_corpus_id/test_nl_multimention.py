# -*- coding: utf-8 -*-
"""Multi-mention in id: extract_timespans -> all mentions in order."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "id"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ('20 juni 2026 atau 4 agustus 2026', 2),
    ('kemarin hari ini besok', 3),
    ('besok', 1),
    ('tidak ada waktu di sini', 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions('20 juni 2026 atau 4 agustus 2026')
    assert [m.text for m in ms] == ['20 juni 2026', '4 agustus 2026']


def test_three_named_days_present():
    ms = mentions('kemarin hari ini besok')
    assert len(ms) == 3
