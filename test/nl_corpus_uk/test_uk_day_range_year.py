# -*- coding: utf-8 -*-
"""Intra-month day range with a trailing year (uk): "з 5 по 12 серпня 2019".

The month and year are named once for the pair of days; both endpoints must
read them.  The year used to detach and "5 по" leaked into the residue.  The
shared month and year are now lent to both days.
"""
from ._corpus import AstroDate, start_end, parse


def test_day_range_shares_month_and_year():
    ss, ee = start_end("з 5 по 12 серпня 2019")
    assert ss == AstroDate(2019, 8, 5)
    assert ee == AstroDate(2019, 8, 13)
    assert parse("з 5 по 12 серпня 2019")[1] == ""
