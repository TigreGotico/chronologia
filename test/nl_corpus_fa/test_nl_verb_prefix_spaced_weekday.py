# -*- coding: utf-8 -*-
"""The verb prefix "می" is no month, and "سه شنبه" is Tuesday.

"می" before a verb is the durative prefix (Wiktionary "می‌-"), and the OVOS
utterance normalizer writes its joiner as a space.  "سه شنبه" is Tuesday
(Wiktionary "سه‌شنبه"); "شنبه" alone is Saturday.  Anchor: Tuesday 2017-06-27
13:04, so tomorrow is 2017-06-28 and the next Monday is 2017-07-03.  "Tuesday
at 1 am" is 01:00 today or the next Tuesday, 2017-07-04 01:00, as the issue
allows.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ISSUE = "https://github.com/TigreGotico/chronologia/issues/989"
ANCHOR = datetime(2017, 6, 27, 13, 4)


@pytest.mark.xfail(strict=True, reason=ISSUE)
@pytest.mark.parametrize("text", [
    "این سرمای شدید هوا ادامه پیدا می کند",
    "بیرون باد می وزد یا هوا آرام است",
    "این فیلم طول می کشد",
    "می خوام برم",
])
def test_the_verb_prefix_is_no_month(text):
    assert extract_timespan(text, "fa", ANCHOR) is None


@pytest.mark.xfail(strict=True, reason=ISSUE)
def test_the_verb_prefix_beside_tomorrow_leaves_tomorrow():
    found = extract_timespan(
        "می خواهم بدانم هوای فردا قرار است چطور باشد", "fa", ANCHOR)
    assert found.span.start.datetime() == datetime(2017, 6, 28)


@pytest.mark.xfail(strict=True, reason=ISSUE)
def test_spaced_tuesday_at_one_am_is_a_tuesday():
    found = extract_timespan(
        "هوا سه شنبه ساعت یک بامداد چطور خواهد بود", "fa", ANCHOR)
    assert found.span.start.datetime() in (
        datetime(2017, 6, 27, 1, 0), datetime(2017, 7, 4, 1, 0))


@pytest.mark.xfail(strict=True, reason=ISSUE)
def test_spaced_tuesday_morning_is_a_tuesday():
    found = extract_timespan("دمای پایین روز سه شنبه صبح چیست", "fa", ANCHOR)
    assert found.span.start.datetime().weekday() == 1


@pytest.mark.xfail(strict=True, reason=ISSUE)
def test_monday_morning_is_the_next_monday():
    found = extract_timespan(
        "دمای هوا صبح دوشنبه چند درجه می شود", "fa", ANCHOR)
    assert found.span.start.datetime().date() == datetime(2017, 7, 3).date()
