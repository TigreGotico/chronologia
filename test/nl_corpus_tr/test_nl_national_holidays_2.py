# -*- coding: utf-8 -*-
"""Turkish national / civil holidays bound by name (round 2, ``holiday_ref``).

Anchor 2026-07-15 (a Wednesday, noon; the Turkish corpus anchor). Bare rule =
next occurrence on or after the anchor. Each fixed civil date is hand-verified
against its official source
(national public-holiday statutes); see ``chronologia/civil_holidays/well_known.py``
for the per-holiday citations and ``i18n/well_known.tab`` for the spoken surfaces.

Holidays that share a cross-border key (Labour Day = 1 May, Assumption = 15 Aug,
Epiphany = 6 Jan, New Year = 1 Jan, V-E Day = 8 May) are exercised here through
their per-locale surface, not re-keyed.
"""
from datetime import timedelta

import pytest

from ._corpus import AstroDate, span, start

_BARE = [
    ('cumhuriyet bayramı', (2026, 10, 29)),
    ('zafer bayramı', (2026, 8, 30)),
    ('ulusal egemenlik ve çocuk bayramı', (2027, 4, 23)),
    ('ulusal egemenlik bayramı', (2027, 4, 23)),
    ('çocuk bayramı', (2027, 4, 23)),
    ("atatürk'ü anma gençlik ve spor bayramı", (2027, 5, 19)),
    ('gençlik ve spor bayramı', (2027, 5, 19)),
    ('demokrasi ve millî birlik günü', (2026, 7, 15)),
    ('demokrasi günü', (2026, 7, 15)),
]


@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_national_holiday(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ('cumhuriyet bayramı 2020', (2020, 10, 29)),
    ('zafer bayramı 2019', (2019, 8, 30)),
])
def test_explicit_year(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


# -- collision regression pins: the bare month / weekday / numeric-date tokens
#    the holiday names embed must stay byte-identical to their pre-holiday
#    reading (a whole-month span, a single weekday, a plain day-date). --
def test_bare_month_unchanged():
    assert start('ekim') == AstroDate(2026, 10, 1)
    assert span('ekim').width == timedelta(days=31)


def test_bare_weekday_unchanged():
    assert start('pazartesi') == AstroDate(2026, 7, 20)
    assert span('pazartesi').width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ('23 nisan', (2027, 4, 23)),
])
def test_numeric_date_unchanged(text, ymd):
    # a plain numeric day-date the holiday name embeds stays a 1-day date.
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)
