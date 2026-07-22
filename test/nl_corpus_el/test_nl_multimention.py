# -*- coding: utf-8 -*-
"""Multi-mention in el: extract_timespans -> all mentions in order."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "el"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ('20 ιουνίου 2026 ή 4 αυγούστου 2026', 2),
    ('χθες, σήμερα και αύριο', 3),
    ('αύριο', 1),
    ('τίποτα χρονικό εδώ', 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions('20 ιουνίου 2026 ή 4 αυγούστου 2026')
    assert [m.text for m in ms] == ['20 ιουνίου 2026', '4 αυγούστου 2026']


def test_three_named_days_in_order():
    ms = mentions('χθες, σήμερα και αύριο')
    assert len(ms) == 3
