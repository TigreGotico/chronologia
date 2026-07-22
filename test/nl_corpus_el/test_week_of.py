# -*- coding: utf-8 -*-
"""The "week of <date>" construction for el: widen a date to its week."""
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
    ('η εβδομάδα του 20 ιουλίου 2026', (2026, 7, 20)),
    ('η εβδομάδα του 15 ιανουαρίου 2026', (2026, 1, 15)),
    ('η εβδομάδα του 10 δεκεμβρίου 2026', (2026, 12, 10)),
    ('η εβδομάδα του 5 μαρτίου 2026', (2026, 3, 5)),
    ('η εβδομάδα του 4 ιουλίου 2026', (2026, 7, 4)),
    ('η εβδομάδα του 11 μαρτίου 2026', (2026, 3, 11)),
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
    MN = {7: 'ιουλίου', 1: 'ιανουαρίου', 12: 'δεκεμβρίου', 3: 'μαρτίου', 6: 'ιουνίου', 8: 'αυγούστου'}
    text = '{d} {M} {y}'.format(d=ymd[2], M=MN[ymd[1]], y=ymd[0])
    assert span(text).width.days == 1


@pytest.mark.parametrize("text", [
    'η εβδομάδα του',
    'εβδομάδα του',
])
def test_marker_without_a_date_does_not_parse(text):
    nomatch(text)
