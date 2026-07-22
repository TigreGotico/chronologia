# -*- coding: utf-8 -*-
"""Durations in German: ``extract_duration(text, "de")`` -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "de"

_CASES = [
    ("5 minuten", timedelta(minutes=5)),
    ("1 minute", timedelta(minutes=1)),
    ("2 stunden", timedelta(hours=2)),
    ("eine stunde", timedelta(hours=1)),
    ("4 stunden", timedelta(hours=4)),
    ("ein tag", timedelta(days=1)),
    ("7 tage", timedelta(days=7)),
    ("3 wochen", timedelta(weeks=3)),
    ("eine woche", timedelta(weeks=1)),
    ("neunzig minuten", timedelta(minutes=90)),
    ("eine halbe stunde", timedelta(minutes=30)),
    ("eine viertel stunde", timedelta(minutes=15)),
    ("drei viertel stunde", timedelta(minutes=45)),
    ("2 tage 4 stunden", timedelta(days=2, hours=4)),
    ("1 stunde 30 minuten", timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ["2 monate", "hallo welt"])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None
