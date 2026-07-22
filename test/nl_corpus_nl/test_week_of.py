# -*- coding: utf-8 -*-
"""The "week of <date>" construction: widen a date to its calendar week.

The locale carries a "week of" marker (marker_weekof.voc); the engine
resolves the inner date normally, then widens it to the seven-day week
(week_start = monday for these locales) that contains it.  Expected weeks
are derived by independent Python date arithmetic, never from the parser.
"""
from datetime import date, datetime, timedelta

import pytest

from ._corpus import AstroDate, nomatch, parse, span, start_end


def _week(y, m, d):
    """The monday-start week containing (y, m, d), as (start, end) AstroDates."""
    day = date(y, m, d)
    ws = day - timedelta(days=day.weekday())
    start = AstroDate(ws.year, ws.month, ws.day)
    end_dt = datetime(ws.year, ws.month, ws.day) + timedelta(days=7)
    return start, AstroDate(end_dt.year, end_dt.month, end_dt.day)


@pytest.mark.parametrize("text,ymd", [
    ('de week van 20 juli 2026', (2026, 7, 20)),
    ('week van 20 juli 2026', (2026, 7, 20)),
    ('de week van 15 januari 2026', (2026, 1, 15)),
    ('week van 15 januari 2026', (2026, 1, 15)),
    ('de week van 10 december 2026', (2026, 12, 10)),
    ('week van 10 december 2026', (2026, 12, 10)),
    ('de week van 5 maart 2026', (2026, 3, 5)),
    ('week van 5 maart 2026', (2026, 3, 5)),
])
def test_week_of(text, ymd):
    s, e = start_end(text)
    assert (s, e) == _week(*ymd)
    assert span(text).width.days == 7           # a whole week wide
    assert parse(text)[1] == ""                 # marker consumed


@pytest.mark.parametrize("ymd", [
    (2026, 7, 20),
    (2026, 1, 15),
    (2026, 12, 10),
    (2026, 3, 5),
])
def test_bare_date_is_a_single_day(ymd):
    # without the "week of" marker the same date is one day wide, proving
    # the marker is what widens it to the week (no accidental widening)
    MN = {1: 'januari', 3: 'maart', 7: 'juli', 12: 'december'}
    text = f"{ymd[2]} {MN[ymd[1]]} {ymd[0]}"
    assert span(text).width.days == 1


@pytest.mark.parametrize("text", [
    'de week van',
    'week van',
])
def test_marker_without_a_date_does_not_parse(text):
    # the bare marker names no date -- nothing to widen, so nothing matches
    nomatch(text)
