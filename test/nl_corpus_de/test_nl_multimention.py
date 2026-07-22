# -*- coding: utf-8 -*-
"""Multi-mention in German: ``extract_timespans(text, "de", anchor)``."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "de"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ("morgen oder nächste woche", 2),
    ("gestern, heute und morgen", 3),
    ("nur morgen", 1),
    ("nichts zeitliches hier", 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions("morgen oder nächste woche")
    assert [m.text for m in ms] == ["morgen", "nächste woche"]


def test_three_named_days_in_order():
    ms = mentions("gestern, heute und morgen")
    assert [m.span.start.day for m in ms] == [26, 27, 28]
