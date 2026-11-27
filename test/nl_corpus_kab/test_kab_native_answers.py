# -*- coding: utf-8 -*-
"""Kabyle forms from the native answer, chronologia#1489 (comment 7218700864).

Anchor Tuesday 2017-06-27 13:04.  Gold is calendar arithmetic from the
anchor with ``timedelta``; Islamic dates are Umm al-Qura (Eid al-Fitr 1439
= 2018-06-15).
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_timespan
from chronologia.extract import extract_recurrence

from ._corpus import ANCHOR, LANG

SOURCE = "native answer, chronologia#1489 (comment 7218700864)"

MIDNIGHT = ANCHOR.replace(hour=0, minute=0)
NEXT_MONDAY = MIDNIGHT + timedelta(days=(0 - ANCHOR.weekday()) % 7 or 7)
THIS_MONDAY = MIDNIGHT - timedelta(days=ANCHOR.weekday())


def _start(text):
    r = extract_timespan(text, LANG, ANCHOR)
    assert r is not None, f"{text!r} did not parse ({SOURCE})"
    return r.span.start.datetime()


@pytest.mark.parametrize("text,expected", [
    # 1, 3, 14, 4: "akka N n wussan" = in N days
    ("akka yiwen n wass", ANCHOR + timedelta(days=1)),
    ("akka tlata n wussan", ANCHOR + timedelta(days=3)),
    ("akka ṛebɛa n wussan", ANCHOR + timedelta(days=4)),
    # 8: Friday next week, with "ssmana" as the week noun
    ("lǧemɛa n ssmana i d-iteddun", NEXT_MONDAY + timedelta(days=4)),
    # 15: "izrin" = last
    ("ddurt izrin", THIS_MONDAY - timedelta(days=7)),
    ("ssmana izrin", THIS_MONDAY - timedelta(days=7)),
    ("ssmana iɛeddan", THIS_MONDAY - timedelta(days=7)),
    ("letnayen izrin", THIS_MONDAY),
    # 10: holidays
    ("Tawwurt n useggas amaynut", datetime(2018, 1, 1)),
    ("Lɛid abesṭuḥ", datetime(2018, 6, 15)),
    ("lɛid amecṭuḥ", datetime(2018, 6, 15)),
    ("Nuwil", datetime(2017, 12, 25)),
    # 11: at night, today
    ("n yiḍ", MIDNIGHT + timedelta(hours=21)),
    ("n deg yiḍ", MIDNIGHT + timedelta(hours=21)),
])
def test_native_answer_start(text, expected):
    assert _start(text) == expected


@pytest.mark.parametrize("text", ["seg letnayen alamma d lexmis",
                                  "seg letnayen ar lexmis"])
def test_monday_to_thursday(text):
    # 7: the range ends at the end of Thursday of the coming week.
    r = extract_timespan(text, LANG, ANCHOR)
    assert r is not None
    assert r.span.start.datetime() == NEXT_MONDAY
    assert r.span.end.datetime() == NEXT_MONDAY + timedelta(days=4)


@pytest.mark.parametrize("text", ["yal letnayen", "kul letnayen",
                                  "mkul letnayen"])
def test_every_monday(text):
    # 9, 13
    got = extract_recurrence(text, LANG)
    assert got is not None and got[0].to_string() == "FREQ=WEEKLY;BYDAY=MO"
