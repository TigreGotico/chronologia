# -*- coding: utf-8 -*-
"""Tuesday written with a space, "سه شنبه", is Tuesday, not Saturday.

The OVOS utterance normalizer writes the joiner of "سه‌شنبه" (Wiktionary) as a
space, and "شنبه" alone is Saturday.  Anchor: Tuesday 2017-06-27 13:04.  The
issue allows today or the next Tuesday, 2017-07-04.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ISSUE = "https://github.com/TigreGotico/chronologia/issues/989"
ANCHOR = datetime(2017, 6, 27, 13, 4)


@pytest.mark.xfail(raises=AssertionError, strict=True, reason=ISSUE)
def test_spaced_tuesday_at_one_am_is_a_tuesday():
    found = extract_timespan(
        "هوا سه شنبه ساعت یک بامداد چطور خواهد بود", "fa", ANCHOR)
    assert found.span.start.datetime() in (
        datetime(2017, 6, 27, 1, 0), datetime(2017, 7, 4, 1, 0))


@pytest.mark.xfail(raises=AssertionError, strict=True, reason=ISSUE)
def test_spaced_tuesday_morning_is_a_tuesday():
    found = extract_timespan("دمای پایین روز سه شنبه صبح چیست", "fa", ANCHOR)
    assert found.span.start.datetime().date() in (
        datetime(2017, 6, 27).date(), datetime(2017, 7, 4).date())
