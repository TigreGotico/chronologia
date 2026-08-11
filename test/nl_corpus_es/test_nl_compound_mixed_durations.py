# -*- coding: utf-8 -*-
"""Mixed-grain duration/offset compounds in Spanish -- mirrors
``test/nl_corpus_en/test_nl_compound_mixed_durations.py``: a calendar-grain
unit (mes/año) chained by "y" to a fixed-grain unit (dia/hora) must compose
into ONE point for ``extract_timespan``, and ``extract_duration`` must refuse
the whole mixed compound rather than strand the calendar part.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from chronologia.extract import extract_duration
from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, start_end

LANG = "es"


def _point(anchor=ANCHOR, **delta):
    dt = anchor + relativedelta(**delta)
    return AstroDate(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                     dt.second, dt.microsecond)


def test_month_day_compound_composes():
    start, end = start_end("en 3 meses y 2 dias")
    exp_start = _point(months=3, days=2)
    assert start == exp_start
    assert end == exp_start + timedelta(days=1)


def test_year_day_compound_composes():
    start, end = start_end("en un año y un dia")
    exp_start = _point(years=1, days=1)
    assert start == exp_start
    assert end == exp_start + timedelta(days=1)


@pytest.mark.parametrize("text", [
    "3 meses y 2 dias",
    "3 años y 2 meses",
])
def test_mixed_calendar_fixed_duration_refuses(text):
    assert extract_duration(text, LANG) is None


def test_pure_fixed_grain_duration_compound_unaffected():
    got = extract_duration("3 dias y 2 horas", LANG)
    assert got == (timedelta(days=3, hours=2), "")
