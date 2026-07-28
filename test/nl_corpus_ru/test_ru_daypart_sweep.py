# -*- coding: utf-8 -*-
"""Daypart-on-date sweep (ru) -- "утром 5 июня 2019" etc.

The engine maps the Russian dayparts to fixed wall-clock bands on the named
day: ночью = 00:00-04:00, утром = 04:00-12:00, днём = 12:00-18:00, вечером =
18:00-24:00.  Gold is that fixed banding on the explicit day-month-year date,
independent of the parser.  Anchor 2017-06-27."""
from datetime import datetime, timedelta

import pytest

from ._corpus import AstroDate, start_end

_MONTHS_GEN = [None, "января", "февраля", "марта", "апреля", "мая", "июня",
               "июля", "августа", "сентября", "октября", "ноября", "декабря"]

# daypart -> (start hour, end hour)
_BANDS = {
    "ночью": (0, 4),
    "утром": (4, 12),
    "днём": (12, 18),
    "вечером": (18, 24),
}

# (day, month) sample dates across the calendar
_DATES = [(5, 6), (15, 3), (1, 10), (20, 12), (28, 2), (9, 5), (31, 1), (11, 9)]
_YEARS = (2018, 2019, 2020, 2021)


def _ad(dt):
    return AstroDate(dt.year, dt.month, dt.day, dt.hour, dt.minute)


def _cases():
    out = []
    for word, (h0, h1) in _BANDS.items():
        for day, month in _DATES:
            for year in _YEARS:
                base = datetime(year, month, day)
                s = base + timedelta(hours=h0)
                e = base + timedelta(hours=h1)
                text = f"{word} {day} {_MONTHS_GEN[month]} {year}"
                out.append((text, s, e))
    return out


@pytest.mark.parametrize("text,s,e", _cases())
def test_daypart_on_date(text, s, e):
    st, en = start_end(text)
    assert st == _ad(s)
    assert en == _ad(e)
