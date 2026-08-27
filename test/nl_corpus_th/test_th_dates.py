# -*- coding: utf-8 -*-
"""Calendar dates: day before month before year, with วันที่ introducing the day."""
import pytest

from ._corpus import day, parse, start_end

MONTHS = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
          "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
ABBREVIATIONS = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
                 "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]


@pytest.mark.parametrize("n,name", list(enumerate(MONTHS, start=1)))
def test_every_month_name_reads(n, name):
    assert start_end(f"20 {name} 2026") == day(2026, n, 20)


@pytest.mark.parametrize("n,abbr", list(enumerate(ABBREVIATIONS, start=1)))
def test_every_month_abbreviation_reads(n, abbr):
    """The abbreviations are dot-internal and dot-final; a tokenizer that read
    the dot as a sentence boundary would split every one of them."""
    assert start_end(f"20 {abbr} 2026") == day(2026, n, 20)


def test_the_day_noun_introduces_the_day_of_the_month():
    assert start_end("วันที่ 15 มกราคม 2026") == day(2026, 1, 15)


def test_the_day_noun_is_optional():
    assert start_end("15 มกราคม 2026") == day(2026, 1, 15)


def test_a_month_alone_spans_the_month():
    assert start_end("มกราคม 2026") == (day(2026, 1, 1)[0], day(2026, 2, 1)[0])


def test_a_date_line_leaves_no_remainder():
    r = parse("วันที่ 15 มกราคม 2026")
    assert r is not None and r[1] == ""


def test_the_may_month_and_the_buddhist_era_marker_are_kept_apart():
    """พ.ค. (May) and พ.ศ. (Buddhist Era) differ by one letter and both sit
    next to a number."""
    assert start_end("20 พ.ค. 2026") == day(2026, 5, 20)
    from ._corpus import start
    assert start("พ.ศ. 2026").year == 2026 - 543


def test_an_iso_literal_still_reads():
    assert start_end("2026-01-15") == day(2026, 1, 15)
