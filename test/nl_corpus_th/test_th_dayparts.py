# -*- coding: utf-8 -*-
"""Day-part bands, transcribed from CLDR's day-period rules for th.

CLDR draws two afternoon rows and labels both บ่าย, so they are one band here.
The two evening rows are not joined: เย็น is the late afternoon and ค่ำ the
hours after dark, and a single band across both would answer 16:00-21:00 for a
word that means 18:00-21:00.
"""
import pytest

from ._corpus import band, start_end

BANDS = [
    ("เช้า", (6, 0), (12, 0), 0),
    ("บ่าย", (12, 0), (16, 0), 0),
    ("เย็น", (16, 0), (18, 0), 0),
    ("ค่ำ", (18, 0), (21, 0), 0),
    ("กลางคืน", (21, 0), (6, 0), 1),
]


@pytest.mark.parametrize("word,lo,hi,days", BANDS)
def test_each_band_spans_its_own_hours(word, lo, hi, days):
    assert start_end(word) == band(2027, 5, 12, lo, hi, days=days)


@pytest.mark.parametrize("word,lo,hi,days",
                         [b for b in BANDS if b[0] in ("เช้า", "บ่าย", "เย็น")])
def test_the_prefixed_forms_name_the_same_band(word, lo, hi, days):
    """CLDR's wide labels prefix ในตอน to the morning, afternoon and evening
    words; the bare and prefixed forms are the same band."""
    assert start_end("ในตอน" + word) == band(2027, 5, 12, lo, hi, days=days)


def test_the_late_afternoon_and_the_night_are_different_words():
    assert start_end("เย็น") != start_end("ค่ำ")


def test_the_night_wraps_midnight():
    s, e = start_end("กลางคืน")
    assert s.day == 12 and e.day == 13


def test_a_band_composes_with_a_named_day():
    assert start_end("พรุ่งนี้ เช้า") == band(2027, 5, 13, (6, 0), (12, 0))
