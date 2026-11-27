# -*- coding: utf-8 -*-
"""Month-thirds "principios / finais de <month>" for Galician.

A month splits into three fuzzy thirds; the extremes have parser-independent
anchors regardless of the month's length: "principios de <month>" always opens
on the first of the month, and "finais de <month>" always closes on the first
of the following month.  Those two boundaries are what we pin here -- the exact
inner cut of each third depends on the month length and is deliberately left to
the daypart/fuzzy files.  Anchor Tue 2017-06-27.  A bare month takes the year the month alone
takes (ruling 1, changed on 26 November 2026: it used to be the anchor year for every
month); a month that ended before the anchor, xaneiro to maio, is 2018, and so is the first
third of xuño, which ended before the anchor."""
from datetime import datetime

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, parse, span, ad

_MONTHS = [("xaneiro", 1), ("febreiro", 2), ("marzo", 3), ("abril", 4),
           ("maio", 5), ("xuño", 6), ("xullo", 7), ("agosto", 8),
           ("setembro", 9), ("outubro", 10), ("novembro", 11), ("decembro", 12)]


@pytest.mark.parametrize("monw,mon", _MONTHS)
def test_principios_opens_on_the_first(monw, mon):
    phrase = f"principios de {monw}"
    year = ANCHOR.year + (mon < ANCHOR.month)
    if mon == ANCHOR.month:
        # ruling 1 (26 November 2026): a part of a month is read as a span;
        # the first third of June 2017 ended on the 11th, before the anchor,
        # so "principios de xuño" is early June 2018
        year += 1
    assert span(phrase).start == ad(datetime(year, mon, 1))
    assert parse(phrase)[1] == ""


@pytest.mark.parametrize("monw,mon", _MONTHS)
def test_finais_closes_on_the_first_of_next_month(monw, mon):
    phrase = f"finais de {monw}"
    end = datetime(ANCHOR.year + (mon < ANCHOR.month), mon, 1) + relativedelta(months=1)
    assert span(phrase).end == ad(end)
    assert parse(phrase)[1] == ""
