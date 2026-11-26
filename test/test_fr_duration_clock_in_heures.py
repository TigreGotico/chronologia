# -*- coding: utf-8 -*-
"""fr: a clock in "heures" is no length.

"pour 7 heures demain matin" and "à 18 heures" name a clock, which
extract_timespan reads as 07:00 and 18:00 tomorrow.  Neither says a length,
so extract_duration returns None.  Anchor: Tuesday 2017-06-27 13:04.
"""
from datetime import datetime

import pytest

from chronologia import extract_duration

ISSUE = "https://github.com/TigreGotico/chronologia/issues/1063"


@pytest.mark.parametrize("text", [
    "crée un rappel pour appeler maman demain à 18 heures",
    pytest.param("mets une alarme pour 7 heures demain matin",
                 marks=pytest.mark.xfail(raises=AssertionError, strict=True, reason=ISSUE)),
])
def test_a_clock_in_heures_is_no_length(text):
    assert extract_duration(
        text, "fr", anchor=datetime(2017, 6, 27, 13, 4)) is None
