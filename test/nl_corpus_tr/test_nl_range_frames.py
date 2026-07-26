"""Turkish "X-Y <month>" tight-dash day-range shorthand.

Turkish writes a day range as "3-10 Temmuz" (3rd-10th of July). The tight dash
between two plain day numerals was refused (only year-year tight dashes were
trusted), so it collapsed onto the 10th and stranded "3". A tight dash between
two plain numerals is now read as a range -- but only composes when one side
can lend the other a month, so a bare "12-15" is still no range.
"""
from ._corpus import parse, AstroDate


def _span_rem(text):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    return (r[0].start, r[0].end), r[1]


def test_dash_day_range():
    # anchor is 2026-07-15; a past July flings forward one year (prefer_future)
    (s, e), rem = _span_rem("3-10 Temmuz")
    assert (s, e) == (AstroDate(2027, 7, 3), AstroDate(2027, 7, 11))
    assert rem == ""


def test_dash_day_range_future_month():
    (s, e), rem = _span_rem("15-20 Ağustos")
    assert (s, e) == (AstroDate(2026, 8, 15), AstroDate(2026, 8, 21))
    assert rem == ""


def test_bare_number_dash_is_not_a_range():
    # no month to share -> not a date range, must not be fabricated
    assert parse("12-15") is None
