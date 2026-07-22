# -*- coding: utf-8 -*-
"""Multi-mention in French: ``extract_timespans(text, "fr", anchor)``."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "fr"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ("demain ou la semaine prochaine", 2),
    ("hier ou demain", 2),
    ("hier et demain", 2),
    ("hier, demain ou mardi prochain", 3),
    ("juste demain", 1),
    ("rien de temporel ici", 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions("demain ou la semaine prochaine")
    assert [m.text for m in ms] == ["demain", "la semaine prochaine"]


def test_three_mentions_in_order():
    ms = mentions("hier, demain ou mardi prochain")
    assert [m.span.start.day for m in ms] == [26, 28, 4]
