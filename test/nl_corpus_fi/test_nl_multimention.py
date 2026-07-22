# -*- coding: utf-8 -*-
"""Multi-mention in fi: extract_timespans -> all mentions in order."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "fi"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ('20 heinäkuuta 2026 tai 4 elokuuta 2026', 2),
    ('eilen, tänään ja huomenna', 3),
    ('huomenna', 1),
    ('ei mitään ajallista tässä', 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions('20 heinäkuuta 2026 tai 4 elokuuta 2026')
    assert [m.text for m in ms] == ['20 heinäkuuta 2026', '4 elokuuta 2026']


def test_three_named_days_in_order():
    ms = mentions('eilen, tänään ja huomenna')
    assert len(ms) == 3
