# -*- coding: utf-8 -*-
"""Hungarian national / civil holidays bound by name (round 2, ``holiday_ref``).

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
    ('a munka ünnepe', (2018, 5, 1)),
    ('munka ünnepe', (2018, 5, 1)),
    ('nemzeti ünnep', (2018, 3, 15)),
    ('1848-as forradalom', (2018, 3, 15)),
    ('az 1848-as forradalom emléknapja', (2018, 3, 15)),
    ('államalapítás ünnepe', (2017, 8, 20)),
    ('az államalapítás ünnepe', (2017, 8, 20)),
    ('szent istván ünnepe', (2017, 8, 20)),
    ('1956-os forradalom', (2017, 10, 23)),
    ('az 1956-os forradalom emléknapja', (2017, 10, 23)),
]


@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_national_holiday(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ('nemzeti ünnep 2019', (2019, 3, 15)),
])
def test_explicit_year(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


# -- collision regression pins: the bare month / weekday / numeric-date tokens
#    the holiday names embed must stay byte-identical to their pre-holiday
#    reading (a whole-month span, a single weekday, a plain day-date). --
def test_bare_month_unchanged():
    assert start('március') == AstroDate(2017, 3, 1)
    assert span('március').width == timedelta(days=31)


def test_bare_weekday_unchanged():
    assert start('hétfő') == AstroDate(2017, 7, 3)
    assert span('hétfő').width == timedelta(days=1)
