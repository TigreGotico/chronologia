# -*- coding: utf-8 -*-
"""Ukrainian national / civil holidays bound by name (round 2, ``holiday_ref``).

Anchor 2017-06-27 (a Tuesday, 13:04). Bare rule = next occurrence on or after
the anchor. Each fixed civil date is hand-verified against its official source
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
    ('день незалежності', (2017, 8, 24)),
    ('день незалежності україни', (2017, 8, 24)),
    ('день конституції', (2017, 6, 28)),
    ('день конституції україни', (2017, 6, 28)),
    ('день захисника', (2017, 10, 14)),
    ('день захисників', (2017, 10, 14)),
    ('день захисників і захисниць', (2017, 10, 14)),
    ('міжнародний жіночий день', (2018, 3, 8)),
    ('жіночий день', (2018, 3, 8)),
    ('день перемоги', (2018, 5, 9)),
    ('день праці', (2018, 5, 1)),
    ('міжнародний день праці', (2018, 5, 1)),
]


@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_national_holiday(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ('день незалежності 2019', (2019, 8, 24)),
    ('день перемоги 2019', (2019, 5, 9)),
])
def test_explicit_year(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


# -- collision regression pins: the bare month / weekday / numeric-date tokens
#    the holiday names embed must stay byte-identical to their pre-holiday
#    reading (a whole-month span, a single weekday, a plain day-date). --
def test_bare_month_unchanged():
    assert start('серпень') == AstroDate(2017, 8, 1)
    assert span('серпень').width == timedelta(days=31)


def test_bare_weekday_unchanged():
    assert start('понеділок') == AstroDate(2017, 7, 3)
    assert span('понеділок').width == timedelta(days=1)
