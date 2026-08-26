# -*- coding: utf-8 -*-
"""Adversarial Thai cases plus the shared English semantic-parity block."""
import pytest

from ._corpus import ANCHOR, nomatch, parse


@pytest.mark.parametrize("text", ["25:00", "15:99", "99:99"])
def test_impossible_clock(text):
    r = parse(text)
    if r is not None:
        assert 0 <= r[0].start.hour <= 23


@pytest.mark.parametrize("text", ["วัน", "ปี", "เดือน", "สัปดาห์", "ชั่วโมง",
                                  "นาที", "วินาที"])
def test_a_bare_unit_without_a_count_is_not_an_offset(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


@pytest.mark.parametrize("text", ["ใน", "ก่อน", "หลัง", "ตั้งแต่", "ถึง",
                                  "ระหว่าง", "ทุก", "เมื่อ"])
def test_a_lone_marker_is_not_a_date(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["ที่แล้ว", "ที่ผ่านมา", "หน้า", "นี้",
                                  "ในอีก", "วันที่"])
def test_a_lone_relative_word_is_not_a_date(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["สาม", "ยี่สิบเอ็ด", "สิบห้า",
                                  "หนึ่งร้อยยี่สิบสาม", "ห้าสิบ"])
def test_a_bare_numeral_is_not_a_date(text):
    """A count with nothing counted names no time."""
    nomatch(text)


@pytest.mark.parametrize("text", ["ตี", "ทุ่ม", "โมง"])
def test_a_bare_hour_word_is_not_a_time(text):
    """ตี is equally the verb "to hit" and ทุ่ม "to hurl"; both are read as
    hour words only next to a numeral, and โมง never binds anything alone."""
    nomatch(text)


PAIRS = [
    ("วันนี้", "today"),
    ("พรุ่งนี้", "tomorrow"),
    ("เมื่อวาน", "yesterday"),
    ("เมื่อวานซืน", "the day before yesterday"),
    ("มะรืนนี้", "overmorrow"),
    ("สามวันที่ผ่านมา", "3 days ago"),
    ("ห้าวันที่ผ่านมา", "5 days ago"),
    ("สามชั่วโมงที่ผ่านมา", "3 hours ago"),
    ("สิบนาทีที่ผ่านมา", "10 minutes ago"),
    ("สามสิบวินาทีที่ผ่านมา", "30 seconds ago"),
    ("สองสัปดาห์ที่ผ่านมา", "2 weeks ago"),
    ("สามเดือนที่ผ่านมา", "3 months ago"),
    ("สองปีที่แล้ว", "2 years ago"),
    ("สิบเอ็ดปีที่แล้ว", "11 years ago"),
    ("สิบห้านาทีที่ผ่านมา", "15 minutes ago"),
    ("หนึ่งร้อยปีที่แล้ว", "100 years ago"),
    ("ยี่สิบเอ็ดวันที่ผ่านมา", "21 days ago"),
    ("ในอีกสองวัน", "in 2 days"),
    ("ในอีกสามชั่วโมง", "in 3 hours"),
    ("ในอีกสี่สิบห้านาที", "in 45 minutes"),
    ("ในอีกหนึ่งสัปดาห์", "in 1 week"),
    ("ในอีกหกเดือน", "in 6 months"),
    ("ในอีกยี่สิบสี่ชั่วโมง", "in 24 hours"),
    ("ปีนี้", "this year"),
    ("ปีที่แล้ว", "last year"),
    ("ปีหน้า", "next year"),
    ("เดือนนี้", "this month"),
    ("เดือนที่แล้ว", "last month"),
    ("เดือนหน้า", "next month"),
    ("สัปดาห์นี้", "this week"),
    ("สัปดาห์ที่แล้ว", "last week"),
    ("สัปดาห์หน้า", "next week"),
    ("วันจันทร์หน้า", "next monday"),
    ("วันศุกร์ที่แล้ว", "last friday"),
    ("วันอาทิตย์หน้า", "next sunday"),
    ("จันทร์ที่แล้ว", "last monday"),
    ("วันที่ 15 มกราคม 2026", "15 january 2026"),
    ("มกราคม 2026", "january 2026"),
    ("15 มีนาคม", "15 march"),
    ("ธันวาคม", "december"),
    ("สองพันยี่สิบหก", "2026"),
    ("เที่ยง", "noon"),
    ("เที่ยงคืน", "midnight"),
    ("ตีสาม", "3 am"),
    ("หนึ่งทุ่ม", "7 pm"),
    ("สามทุ่ม", "9 pm"),
    ("หกโมงเย็น", "6 pm"),
    ("บ่ายโมง", "1 pm"),
    ("บ่ายสองโมง", "2 pm"),
    ("แปดโมงเช้า", "8 am"),
]
