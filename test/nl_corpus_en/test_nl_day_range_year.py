"""Intra-month day range with a trailing year: the month AND the year are
named once for the pair of days, and both endpoints must read them.

"5-12 June 2020" is the day-range analogue of the shared-month range
("June 5 to 12", #236) and the month-range year-lending ("from January to
March 2020", #323): the trailing "June 2020" belongs to *both* the 5th and
the 12th.  It used to bind only to the right endpoint -- the left day was
dropped into the remainder and the range collapsed onto the 12th (or ran to
the anchor instant).  The shared month and year are now lent to both days.
"""
import pytest

from ._corpus import AstroDate, start_end, parse


def _residue(text):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    return r[1]


# -- the intra-month "D1[-/to] D2 <month> <year>" range: month+year named once
@pytest.mark.parametrize("text", [
    "5 to 12 June 2020",
    "5-12 June 2020",
    "from 5 to 12 June 2020",
])
def test_day_range_shares_month_and_year(text):
    ss, ee = start_end(text)
    assert ss == AstroDate(2020, 6, 5), f"{text!r} start"
    assert ee == AstroDate(2020, 6, 13), f"{text!r} end"
    assert _residue(text) == "", f"{text!r} left a residue"


# the determiner ("the 5th ... the 12th of June 2020") form now reads the same
# span; its "the" residue is byte-identical to the no-year determiner range
# ("from the 5th to the 12th of June"), an established artefact of that surface,
# so the fix is verified against that baseline rather than an empty residue.
def test_determiner_day_range_matches_no_year_residue():
    ss, ee = start_end("from the 5th to the 12th of June 2020")
    assert ss == AstroDate(2020, 6, 5) and ee == AstroDate(2020, 6, 13)
    assert _residue("from the 5th to the 12th of June 2020") \
        == _residue("from the 5th to the 12th of June")


# -- regression pins: the byte-identical readings that must NOT change -------

# the bare day range with no year still reads in the prefer-future year (#236)
def test_bare_day_range_no_year_unchanged():
    ss, ee = start_end("June 5 to 12")
    assert ss == AstroDate(2018, 6, 5) and ee == AstroDate(2018, 6, 13)


# the month-range year-lending (#323) is untouched
def test_month_range_year_lend_unchanged():
    ss, ee = start_end("from January to March 2020")
    assert ss == AstroDate(2020, 1, 1) and ee == AstroDate(2020, 4, 1)


# a cross-month range where each endpoint names its own month: the trailing
# year is lent, the months are NOT shared
def test_cross_month_range_with_trailing_year():
    ss, ee = start_end("from June 5 to July 12 2020")
    assert ss == AstroDate(2020, 6, 5) and ee == AstroDate(2020, 7, 13)


# each endpoint carrying its own year stays per-endpoint
def test_each_endpoint_its_own_year_unchanged():
    ss, ee = start_end("from June 5 2019 to June 12 2020")
    assert ss == AstroDate(2019, 6, 5) and ee == AstroDate(2020, 6, 13)
