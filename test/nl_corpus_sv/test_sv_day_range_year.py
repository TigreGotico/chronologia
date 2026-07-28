# -*- coding: utf-8 -*-
"""Intra-month day range with a trailing year (sv): "5-12 juni 2020".

The month and the year are named once for the pair of days; both endpoints
must read them.  The year used to bind only to the right day and the left "5"
leaked into the residue (span collapsed onto the 12th).  The shared month and
year are now lent to both days.
"""
from ._corpus import AstroDate, start_end, parse


def test_day_range_shares_month_and_year():
    ss, ee = start_end("5-12 juni 2020")
    assert ss == AstroDate(2020, 6, 5)
    assert ee == AstroDate(2020, 6, 13)
    assert parse("5-12 juni 2020")[1] == ""


def test_bare_day_range_no_year_unchanged():
    # regression pin: the no-year form keeps its prefer-future reading
    ss, ee = start_end("5-12 juni")
    assert ss == AstroDate(2018, 6, 5) and ee == AstroDate(2018, 6, 13)
