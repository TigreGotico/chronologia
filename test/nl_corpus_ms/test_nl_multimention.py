# -*- coding: utf-8 -*-
"""Multi-mention in ms: extract_timespans -> all mentions in order."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "ms"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ('20 jun 2026 atau 4 ogos 2026', 2),
    ('semalam hari ini esok', 3),
    ('esok', 1),
    ('tiada masa di sini', 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions('20 jun 2026 atau 4 ogos 2026')
    assert [m.text for m in ms] == ['20 jun 2026', '4 ogos 2026']


def test_three_named_days_present():
    ms = mentions('semalam hari ini esok')
    assert len(ms) == 3
