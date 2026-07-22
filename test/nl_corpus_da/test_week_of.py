# -*- coding: utf-8 -*-
"""The "week of <date>" construction for da: widen a date to its week."""
from datetime import date, datetime, timedelta

import pytest

from ._corpus import AstroDate, nomatch, parse, span, start_end


def _week(y, m, d):
    day = date(y, m, d)
    ws = day - timedelta(days=day.weekday())
    start = AstroDate(ws.year, ws.month, ws.day)
    end_dt = datetime(ws.year, ws.month, ws.day) + timedelta(days=7)
    return start, AstroDate(end_dt.year, end_dt.month, end_dt.day)


@pytest.mark.parametrize("text,ymd", [
    ('ugen med 20 juli 2026', (2026, 7, 20)),
    ('ugen med 15 januar 2026', (2026, 1, 15)),
    ('ugen med 10 december 2026', (2026, 12, 10)),
    ('ugen med 5 marts 2026', (2026, 3, 5)),
    ('ugen med 4 juli 2026', (2026, 7, 4)),
    ('ugen med 11 marts 2026', (2026, 3, 11)),
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
    MN = {7: 'juli', 1: 'januar', 12: 'december', 3: 'marts', 6: 'juni', 8: 'august'}
    text = "%d %s %d" % (ymd[2], MN[ymd[1]], ymd[0])
    assert span(text).width.days == 1


@pytest.mark.parametrize("text", [
    'ugen med',
    'ugen omkring',
])
def test_marker_without_a_date_does_not_parse(text):
    nomatch(text)
