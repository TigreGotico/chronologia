# -*- coding: utf-8 -*-
"""Multi-mention in cs: extract_timespans -> all mentions in order."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "cs"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ('20 června 2026 nebo 4 srpna 2026', 2),
    ('včera, dnes a zítra', 3),
    ('zítra', 1),
    ('nic časového tady', 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions('20 června 2026 nebo 4 srpna 2026')
    assert [m.text for m in ms] == ['20 června 2026', '4 srpna 2026']


def test_three_named_days_in_order():
    ms = mentions('včera, dnes a zítra')
    assert len(ms) == 3
