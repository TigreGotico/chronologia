# -*- coding: utf-8 -*-
"""Multi-mention in eu: extract_timespans -> all mentions in order."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "eu"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ('2026ko ekainaren 20an edo 2026ko abuztuaren 4an', 2),
    ('atzo, gaur eta bihar', 3),
    ('bihar', 1),
    ('ezer denborazkorik hemen', 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions('2026ko ekainaren 20an edo 2026ko abuztuaren 4an')
    assert [m.text for m in ms] == ['2026ko ekainaren 20an', '2026ko abuztuaren 4an']


def test_three_named_days_in_order():
    ms = mentions('atzo, gaur eta bihar')
    assert len(ms) == 3
