# -*- coding: utf-8 -*-
"""An hour followed by العصر or الظهر is a pm hour, and "الساعة <hour>" alone is
a clock.

Wiktionary عصر: "late afternoon"; ظهر (ظُهْر): "noon, midday" and
"afternoon, p.m." (after Wehr, A Dictionary of Modern Written Arabic).  Ruling
27 lets a locale's own pm word beside a clock decide the half, and ruling 17
gives a lone hour its next twelve-hour reading.  Gold values are hand
arithmetic on the anchors: Tuesday 2017-06-27 08:00 and 15:00.
"""
import pytest

from ._corpus import AstroDate, datetime, parse, start_end

EARLY = datetime(2017, 6, 27, 8, 0)
LATE = datetime(2017, 6, 27, 15, 0)


def _at(day, hour):
    return AstroDate(2017, 6, day, hour, 0), AstroDate(2017, 6, day, hour, 1)


@pytest.mark.parametrize("text,gold", [
    ("الساعة 4 العصر", _at(27, 16)),
    ("الساعة 5 العصر", _at(27, 17)),
    ("الساعة 2 الظهر", _at(27, 14)),
    ("الساعة 1 الظهر", _at(27, 13)),
    ("الساعة 12 الظهر", _at(27, 12)),
    ("الساعة 4 عصرا", _at(27, 16)),
    ("الساعة 2 ظهرا", _at(27, 14)),
    ("الساعة 4 مساء", _at(27, 16)),
])
def test_an_hour_before_a_pm_word_is_the_pm_hour(text, gold):
    assert start_end(text, EARLY) == gold
    assert parse(text, EARLY).remainder == ""


def test_the_definite_and_the_accusative_form_read_alike():
    for hour in range(1, 12):
        assert (start_end(f"الساعة {hour} العصر", EARLY)
                == start_end(f"الساعة {hour} عصرا", EARLY))
        assert (start_end(f"الساعة {hour} الظهر", EARLY)
                == start_end(f"الساعة {hour} ظهرا", EARLY))


def test_a_half_hour_clock_before_alasr_is_pm():
    assert start_end("الساعة 2:30 العصر", EARLY) == (
        AstroDate(2017, 6, 27, 14, 30), AstroDate(2017, 6, 27, 14, 31))
    assert parse("الساعة 2:30 العصر", EARLY).remainder == ""


def test_a_day_word_leaves_the_pm_hour_with_the_day():
    text = "غدا الساعة 4 العصر"
    assert start_end(text, EARLY) == _at(28, 16)
    assert parse(text, EARLY).remainder == ""


def test_alzuhr_alone_is_still_noon():
    assert start_end("الظهر", EARLY) == _at(27, 12)


@pytest.mark.parametrize("text", ["العصر الحديث", "في العصر", "العصر"])
def test_alasr_with_no_hour_names_no_time(text):
    assert parse(text, EARLY) is None


@pytest.mark.parametrize("anchor,text,gold", [
    (EARLY, "الساعة 2", _at(27, 14)),
    (EARLY, "الساعة 9", _at(27, 9)),
    (LATE, "الساعة 2", _at(28, 2)),
    (EARLY, "الساعة 14", _at(27, 14)),
])
def test_the_hour_word_makes_a_lone_hour_a_clock(anchor, text, gold):
    assert start_end(text, anchor) == gold
    assert parse(text, anchor).remainder == ""


@pytest.mark.parametrize("text", ["2", "14", "في 3"])
def test_a_number_with_no_hour_word_is_not_a_clock(text):
    assert parse(text, EARLY) is None
