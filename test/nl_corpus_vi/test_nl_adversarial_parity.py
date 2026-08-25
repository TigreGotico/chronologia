"""Adversarial Vietnamese cases plus the shared English semantic-parity block."""
import pytest

from ._corpus import ANCHOR, nomatch, parse


@pytest.mark.parametrize("text", [
    "", "   ", "xin chào bạn khỏe không", "qwerty zxcvb",
    "ở đây không có ngày tháng gì cả",
])
def test_junk_is_none(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["trước", "sau", "cách đây", "kém"])
def test_incomplete_offset(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


@pytest.mark.parametrize("text", [
    "hace tres días", "il y a trois jours", "vor drei Tagen",
    "three days ago",
])
def test_other_languages_are_not_matched(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


@pytest.mark.parametrize("text", ["32 tháng 1 năm 2020", "0 tháng 3 năm 2020"])
def test_impossible_day_of_month(text):
    r = parse(text)
    if r is not None:
        assert 1 <= r[0].start.day <= 31


#: (Vietnamese, English) pairs that mean the same thing and must resolve to
#: the same span under the same anchor.
PAIRS = [
    ("hôm nay", "today"),
    ("hôm qua", "yesterday"),
    ("ngày mai", "tomorrow"),
    ("hôm kia", "the day before yesterday"),
    ("ngày kia", "the day after tomorrow"),
    ("một ngày trước", "one day ago"),
    ("hai ngày trước", "two days ago"),
    ("ba ngày trước", "three days ago"),
    ("năm ngày trước", "five days ago"),
    ("mười ngày trước", "ten days ago"),
    ("hai mươi ngày trước", "twenty days ago"),
    ("ba mươi ngày trước", "thirty days ago"),
    ("cách đây ba ngày", "three days ago"),
    ("hai ngày sau", "in two days"),
    ("ba ngày sau", "in three days"),
    ("ba tháng trước", "three months ago"),
    ("sáu tháng trước", "six months ago"),
    ("hai tháng sau", "in two months"),
    ("hai năm trước", "two years ago"),
    ("mười năm trước", "ten years ago"),
    ("tháng sau", "next month"),
    ("tháng trước", "last month"),
    ("năm sau", "next year"),
    ("năm trước", "last year"),
    ("5 tháng 6 năm 2020", "5 june 2020"),
    ("31 tháng 12 năm 2000", "31 december 2000"),
    ("thứ hai", "monday"),
    ("thứ sáu", "friday"),
    ("2020", "2020"),
    ("15:30", "15:30"),
    ("nửa đêm", "midnight"),
    ("hai giờ rưỡi", "half past two"),
    ("ba giờ kém mười lăm", "quarter to three"),
]
