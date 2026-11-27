# -*- coding: utf-8 -*-
"""Scoped-ordinal "Nth <weekday> of <month>" for he: binds ORD+WEEKDAY+of/
MONTH into the nth-weekday-of-the-named-month span (anchor Tue 2017-06-27).
Expected dates from parser-independent calendar arithmetic.  With no year the month
takes the year the month alone takes (ruling 1, changed 26 November 2026): March has
ended at the anchor, so it is March 2018 and the 2nd Monday is the 12th."""

from ._corpus import parse, start, ad
from datetime import datetime


def test_יום_שני_שני_של_מרץ():
    phrase = 'יום שני שני של מרץ'
    assert start(phrase) == ad(datetime(2018, 3, 12))  # ruling 1: March 2018, 2nd Monday
    assert parse(phrase)[1] == ""

