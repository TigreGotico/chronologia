# -*- coding: utf-8 -*-
"""Multi-mention in et: extract_timespans -> all mentions in order."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "et"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ('20. juuni 2026 või 4. august 2026', 2),
    ('eile, täna ja homme', 3),
    ('homme', 1),
    ('ei midagi ajalist siin', 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions('20. juuni 2026 või 4. august 2026')
    assert [m.text for m in ms] == ['20. juuni 2026', '4. august 2026']


def test_three_named_days_in_order():
    ms = mentions('eile, täna ja homme')
    assert len(ms) == 3
