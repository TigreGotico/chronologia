"""Apostrophe two-digit years resolve via an anchor-relative sliding window.

"the summer of '42" is 1942, not 2042; "the summer of '20" is 2020, not the
anchor year with a stranded "'20"; "the spring of '08" is 2008.  A bare
two-digit year is inherently ambiguous, so it resolves into the 100-year span
``[anchor_year - 80, anchor_year + 19]`` -- the anchor-relative window
:mod:`email.utils` and ``dateutil`` use.  Exactly one of ``19YY`` / ``20YY``
lands inside that window, and that one wins, so the reading tracks the anchor
and ages correctly.

Regression guard for the silent-wrong where a fixed ``%y`` pivot (00-68 ->
20YY, 69-99 -> 19YY) mis-centuried recent years ("'42" -> 2042) AND the year
matcher's >=32 threshold silently DROPPED apostrophe years below 32 ("'20"
returned the anchor year with "of '20" stranded in the remainder).

Anchor 2017-06-27 (Tue, 13:04): the window is 1937..2036.
"""
from datetime import datetime

import pytest

from ._corpus import parse, start, start_end, ANCHOR


def _window(yy, anchor_year):
    """Independent reference: the year a two-digit YY resolves to under the
    anchor-relative window, computed WITHOUT touching the parser."""
    candidate = 2000 + yy
    if anchor_year - 80 <= candidate <= anchor_year + 19:
        return candidate
    return 1900 + yy


# -- the full YY sweep, "the summer of 'YY" -> the windowed year -----------

@pytest.mark.parametrize("yy", [1, 5, 8, 17, 20, 25, 30, 37,
                                42, 45, 63, 69, 85, 95, 99])
def test_summer_of_two_digit_year_uses_window(yy):
    text = f"the summer of '{yy:02d}"
    expected = _window(yy, ANCHOR.year)
    r = parse(text)
    assert r is not None, f"{text!r} did not parse (year was dropped)"
    span, remainder = r
    assert span.start.year == expected, (
        f"{text!r} -> {span.start.year}, want {expected}")
    # the apostrophe year must be CONSUMED, never stranded in the remainder
    assert f"{yy:02d}" not in remainder, (
        f"{text!r} stranded the year in remainder {remainder!r}")


# -- the exact window values for anchor 2017 (window 1937..2036) -----------

@pytest.mark.parametrize("text,year", [
    ("the summer of '42", 1942),   # 2042 outside window -> 1942
    ("the summer of '45", 1945),
    ("the summer of '20", 2020),   # was dropped
    ("the summer of '25", 2025),
    ("the spring of '08", 2008),   # was dropped + stranded
    ("the summer of '05", 2005),
    ("the summer of '17", 2017),
    ("the summer of '69", 1969),
    ("the summer of '95", 1995),
    ("the summer of '30", 2030),   # 2030 inside window
    ("the summer of '37", 1937),   # 2037 outside window (>2036) -> 1937
])
def test_window_pivot_exact_values(text, year):
    assert start(text).year == year


# -- bare "in 'YY" / "'YY" standalone year forms --------------------------

@pytest.mark.parametrize("text,year", [
    ("'99", 1999),
    ("in '05", 2005),
    ("back in '85", 1985),
    ("born in '63", 1963),
    ("the winter of '45", 1945),
])
def test_bare_apostrophe_year(text, year):
    assert start(text).year == year


# -- decades keep resolving (same window on the decade base) ---------------

@pytest.mark.parametrize("text,decade_start", [
    ("the '90s", 1990),
    ("the '80s", 1980),
])
def test_apostrophe_decade(text, decade_start):
    s, e = start_end(text)
    assert s.year == decade_start
    assert e.year == decade_start + 10


# -- the window is ANCHOR-RELATIVE, not a fixed pivot ----------------------

def test_window_is_anchor_relative():
    """The same surface resolves to a different century under a different
    anchor, proving the pivot tracks the anchor rather than a fixed cut.
    "'90": anchor 2017 (window 1937..2036) -> 1990, since 2090 is outside;
    anchor 2080 (window 2000..2099) -> 2090, since 2090 is now inside."""
    assert start("the summer of '90", ANCHOR).year == 1990
    far = datetime(2080, 6, 27, 13, 4)
    assert start("the summer of '90", far).year == 2090


# -- 4-digit years are byte-identical (no window applied) ------------------

@pytest.mark.parametrize("text,year", [
    ("the summer of 1942", 1942),
    ("in 2020", 2020),
    ("the summer of 500", 500),
    ("in 1985", 1985),
    ("in 2005", 2005),
])
def test_four_digit_years_unchanged(text, year):
    assert start(text).year == year


# -- an apostrophe possessive / o'clock is NOT read as a year --------------

def test_apostrophe_not_a_year_false_positive():
    # "summer's end" -- the 's is possessive, no digit follows
    assert parse("summer's end") is None
    # "o'clock" carries no two-digit-year reading: "at 3 o'clock" reads as the
    # 3 o'clock TIME (o'clock consumed as the clock marker, never as a spurious
    # '<year>), so the result -- if any -- is an hour-3 clock span, not a year.
    r = parse("at 3 o'clock")
    assert r is None or (r[0].start.hour == 3
                         and "clock" not in r[1] and "'" not in r[1])
