# -*- coding: utf-8 -*-
"""The "week of <date>" construction for nb: widen a date to its week."""
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
    ('uken med 20 juli 2026', (2026, 7, 20)),
    ('uken med 15 januar 2026', (2026, 1, 15)),
    ('uken med 10 desember 2026', (2026, 12, 10)),
    ('uken med 5 mars 2026', (2026, 3, 5)),
    ('uken med 4 juli 2026', (2026, 7, 4)),
    ('uken med 11 mars 2026', (2026, 3, 11)),
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
    MN = {7: 'juli', 1: 'januar', 12: 'desember', 3: 'mars', 6: 'juni', 8: 'august'}
    text = "%d %s %d" % (ymd[2], MN[ymd[1]], ymd[0])
    assert span(text).width.days == 1


@pytest.mark.parametrize("text", [
    'uken med',
    'uken omkring',
])
def test_marker_without_a_date_does_not_parse(text):
    nomatch(text)
