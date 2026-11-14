# -*- coding: utf-8 -*-
"""Durations in French: ``extract_duration(text, "fr")`` -> timedelta."""
from datetime import datetime, timedelta

import pytest
from dateutil.relativedelta import relativedelta

from chronologia.extract import extract_duration

LANG = "fr"

_CASES = [
    ("5 minutes", timedelta(minutes=5)),
    ("1 minute", timedelta(minutes=1)),
    ("2 heures", timedelta(hours=2)),
    ("une heure", timedelta(hours=1)),
    ("4 heures", timedelta(hours=4)),
    ("un jour", timedelta(days=1)),
    ("3 semaines", timedelta(weeks=3)),
    ("une demi-heure", timedelta(minutes=30)),
    ("un quart d heure", timedelta(minutes=15)),
    ("trois quarts d heure", timedelta(minutes=45)),
    ("une heure et demie", timedelta(hours=1, minutes=30)),
    ("deux heures et demie", timedelta(hours=2, minutes=30)),
    ("2 jours 4 heures", timedelta(days=2, hours=4)),
    ("1 heure 30 minutes", timedelta(hours=1, minutes=30)),
    ("45 minutes", timedelta(minutes=45)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ["bonjour le monde"])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None


def test_a_calendar_unit_counts_from_the_anchor():
    anchor = datetime(2026, 12, 31, 10, 0)
    got = extract_duration("2 mois", LANG, anchor=anchor)
    assert got == (anchor + relativedelta(months=2) - anchor, "")
