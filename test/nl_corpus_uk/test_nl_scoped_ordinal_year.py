# -*- coding: utf-8 -*-
"""An explicit trailing year on the Nth-weekday-of-month construction must bind
in the Slavic connector-less genitive surface ("третій понеділок березня
2019") -- the year may never be silently dropped in favour of the anchor year.

uk already binds the bare genitive year; this pins that reading against the
shared scoped_ordinal fix so the Slavic surface stays byte-identical while the
Romance "de <year>" connector form gains the same binding.  The no-year reading
is pinned to prove the fix stays positional.
"""
from ._corpus import AstroDate, parse, start_end


def test_scoped_ordinal_binds_trailing_genitive_year():
    # 3rd Monday of March 2019 = 2019-03-18 (Mondays: 4, 11, 18).
    assert start_end('третій понеділок березня 2019') == (
        AstroDate(2019, 3, 18), AstroDate(2019, 3, 19))
    assert parse('третій понеділок березня 2019')[1] == ''


def test_scoped_ordinal_no_year_is_next_occurrence():
    # ruling 1 (changed 26 November 2026): with no year the month takes the year the
    # month alone takes; March has ended at the anchor (2017-06-27), so it is March
    # 2018 and its 3rd Monday is the 19th (it was the 20th of March 2017).
    assert start_end('третій понеділок березня') == (
        AstroDate(2018, 3, 19), AstroDate(2018, 3, 20))
