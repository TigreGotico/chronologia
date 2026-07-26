# -*- coding: utf-8 -*-
"""Arabic الأول/الثاني: ordinal vs Levantine month-name (Rule A, confirmed by
native speaker athmanemokraoui, TigreGotico/chronologia#268). Anchor Tue
2017-06-27."""
from datetime import datetime
import pytest
from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)


def _span(t):
    r = extract_timespan(t, "ar", ANCHOR)
    assert r is not None and r[0] is not None, f"{t!r} did not parse"
    return r


@pytest.mark.parametrize("text,start,days", [
    ("النصف الأول من 2020", "2020-01-01", 182),   # first half
    ("النصف الثاني من 2020", "2020-07-01", 184),   # second half
    ("الربع الأول من 2020", "2020-01-01", 91),     # first quarter
])
def test_half_quarter_read_ordinal(text, start, days):
    sp, rem = _span(text)
    assert sp.start_datetime.date().isoformat() == start
    assert (sp.end_datetime - sp.start_datetime).days == days
    assert rem == ""


@pytest.mark.parametrize("text,start", [
    ("تشرين الأول", "2017-10-01"),   # October (NOT "the first")
    ("كانون الثاني", "2017-01-01"),  # January (NOT "the second")
])
def test_month_names_preserved(text, start):
    sp, _ = _span(text)
    assert sp.start_datetime.date().isoformat() == start
    assert (sp.end_datetime - sp.start_datetime).days in (28, 29, 30, 31)
