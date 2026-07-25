# -*- coding: utf-8 -*-
"""Scoped-ordinal "Nth <weekday> of <month>" for an: binds ORD+WEEKDAY+of/
MONTH into the nth-weekday-of-the-named-month span (anchor Tue 2017-06-27).
Expected dates from parser-independent calendar arithmetic."""

from ._corpus import parse, start, ad
from datetime import datetime


def test_o_segundo_luns_de_marzo():
    phrase = 'o segundo luns de marzo'
    assert start(phrase) == ad(datetime(2018, 3, 12))
    assert parse(phrase)[1] == ""

