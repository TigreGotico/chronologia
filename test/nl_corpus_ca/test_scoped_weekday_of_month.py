# -*- coding: utf-8 -*-
"""Scoped-ordinal "Nth <weekday> of <month>" for ca: binds ORD+WEEKDAY+of/
MONTH into the nth-weekday-of-the-named-month span (anchor Tue 2017-06-27).
Expected dates from parser-independent calendar arithmetic."""

from ._corpus import parse, start, ad
from datetime import datetime


def test_el_segon_dilluns_de_marc():
    phrase = 'el segon dilluns de març'
    assert start(phrase) == ad(datetime(2017, 3, 13))
    assert parse(phrase)[1] == ""


def test_lultim_dilluns_de_marc():
    phrase = "l'últim dilluns de març"
    assert start(phrase) == ad(datetime(2017, 3, 27))
    assert parse(phrase)[1] == ""

