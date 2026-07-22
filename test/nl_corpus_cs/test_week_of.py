# -*- coding: utf-8 -*-
"""The "week of <date>" construction for cs: widen a date to its week."""
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
    ('týden od 20 července 2026', (2026, 7, 20)),
    ('týden od 15 ledna 2026', (2026, 1, 15)),
    ('týden od 10 prosince 2026', (2026, 12, 10)),
    ('týden od 5 března 2026', (2026, 3, 5)),
    ('týden od 4 července 2026', (2026, 7, 4)),
    ('týden od 11 března 2026', (2026, 3, 11)),
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
    MN = {7: 'července', 1: 'ledna', 12: 'prosince', 3: 'března', 6: 'června', 8: 'srpna'}
    text = "%d %s %d" % (ymd[2], MN[ymd[1]], ymd[0])
    assert span(text).width.days == 1


@pytest.mark.parametrize("text", [
    'týden od',
    'týden okolo',
])
def test_marker_without_a_date_does_not_parse(text):
    nomatch(text)
