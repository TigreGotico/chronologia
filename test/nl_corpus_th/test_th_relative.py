# -*- coding: utf-8 -*-
"""Relative time: a count and a unit with the direction word trailing.

Thai has no plural agreement, so CLDR carries one pattern per direction and
the unit noun never changes shape.  The past marker splits by unit in CLDR's
generation data -- ที่แล้ว for the year, ที่ผ่านมา for everything shorter --
but both forms occur on input for every unit and both are read.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, day, parse, start, start_end

UNITS = [("วัน", timedelta(days=1)), ("ชั่วโมง", timedelta(hours=1)),
         ("นาที", timedelta(minutes=1)), ("วินาที", timedelta(seconds=1)),
         ("สัปดาห์", timedelta(weeks=1))]


@pytest.mark.parametrize("noun,step", UNITS)
@pytest.mark.parametrize("n,word", [(2, "สอง"), (3, "สาม"), (5, "ห้า"),
                                    (10, "สิบ")])
def test_a_counted_offset_into_the_past(noun, step, n, word):
    assert start(f"{word}{noun}ที่ผ่านมา") == ad(ANCHOR - n * step)


@pytest.mark.parametrize("noun,step", UNITS)
@pytest.mark.parametrize("n,word", [(2, "สอง"), (4, "สี่"), (7, "เจ็ด")])
def test_a_counted_offset_into_the_future(noun, step, n, word):
    assert start(f"ในอีก{word}{noun}") == ad(ANCHOR + n * step)


@pytest.mark.parametrize("marker", ["ที่ผ่านมา", "ที่แล้ว"])
def test_both_past_markers_are_read_for_every_unit(marker):
    """CLDR splits the two by unit when generating text; on input both occur
    for all of them, so both must read the same offset."""
    assert start(f"สามวัน{marker}") == ad(ANCHOR - timedelta(days=3))


@pytest.mark.parametrize("noun,expect", [
    ("ปี", (2026, 1, 1)), ("เดือน", (2027, 4, 1)),
])
def test_the_previous_whole_period(noun, expect):
    assert start_end(f"{noun}ที่แล้ว")[0] == ad(
        __import__("datetime").datetime(*expect))


@pytest.mark.parametrize("noun,expect", [
    ("ปี", (2028, 1, 1)), ("เดือน", (2027, 6, 1)),
])
def test_the_next_whole_period(noun, expect):
    assert start_end(f"{noun}หน้า")[0] == ad(
        __import__("datetime").datetime(*expect))


@pytest.mark.parametrize("noun,expect", [
    ("ปี", (2027, 1, 1)), ("เดือน", (2027, 5, 1)),
])
def test_the_current_whole_period(noun, expect):
    assert start_end(f"{noun}นี้")[0] == ad(
        __import__("datetime").datetime(*expect))


@pytest.mark.parametrize("name,index", [
    ("วันจันทร์", 0), ("วันอังคาร", 1), ("วันพุธ", 2), ("วันพฤหัสบดี", 3),
    ("วันศุกร์", 4), ("วันเสาร์", 5), ("วันอาทิตย์", 6),
])
def test_every_weekday_name_reads_on_its_own(name, index):
    s = start(name)
    assert s.weekday() == index


@pytest.mark.parametrize("abbr,index", [
    ("จันทร์", 0), ("อังคาร", 1), ("พุธ", 2), ("พฤหัส", 3),
    ("ศุกร์", 4), ("เสาร์", 5), ("อาทิตย์", 6),
])
def test_the_short_weekday_forms_read_when_a_marker_frames_them(abbr, index):
    """CLDR's own relative-time data writes จันทร์ที่แล้ว for last Monday, so
    the prefixless form has to read; on its own it does not, because จันทร์ is
    equally the moon and อาทิตย์ equally the week."""
    s = start(f"{abbr}ที่แล้ว")
    assert s.weekday() == index
    assert s < ad(ANCHOR)


@pytest.mark.parametrize("text,expect", [
    ("วันนี้", (2027, 5, 12)),
    ("พรุ่งนี้", (2027, 5, 13)),
    ("เมื่อวาน", (2027, 5, 11)),
    ("มะรืนนี้", (2027, 5, 14)),
    ("เมื่อวานซืน", (2027, 5, 10)),
])
def test_the_named_days(text, expect):
    assert start_end(text) == day(*expect)


def test_a_named_day_leaves_no_remainder():
    r = parse("เมื่อวานซืน")
    assert r is not None and r[1] == ""
