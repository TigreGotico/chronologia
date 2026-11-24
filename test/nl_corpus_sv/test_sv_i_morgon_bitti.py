# -*- coding: utf-8 -*-
"""sv "i morgon bitti" and "till i morgon" (tomorrow).

"bitti" is "early in the day" and is used only in "i morgon bitti" (early
tomorrow, tomorrow morning; Wiktionary, sv "bitti"), so it names the morning
band [05:00, 10:00) of tomorrow (CLDR 47 day periods, locale sv).  "till i
morgon" after other words names tomorrow, as "till imorgon" does: the last
word of the day name "i morgon" is not a meridiem to lend to the words before
it.  Anchor: Tuesday 2017-06-27 13:04, so tomorrow is 2017-06-28.
"""
import pytest

from ._corpus import AstroDate, parse, start_end

TOMORROW_MORNING = (AstroDate(2017, 6, 28, 5), AstroDate(2017, 6, 28, 10))
TOMORROW = (AstroDate(2017, 6, 28), AstroDate(2017, 6, 29))
YESTERDAY_MORNING = (AstroDate(2017, 6, 26, 5), AstroDate(2017, 6, 26, 10))


@pytest.mark.parametrize("text,expected,remainder", [
    ("väck mig i morgon bitti", TOMORROW_MORNING, "väck mig"),
    ("i morgon bitti", TOMORROW_MORNING, ""),
    ("i går bitti", YESTERDAY_MORNING, ""),
])
def test_bitti_is_the_morning_band(text, expected, remainder):
    assert start_end(text) == expected
    assert parse(text).remainder == remainder


@pytest.mark.parametrize("text", [
    "vilka larm har jag till i morgon",
    "vi ses till i morgon",
    "larm till i morgon",
])
def test_till_i_morgon_after_words_is_tomorrow(text):
    assert start_end(text) == TOMORROW
