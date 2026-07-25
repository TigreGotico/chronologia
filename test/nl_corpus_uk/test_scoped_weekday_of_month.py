# -*- coding: utf-8 -*-
"""Scoped-ordinal "Nth <weekday> of <month>" for uk: binds ORD+WEEKDAY+of/
MONTH into the nth-weekday-of-the-named-month span (anchor Tue 2017-06-27).
Expected dates from parser-independent calendar arithmetic."""

from ._corpus import parse, start, ad
from datetime import datetime


def test_другий_понеділок_березня():
    phrase = 'другий понеділок березня'
    assert start(phrase) == ad(datetime(2017, 3, 13))
    assert parse(phrase)[1] == ""

