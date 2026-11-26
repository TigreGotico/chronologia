# -*- coding: utf-8 -*-
"""Clock readings in Persian."""
from datetime import datetime

import pytest

from chronologia import extract_timespan
from ._corpus import start
from ._corpus import ANCHOR
from ruling17 import moved


@pytest.mark.parametrize("text,h,m", [
    ("15:30", 15, 30), ("09:00", 9, 0), ("23:59", 23, 59),
    ("06:15", 6, 15), ("00:00", 0, 0), ("12:00", 12, 0)])
def test_iso_clock(text, h, m):
    s = start(text)
    assert (s.hour, s.minute) == (h, m)


@pytest.mark.parametrize("text,h", [
    ("ساعت 3", 3), ("ساعت 9", 9), ("ساعت 7", 7), ("ساعت 11", 11)])
def test_at_hour(text, h):
    assert start(text).hour == moved(h, ANCHOR)


@pytest.mark.parametrize("text,h", [("ظهر", 12), ("نیمه‌شب", 0)])
def test_landmarks(text, h):
    assert start(text).hour == h


@pytest.mark.xfail(raises=AssertionError, strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1345")
@pytest.mark.parametrize("text,expected", [
    ("ساعت بیست و دو و چهل و پنج دقیقه", datetime(2017, 6, 27, 22, 45)),
    ("ساعت ده و پانزده دقیقه", datetime(2017, 6, 27, 22, 15)),
    ("ساعت ۲۲ و ۴۵ دقیقه", datetime(2017, 6, 27, 22, 45)),
])
def test_minutes_after_va_join_the_hour(text, expected):
    # Anchor Tuesday 2017-06-27 13:04; 10:15 takes the next twelve-hour reading, 22:15
    result = extract_timespan(text, "fa", datetime(2017, 6, 27, 13, 4))
    assert (result.span.start.datetime(), result.remainder) == (expected, "")
