# -*- coding: utf-8 -*-
"""Romanian national / civil holidays bound by name (round 2, ``holiday_ref``).

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
    ('anul nou', (2018, 1, 1)),
    ('ziua muncii', (2018, 5, 1)),
    ('ziua copilului', (2018, 6, 1)),
    ('ziua internațională a copilului', (2018, 6, 1)),
    ('ziua națională', (2017, 12, 1)),
    ('ziua națională a româniei', (2017, 12, 1)),
    ('ziua marii uniri', (2017, 12, 1)),
    ('unirea principatelor', (2018, 1, 24)),
    ('ziua unirii principatelor române', (2018, 1, 24)),
    ('mica unire', (2018, 1, 24)),
    ('adormirea maicii domnului', (2017, 8, 15)),
    ('sfânta maria mare', (2017, 8, 15)),
]


@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_national_holiday(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ('ziua națională 2019', (2019, 12, 1)),
    ('ziua muncii 2020', (2020, 5, 1)),
])
def test_explicit_year(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


# -- collision regression pins: the bare month / weekday / numeric-date tokens
#    the holiday names embed must stay byte-identical to their pre-holiday
#    reading (a whole-month span, a single weekday, a plain day-date). --
def test_bare_month_unchanged():
    assert start('decembrie') == AstroDate(2017, 12, 1)
    assert span('decembrie').width == timedelta(days=31)


def test_bare_weekday_unchanged():
    assert start('luni') == AstroDate(2017, 7, 3)
    assert span('luni').width == timedelta(days=1)
