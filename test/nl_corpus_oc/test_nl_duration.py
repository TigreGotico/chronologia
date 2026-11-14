# -*- coding: utf-8 -*-
"""Durations in oc: extract_duration -> timedelta."""
from datetime import datetime, timedelta

import pytest
from dateutil.relativedelta import relativedelta

from chronologia.extract import extract_duration

LANG = "oc"

_CASES = [
    ('5 minutas', timedelta(minutes=5)),
    ('45 minutas', timedelta(minutes=45)),
    ('2 ora', timedelta(hours=2)),
    ('una ora', timedelta(hours=1)),
    ('un jorns', timedelta(days=1)),
    ('2 jorns', timedelta(days=2)),
    ('3 setmanas', timedelta(weeks=3)),
    ('90 minutas', timedelta(minutes=90)),
    ('mièja ora', timedelta(minutes=30)),
    ('un quart de ora', timedelta(minutes=15)),
    ('2 jorns 4 ora', timedelta(days=2, hours=4)),
    ('1 ora 30 minutas', timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['pas aicí'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None


def test_a_calendar_unit_counts_from_the_anchor():
    anchor = datetime(2026, 12, 31, 10, 0)
    got = extract_duration('2 meses', LANG, anchor=anchor)
    assert got == (anchor + relativedelta(months=2) - anchor, "")
