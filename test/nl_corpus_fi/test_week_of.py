# -*- coding: utf-8 -*-
"""The "week of <date>" construction for fi: widen a date to its week."""
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
    ('viikko 20. heinäkuuta 2026', (2026, 7, 20)),
    ('viikko 15. tammikuuta 2026', (2026, 1, 15)),
    ('viikko 10. joulukuuta 2026', (2026, 12, 10)),
    ('viikko 5. maaliskuuta 2026', (2026, 3, 5)),
    ('viikko 4. heinäkuuta 2026', (2026, 7, 4)),
    ('viikko 11. maaliskuuta 2026', (2026, 3, 11)),
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
    MN = {7: 'heinäkuuta', 1: 'tammikuuta', 12: 'joulukuuta', 3: 'maaliskuuta', 6: 'kesäkuuta', 8: 'elokuuta'}
    text = '{d}. {M} {y}'.format(d=ymd[2], M=MN[ymd[1]], y=ymd[0])
    assert span(text).width.days == 1


@pytest.mark.parametrize("text", [
    'viikko',
    'viikolla',
])
def test_marker_without_a_date_does_not_parse(text):
    nomatch(text)
