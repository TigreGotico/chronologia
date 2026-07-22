# -*- coding: utf-8 -*-
"""The "week of <date>" construction for ar: widen a date to its week.

Week starts on Saturday here, so the expected week is derived with that offset,
independently of the parser.
"""
from datetime import date, datetime, timedelta

import pytest

from ._corpus import AstroDate, nomatch, parse, span, start_end

_WKSTART = 5  # Mon=0 .. Sun=6


def _week(y, m, d):
    day = date(y, m, d)
    back = (day.weekday() - _WKSTART) % 7
    ws = day - timedelta(days=back)
    start = AstroDate(ws.year, ws.month, ws.day)
    end_dt = datetime(ws.year, ws.month, ws.day) + timedelta(days=7)
    return start, AstroDate(end_dt.year, end_dt.month, end_dt.day)


@pytest.mark.parametrize("text,ymd", [
    ('أسبوع 20 يوليو 2026', (2026, 7, 20)),
    ('أسبوع 15 يناير 2026', (2026, 1, 15)),
    ('أسبوع 10 ديسمبر 2026', (2026, 12, 10)),
    ('أسبوع 5 مارس 2026', (2026, 3, 5)),
    ('أسبوع 4 يوليو 2026', (2026, 7, 4)),
    ('أسبوع 11 مارس 2026', (2026, 3, 11)),
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
    MN = {7: 'يوليو', 1: 'يناير', 12: 'ديسمبر', 3: 'مارس', 6: 'يونيو', 8: 'أغسطس'}
    text = '{d} {M} {y}'.format(d=ymd[2], M=MN[ymd[1]], y=ymd[0])
    assert span(text).width.days == 1


@pytest.mark.parametrize("text", [
    'أسبوع',
    'اسبوع',
])
def test_marker_without_a_date_does_not_parse(text):
    nomatch(text)
