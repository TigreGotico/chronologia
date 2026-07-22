# -*- coding: utf-8 -*-
"""Multi-mention in pl: extract_timespans -> all mentions in order."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "pl"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ('20 czerwca 2026 lub 4 sierpnia 2026', 2),
    ('wczoraj, dziś i jutro', 3),
    ('jutro', 1),
    ('nic czasowego tutaj', 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions('20 czerwca 2026 lub 4 sierpnia 2026')
    assert [m.text for m in ms] == ['20 czerwca 2026', '4 sierpnia 2026']


def test_three_named_days_in_order():
    ms = mentions('wczoraj, dziś i jutro')
    assert len(ms) == 3
