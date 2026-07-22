# -*- coding: utf-8 -*-
"""Multi-mention in sk: extract_timespans -> all mentions in order."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "sk"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ('20 júna 2026 alebo 4 augusta 2026', 2),
    ('včera, dnes a zajtra', 3),
    ('zajtra', 1),
    ('nič časové tu', 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions('20 júna 2026 alebo 4 augusta 2026')
    assert [m.text for m in ms] == ['20 júna 2026', '4 augusta 2026']


def test_three_named_days_in_order():
    ms = mentions('včera, dnes a zajtra')
    assert len(ms) == 3
