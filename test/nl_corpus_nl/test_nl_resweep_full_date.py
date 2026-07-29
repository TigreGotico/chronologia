# -*- coding: utf-8 -*-
"""Second-pass resweep: full calendar-date and bare month+year (nl), fresh years.

"<dag> <maand> <jaar>" and bare "<maand> <jaar>", same shape as
:mod:`test_nl_full_date_sweep` (years 2019-2021) and the ``test_month_year``
cases in :mod:`test_nl_calendar` (only four hand-picked years), but over
fresh years 2029-2033 with every month. Days sampled per month plus that
month's true last day, so February 28/29 and 30/31-day month ends are all
exercised. Gold is a literal date; the span is the single named day
[D, D+1), or the whole month for the bare form.

Anchor 2017-06-27.
"""
import calendar
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, parse, span

_MONTHS = [
    "januari", "februari", "maart", "april", "mei", "juni",
    "juli", "augustus", "september", "oktober", "november", "december",
]
_YEARS = [2029, 2030, 2031, 2032, 2033]
_SAMPLE_DAYS = [2, 9, 16, 23]


def _build_full_dates():
    cases = []
    for y in _YEARS:
        for mi, mname in enumerate(_MONTHS, start=1):
            last = calendar.monthrange(y, mi)[1]
            days = sorted(set(d for d in _SAMPLE_DAYS if d <= last) | {last})
            for d in days:
                cases.append((f"{d} {mname} {y}", date(y, mi, d)))
    return cases


def _build_month_years():
    cases = []
    for y in _YEARS:
        for mi, mname in enumerate(_MONTHS, start=1):
            cases.append((f"{mname} {y}", y, mi))
    return cases


_DATE_CASES = _build_full_dates()
_MY_CASES = _build_month_years()


@pytest.mark.parametrize("phrase,gold", _DATE_CASES, ids=[c[0] for c in _DATE_CASES])
def test_full_date_resweep(phrase, gold):
    s = span(phrase)
    assert s.start == AstroDate(gold.year, gold.month, gold.day), phrase
    nxt = gold + timedelta(days=1)
    assert s.end == AstroDate(nxt.year, nxt.month, nxt.day), phrase
    assert parse(phrase)[1] == "", phrase


@pytest.mark.parametrize("phrase,y,mi", _MY_CASES, ids=[c[0] for c in _MY_CASES])
def test_month_year_resweep(phrase, y, mi):
    s = span(phrase)
    assert s.start == AstroDate(y, mi, 1), phrase
    end_y, end_m = (y + 1, 1) if mi == 12 else (y, mi + 1)
    assert (s.end.year, s.end.month) == (end_y, end_m), phrase
