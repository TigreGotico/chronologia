# -*- coding: utf-8 -*-
"""The translative ``-ksi`` planned-duration idiom in Finnish.

The translative states an *intended* length of time -- "kuinka pitkäksi ajaksi"
-- as in ``viideksi päiväksi`` (for five days) or ``vuodeksi`` (for a year),
distinct from the partitive ``viisi päivää`` that the corpus already reads.
See Uusi kielemme, "Expressions of Time" §6.1.

The unit side (``päiväksi``) folds, and numtag reads the translative
numeral (``viideksi`` = 5), so the digit and the spelled forms read alike.
"""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "fi"


@pytest.mark.parametrize("text,expected", [
    ('5 päiväksi', timedelta(days=5)),
    ('2 päiväksi', timedelta(days=2)),
    ('10 päiväksi', timedelta(days=10)),
])
def test_translative_digit_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text,expected", [
    ('viideksi päiväksi', timedelta(days=5)),
    ('kahdeksi päiväksi', timedelta(days=2)),
])
def test_spelled_translative_numeral(text, expected):
    assert extract_duration(text, LANG)[0] == expected


@pytest.mark.parametrize("text", ['2 kesäkuuta', 'ei mitään ajallista tässä'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None
