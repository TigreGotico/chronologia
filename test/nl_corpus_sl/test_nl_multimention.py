# -*- coding: utf-8 -*-
"""Multi-mention in sl: extract_timespans -> all mentions in order."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "sl"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ('20 junija 2026 ali 4 avgusta 2026', 2),
    ('včeraj, danes in jutri', 3),
    ('jutri', 1),
    ('nič časovnega tukaj', 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions('20 junija 2026 ali 4 avgusta 2026')
    assert [m.text for m in ms] == ['20 junija 2026', '4 avgusta 2026']


def test_three_named_days_in_order():
    ms = mentions('včeraj, danes in jutri')
    assert len(ms) == 3
