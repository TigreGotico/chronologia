# -*- coding: utf-8 -*-
"""The Basque -ko after a length: "hamar minutuko" is "of ten minutes" (Wiktionary, eu "-ko")."""
from datetime import date, datetime, timedelta

import pytest

from chronologia.extract import extract_duration


@pytest.mark.parametrize("text,expected", [
    ("hamar minutuko", timedelta(minutes=10)),
    ("ezarri hamar minutuko tenporizadore bat", timedelta(minutes=10)),
    ("programatu bost minutuko tenporizadorea", timedelta(minutes=5)),
    ("bi orduko", timedelta(hours=2)),
    ("hogei segundoko", timedelta(seconds=20)),
    ("hiru asteko", timedelta(weeks=3)),
])
def test_ko_length(text, expected):
    got = extract_duration(text, "eu")
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text,expected", [
    ("hiru hilabeteko", date(2017, 9, 27) - date(2017, 6, 27)),
    ("bi urteko", date(2019, 6, 27) - date(2017, 6, 27)),
])
def test_ko_length_of_calendar_units(text, expected):
    got = extract_duration(text, "eu", anchor=datetime(2017, 6, 27, 13, 4))
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got.duration == expected
