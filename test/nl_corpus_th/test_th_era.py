# -*- coding: utf-8 -*-
"""The Buddhist Era: BE = CE + 543, read from the marker and never guessed."""
import pytest

from ._corpus import day, parse, start, start_end


@pytest.mark.parametrize("be,ce", [(2568, 2025), (2569, 2026), (2540, 1997),
                                   (2500, 1957), (2600, 2057)])
def test_a_marked_year_converts_through_the_era_registry(be, ce):
    assert start(f"พ.ศ. {be}").year == ce


def test_a_marked_year_composes_with_a_full_date():
    """CLDR's long pattern for th is d MMMM G y, with the era between the
    month and the year, and the whole line reads as one date."""
    assert start_end("15 มกราคม พ.ศ. 2569") == day(2026, 1, 15)


def test_the_common_era_marker_takes_the_year_as_written():
    assert start_end("วันที่ 15 มกราคม ค.ศ. 2026") == day(2026, 1, 15)


def test_the_marker_leaves_no_remainder():
    r = parse("พ.ศ. 2568")
    assert r is not None and r[1] == ""


@pytest.mark.parametrize("be", [2568, 2569, 2600])
def test_the_offset_is_exactly_five_hundred_and_forty_three(be):
    """Computed against the arithmetic, not read back from the parser."""
    assert start(f"พ.ศ. {be}").year == be - 543


def test_an_unmarked_year_is_common_era():
    """The documented locale policy: a bare four-digit year is Common Era.
    Reading it as Buddhist would silently move every foreign date quoted in a
    Thai text by 543 years, and nothing in the digits says which era is meant.
    """
    assert start("2026").year == 2026
    assert start("2568").year == 2568
