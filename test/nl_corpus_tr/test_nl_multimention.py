# -*- coding: utf-8 -*-
"""Multi-mention in tr: extract_timespans -> all mentions in order."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "tr"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ('20 haziran 2026 veya 4 ağustos 2026', 2),
    ('dün bugün yarın', 3),
    ('yarın', 1),
    ('burada zamansal bir şey yok', 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions('20 haziran 2026 veya 4 ağustos 2026')
    assert [m.text for m in ms] == ['20 haziran 2026', '4 ağustos 2026']


def test_three_named_days_present():
    ms = mentions('dün bugün yarın')
    assert len(ms) == 3
