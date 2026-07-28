# -*- coding: utf-8 -*-
"""Intra-month day range with a trailing year (cs): "od 5. do 12. června 2020".

The month and year are named once for the pair of days; both endpoints must
read them.  The shared month and year are now lent to both days.
"""
from ._corpus import AstroDate, start_end, parse


def test_day_range_shares_month_and_year():
    ss, ee = start_end("od 5. do 12. června 2020")
    assert ss == AstroDate(2020, 6, 5)
    assert ee == AstroDate(2020, 6, 13)
    assert parse("od 5. do 12. června 2020")[1] == ""


def test_dash_day_range_shares_month_and_year():
    ss, ee = start_end("5.-12. června 2020")
    assert ss == AstroDate(2020, 6, 5)
    assert ee == AstroDate(2020, 6, 13)
