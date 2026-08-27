# -*- coding: utf-8 -*-
"""The six-hour clock: forward-counted minutes on a cyclically named hour.

Thai never says "minutes to the hour"; a count after the hour word is always
added to it, and ครึ่ง is the half.  The hour's name, though, is not the
24-hour number: ตี names the small hours, ทุ่ม the evening, โมงเช้า the
morning, and บ่าย the early afternoon, each restarting its own count.
"""
import pytest

from ._corpus import minute_at, start_end

TOMORROW = (2027, 5, 13)
TODAY = (2027, 5, 12)


@pytest.mark.parametrize("text,hour", [
    ("ตีหนึ่ง", 1), ("ตีสอง", 2), ("ตีสาม", 3), ("ตีสี่", 4), ("ตีห้า", 5),
])
def test_the_small_hours_count_straight(text, hour):
    """ตี N is N o'clock in the morning, N running 1 to 5."""
    assert start_end(text) == minute_at(*TOMORROW, hour, 0)


@pytest.mark.parametrize("text,hour", [
    ("หนึ่งทุ่ม", 19), ("สองทุ่ม", 20), ("สามทุ่ม", 21),
    ("สี่ทุ่ม", 22), ("ห้าทุ่ม", 23),
])
def test_the_evening_hours_count_from_six_pm(text, hour):
    """N ทุ่ม is 18 + N: หนึ่งทุ่ม is 19:00 and สามทุ่ม is 21:00."""
    assert start_end(text) == minute_at(*TODAY, hour, 0)


@pytest.mark.parametrize("text,hour", [
    ("หกโมงเช้า", 6), ("เจ็ดโมงเช้า", 7), ("แปดโมงเช้า", 8),
    ("เก้าโมงเช้า", 9), ("สิบโมงเช้า", 10), ("สิบเอ็ดโมงเช้า", 11),
])
def test_the_morning_hours_read_directly(text, hour):
    assert start_end(text) == minute_at(*TOMORROW, hour, 0)


def test_one_in_the_afternoon_has_its_own_name():
    """บ่ายโมง carries no numeral at all and is 13:00."""
    assert start_end("บ่ายโมง") == minute_at(*TOMORROW, 13, 0)


@pytest.mark.parametrize("text,hour", [("บ่ายสองโมง", 14), ("บ่ายสามโมง", 15)])
def test_the_early_afternoon_counts_from_noon(text, hour):
    assert start_end(text) == minute_at(*TODAY, hour, 0)


def test_six_in_the_evening():
    assert start_end("หกโมงเย็น") == minute_at(*TODAY, 18, 0)


@pytest.mark.parametrize("text,hm", [
    ("หนึ่งทุ่มสามสิบ", (19, 30)),
    ("หนึ่งทุ่มครึ่ง", (19, 30)),
    ("สามทุ่มครึ่ง", (21, 30)),
    ("หนึ่งทุ่มห้านาที", (19, 5)),
    ("สองทุ่มยี่สิบห้านาที", (20, 25)),
])
def test_minutes_are_added_to_the_hour_just_named(text, hm):
    assert start_end(text) == minute_at(*TODAY, *hm)


@pytest.mark.parametrize("text,hm", [
    ("บ่ายโมงสิบห้านาที", (13, 15)),
    ("บ่ายสองโมงครึ่ง", (14, 30)),
])
def test_the_afternoon_takes_the_same_forward_minutes(text, hm):
    assert start_end(text) == minute_at(*TODAY, *hm)


@pytest.mark.parametrize("text,hm", [
    ("ตีสามครึ่ง", (3, 30)),
    ("ตีสองสิบนาที", (2, 10)),
    ("แปดโมงเช้าครึ่ง", (8, 30)),
])
def test_the_minute_word_is_optional(text, hm):
    assert start_end(text) == minute_at(*TOMORROW, *hm)


def test_the_landmarks_are_their_own_words():
    assert start_end("เที่ยง") == minute_at(*TOMORROW, 12, 0)
    assert start_end("เที่ยงคืน") == minute_at(*TOMORROW, 0, 0)


def test_a_digital_reading_still_parses():
    """Written Thai also uses plain 24-hour notation, which needs no cycle."""
    assert start_end("14:30") == minute_at(*TODAY, 14, 30)


def test_an_unspaced_minute_tail_that_spells_a_larger_number_is_refused():
    """ตีห้าสิบนาที can be cut as ตี + ห้าสิบ (50) นาที or as ตีห้า + สิบ (10)
    นาที, and with no space between the words nothing in the string chooses.
    The numeral reader takes the longest well-formed numeral, 50, which is no
    hour at all -- so the phrase is withdrawn instead of being cut the other
    way on a guess."""
    from ._corpus import nomatch
    nomatch("ตีห้าสิบนาที")
