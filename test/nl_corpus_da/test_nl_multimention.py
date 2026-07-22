# -*- coding: utf-8 -*-
"""Multi-mention in da: extract_timespans -> all mentions in order."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "da"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ('20 juni 2026 eller 4 august 2026', 2),
    ('igår, idag og imorgen', 3),
    ('imorgen', 1),
    ('intet tidsligt her', 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions('20 juni 2026 eller 4 august 2026')
    assert [m.text for m in ms] == ['20 juni 2026', '4 august 2026']


def test_three_named_days_in_order():
    ms = mentions('igår, idag og imorgen')
    assert len(ms) == 3
