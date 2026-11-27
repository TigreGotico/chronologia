# -*- coding: utf-8 -*-
"""Scoped-ordinal "Nth <weekday> of <month>" for it: binds ORD+WEEKDAY+of/
MONTH into the nth-weekday-of-the-named-month span (anchor Tue 2017-06-27).
Expected dates from parser-independent calendar arithmetic.
Ruling 1 (changed on 26 November 2026): a part of a month takes its month's
year; marzo has ended at the anchor, so it is March 2018 (Mondays 5, 12, 19,
26)."""

from ._corpus import parse, start, ad
from datetime import datetime


def test_il_secondo_lunedi_di_marzo():
    phrase = 'il secondo lunedì di marzo'
    assert start(phrase) == ad(datetime(2018, 3, 12))
    assert parse(phrase)[1] == ""


def test_lultimo_lunedi_di_marzo():
    phrase = "l'ultimo lunedì di marzo"
    assert start(phrase) == ad(datetime(2018, 3, 26))
    assert parse(phrase)[1] == ""

