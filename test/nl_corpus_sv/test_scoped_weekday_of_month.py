# -*- coding: utf-8 -*-
"""Scoped-ordinal "Nth <weekday> of <month>" for sv: binds ORD+WEEKDAY+of/
MONTH into the nth-weekday-of-the-named-month span (anchor Tue 2017-06-27).
Expected dates from parser-independent calendar arithmetic.
Ruling 1 (changed on 26 November 2026): a part of a month takes its month's
year; mars has ended at the anchor, so it is March 2018 (Mondays 5, 12, 19,
26)."""

from ._corpus import parse, start, ad
from datetime import datetime


def test_andra_mandagen_i_mars():
    phrase = 'andra måndagen i mars'
    assert start(phrase) == ad(datetime(2018, 3, 12))
    assert parse(phrase)[1] == ""

