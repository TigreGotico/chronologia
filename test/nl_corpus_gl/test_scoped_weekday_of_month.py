# -*- coding: utf-8 -*-
"""Scoped-ordinal "Nth <weekday> of <month>" for gl: binds ORD+WEEKDAY+of/
MONTH into the nth-weekday-of-the-named-month span (anchor Tue 2017-06-27).
Expected dates from parser-independent calendar arithmetic."""

from ._corpus import parse, start, ad
from datetime import datetime


def test_o_segundo_luns_de_marzo():
    phrase = 'o segundo luns de marzo'
    # ruling 1 (26 November 2026): a part of a month takes its month's year;
    # March has ended at the anchor (June 2017), so it is March 2018
    assert start(phrase) == ad(datetime(2018, 3, 12))
    assert parse(phrase)[1] == ""


def test_o_ultimo_luns_de_marzo():
    phrase = 'o último luns de marzo'
    # ruling 1 (26 November 2026): a part of a month takes its month's year;
    # March has ended at the anchor (June 2017), so it is March 2018
    assert start(phrase) == ad(datetime(2018, 3, 26))
    assert parse(phrase)[1] == ""

