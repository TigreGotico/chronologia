"""Mixed-grain duration/offset compounds in German -- mirrors
``test/nl_corpus_en/test_nl_compound_mixed_durations.py``: a calendar-grain
unit (Monat/Jahr) chained by "und" to a fixed-grain unit (Tag/Stunde) must
compose into ONE point for ``extract_timespan``, and ``extract_duration``
must refuse the whole mixed compound rather than strand the calendar part.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from chronologia.extract import extract_duration
from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, start_end

LANG = "de"


def _point(anchor=ANCHOR, **delta):
    dt = anchor + relativedelta(**delta)
    return AstroDate(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                     dt.second, dt.microsecond)


def test_month_day_compound_composes():
    start, end = start_end("in 3 Monaten und 2 Tagen")
    exp_start = _point(months=3, days=2)
    assert start == exp_start
    assert end == exp_start + timedelta(days=1)


def test_year_day_compound_composes():
    start, end = start_end("in einem Jahr und einem Tag")
    exp_start = _point(years=1, days=1)
    assert start == exp_start
    assert end == exp_start + timedelta(days=1)


@pytest.mark.parametrize("text", [
    "3 Monaten und 2 Tagen",
    "3 Jahren und 2 Monaten",
])
def test_mixed_calendar_fixed_duration_refuses(text):
    assert extract_duration(text, LANG) is None


def test_pure_fixed_grain_duration_compound_unaffected():
    got = extract_duration("3 Tagen und 2 Stunden", LANG)
    assert got == (timedelta(days=3, hours=2), "")
