# -*- coding: utf-8 -*-
"""The Basque -ko after a length: "hamar minutuko" is "of ten minutes" (Wiktionary, eu "-ko")."""
from datetime import timedelta

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
