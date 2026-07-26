"""Finnish "N.-M. <month>" tight-dash day-range shorthand.

Finnish writes a day range as "3.-10. heinaekuuta" (3rd-10th of July). The
tight dash between the two ordinal day numerals was refused, so it collapsed
onto the 10th and stranded "3.". A tight dash between two plain numerals is
now read as a range -- but only composes when one side can lend the other a
month, so a bare "12-15" is still no range.
"""
from ._corpus import parse, AstroDate


def _span_rem(text):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    return (r[0].start, r[0].end), r[1]


def test_dash_day_range():
    (s, e), rem = _span_rem("3.-10. heinäkuuta")
    assert (s, e) == (AstroDate(2017, 7, 3), AstroDate(2017, 7, 11))
    assert rem == ""


def test_dash_day_range_other_month():
    (s, e), rem = _span_rem("5.-12. elokuuta")
    assert (s, e) == (AstroDate(2017, 8, 5), AstroDate(2017, 8, 13))
    assert rem == ""


def test_bare_number_dash_is_not_a_range():
    assert parse("12-15") is None
