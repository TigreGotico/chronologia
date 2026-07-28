# -*- coding: utf-8 -*-
"""Month-thirds "principios / finais de <month>" for Galician.

A month splits into three fuzzy thirds; the extremes have parser-independent
anchors regardless of the month's length: "principios de <month>" always opens
on the first of the month, and "finais de <month>" always closes on the first
of the following month.  Those two boundaries are what we pin here -- the exact
inner cut of each third depends on the month length and is deliberately left to
the daypart/fuzzy files.  Anchor Tue 2017-06-27 (bare month => anchor year)."""
from datetime import datetime

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import parse, span, ad

_MONTHS = [("xaneiro", 1), ("febreiro", 2), ("marzo", 3), ("abril", 4),
           ("maio", 5), ("xuño", 6), ("xullo", 7), ("agosto", 8),
           ("setembro", 9), ("outubro", 10), ("novembro", 11), ("decembro", 12)]


@pytest.mark.parametrize("monw,mon", _MONTHS)
def test_principios_opens_on_the_first(monw, mon):
    phrase = f"principios de {monw}"
    assert span(phrase).start == ad(datetime(2017, mon, 1))
    assert parse(phrase)[1] == ""


@pytest.mark.parametrize("monw,mon", _MONTHS)
def test_finais_closes_on_the_first_of_next_month(monw, mon):
    phrase = f"finais de {monw}"
    end = datetime(2017, mon, 1) + relativedelta(months=1)
    assert span(phrase).end == ad(end)
    assert parse(phrase)[1] == ""
