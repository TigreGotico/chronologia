# -*- coding: utf-8 -*-
"""Holiday references in Persian (``holiday_ref``), newly wired for fa.

Anchor 2017-06-27 (Tuesday); a bare rule resolves to the next occurrence on or
after the anchor.  Movable non-Gregorian dates come from this engine's own
tabulated calendars (Umm al-Qura Hijri, arithmetic Solar Hijri for Nowruz,
tabulated Chinese).  Every expected date is derived by hand.

Persian postposes the relative marker (``نوروز آینده`` = "next Nowruz"), so a
``HOLIDAY REL_MARKER`` order is wired alongside the prefixed forms."""
from datetime import timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import parse, span, start, nomatch

_BARE = [
    ('نوروز', (2018, 3, 21)),
    ('عید نوروز', (2018, 3, 21)),
    ('عید فطر', (2018, 6, 15)),
    ('عید قربان', (2017, 9, 1)),
    ('رمضان', (2018, 5, 16)),
    ('عاشورا', (2017, 9, 30)),
    ('کریسمس', (2017, 12, 25)),
    ('سال نو هجری', (2017, 9, 21)),
    ('سال نو چینی', (2018, 2, 16)),
]


@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_holiday(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ('نوروز آینده', (2018, 3, 21)),    # next Nowruz (postposed marker)
    ('نوروز گذشته', (2017, 3, 21)),    # last Nowruz
    ('عید فطر آینده', (2018, 6, 15)),
])
def test_relative(text, ymd):
    assert start(text) == AstroDate(*ymd)


@pytest.mark.parametrize("text,ymd", [
    ('نوروز 2026', (2026, 3, 21)),
    ('کریسمس 2020', (2020, 12, 25)),
])
def test_explicit_year(text, ymd):
    assert start(text) == AstroDate(*ymd)


@pytest.mark.parametrize("text", [
    'قیمت برنج بالا رفت',
    'یک جلسه کاری',
])
def test_no_holiday_no_match(text):
    nomatch(text)
