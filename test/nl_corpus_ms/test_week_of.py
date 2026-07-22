# -*- coding: utf-8 -*-
"""The "week of <date>" construction for ms: widen a date to its week."""
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
    ('minggu 20 julai 2026', (2026, 7, 20)),
    ('minggu 15 januari 2026', (2026, 1, 15)),
    ('minggu 10 disember 2026', (2026, 12, 10)),
    ('minggu 5 mac 2026', (2026, 3, 5)),
    ('minggu 4 julai 2026', (2026, 7, 4)),
    ('minggu 11 mac 2026', (2026, 3, 11)),
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
    MN = {7: 'julai', 1: 'januari', 12: 'disember', 3: 'mac', 6: 'jun', 8: 'ogos'}
    text = "%d %s %d" % (ymd[2], MN[ymd[1]], ymd[0])
    assert span(text).width.days == 1


@pytest.mark.parametrize("text", [
    'minggu',
    'minggu pada',
])
def test_marker_without_a_date_does_not_parse(text):
    nomatch(text)
