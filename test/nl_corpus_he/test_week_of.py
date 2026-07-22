# -*- coding: utf-8 -*-
"""The "week of <date>" construction for he: widen a date to its week.

Week starts on Sunday here, so the expected week is derived with that offset,
independently of the parser.
"""
from datetime import date, datetime, timedelta

import pytest

from ._corpus import AstroDate, nomatch, parse, span, start_end

_WKSTART = 6  # Mon=0 .. Sun=6


def _week(y, m, d):
    day = date(y, m, d)
    back = (day.weekday() - _WKSTART) % 7
    ws = day - timedelta(days=back)
    start = AstroDate(ws.year, ws.month, ws.day)
    end_dt = datetime(ws.year, ws.month, ws.day) + timedelta(days=7)
    return start, AstroDate(end_dt.year, end_dt.month, end_dt.day)


@pytest.mark.parametrize("text,ymd", [
    ('השבוע של 20 ביולי 2026', (2026, 7, 20)),
    ('השבוע של 15 בינואר 2026', (2026, 1, 15)),
    ('השבוע של 10 בדצמבר 2026', (2026, 12, 10)),
    ('השבוע של 5 במרץ 2026', (2026, 3, 5)),
    ('השבוע של 4 ביולי 2026', (2026, 7, 4)),
    ('השבוע של 11 במרץ 2026', (2026, 3, 11)),
])
def test_week_of(text, ymd):
    s, e = start_end(text)
    assert (s, e) == _week(*ymd)
    assert span(text).width.days == 7
    assert parse(text)[1] == ""


@pytest.mark.parametrize("ymd", [
    (2026, 7, 20),
    (2026, 1, 15),
    (2026, 12, 10),
    (2026, 3, 5),
])
def test_bare_date_is_a_single_day(ymd):
    MN = {7: 'יולי', 1: 'ינואר', 12: 'דצמבר', 3: 'מרץ', 6: 'יוני', 8: 'אוגוסט'}
    text = '{d} ב{M} {y}'.format(d=ymd[2], M=MN[ymd[1]], y=ymd[0])
    assert span(text).width.days == 1


@pytest.mark.parametrize("text", [
    'השבוע של',
    'שבוע של',
])
def test_marker_without_a_date_does_not_parse(text):
    nomatch(text)
