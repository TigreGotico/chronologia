# -*- coding: utf-8 -*-
"""Markers, open ranges and closed ranges."""
import pytest

from ._corpus import ad, ANCHOR, day, parse, span, start_end


def test_a_closed_range_between_two_weekdays():
    s, e = start_end("ตั้งแต่ วันจันทร์ ถึง วันศุกร์")
    assert (s, e) == (ad(__import__("datetime").datetime(2027, 5, 17)),
                      ad(__import__("datetime").datetime(2027, 5, 22)))


def test_the_between_marker_opens_the_same_range():
    assert start_end("ระหว่าง วันจันทร์ ถึง วันศุกร์") == \
        start_end("ตั้งแต่ วันจันทร์ ถึง วันศุกร์")


def test_a_range_inside_one_month():
    s, e = start_end("15 ถึง 20 มกราคม 2026")
    assert (s, e) == (day(2026, 1, 15)[0], day(2026, 1, 21)[0])


def test_an_open_range_up_to_a_weekday():
    s, e = start_end("ถึง วันศุกร์")
    assert s == ad(ANCHOR)
    assert e == ad(__import__("datetime").datetime(2027, 5, 15))


def test_an_open_range_before_a_weekday():
    s, e = start_end("ก่อน วันจันทร์")
    assert s == ad(ANCHOR)
    assert e == ad(__import__("datetime").datetime(2027, 5, 18))


def test_a_counted_offset_after_a_weekday_reads_unspaced():
    """หลัง counts the offset it follows, and the whole phrase written as one
    run segments into สาม + วัน + หลัง + วันจันทร์."""
    assert start_end("สามวันหลังวันจันทร์") == day(2027, 5, 20)
    assert start_end("สามวันหลังวันจันทร์") == start_end("สาม วัน หลัง วันจันทร์")


def test_a_range_needs_the_phrase_space_thai_writing_supplies():
    """Range detection reads the token stream BEFORE the segmenter runs, so a
    range written with no space anywhere returns a single endpoint with the
    rest as remainder rather than the whole range.  Thai spaces its phrases,
    so the written form has the space; the unspaced form is a partial reading
    with a visible remainder, never a confident wrong span."""
    r = parse("ตั้งแต่วันจันทร์ถึงวันศุกร์")
    assert r is not None and r[1] != ""
