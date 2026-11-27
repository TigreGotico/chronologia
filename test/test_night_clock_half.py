# -*- coding: utf-8 -*-
"""A night word beside a twelve-hour clock picks the half in the night.

Ruling 36: de "um elf Uhr nachts" and "um 11 Uhr nachts" are 23:00.  en
"night at 1" said at Sunday 2026-11-22 12:00 is 01:00 on 23 November: ruling
20 refuses a night word over 13 to 17.  Anchor for de: Tuesday 2017-06-27
13:04.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ISSUE = "https://github.com/TigreGotico/chronologia/issues/1079"


@pytest.mark.xfail(raises=AssertionError, strict=True, reason=ISSUE)
@pytest.mark.parametrize("text", [
    "um 11:00 nachts", "um 11 Uhr nachts", "um elf Uhr nachts",
])
def test_de_eleven_at_night_is_23_00(text):
    found = extract_timespan(text, "de", datetime(2017, 6, 27, 13, 4))
    assert found.span.start.datetime() == datetime(2017, 6, 27, 23, 0)


@pytest.mark.xfail(raises=AssertionError, strict=True, reason=ISSUE)
def test_en_night_at_one_is_01_00():
    found = extract_timespan("night at 1", "en", datetime(2026, 11, 22, 12, 0))
    assert found.span.start.datetime() == datetime(2026, 11, 23, 1, 0)
