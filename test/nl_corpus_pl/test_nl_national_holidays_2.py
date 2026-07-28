# -*- coding: utf-8 -*-
"""Polish national / civil holidays bound by name (round 2, ``holiday_ref``).

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
    ('święto pracy', (2018, 5, 1)),
    ('konstytucji 3 maja', (2018, 5, 3)),
    ('święto konstytucji 3 maja', (2018, 5, 3)),
    ('święto niepodległości', (2017, 11, 11)),
    ('narodowe święto niepodległości', (2017, 11, 11)),
    ('dzień niepodległości', (2017, 11, 11)),
    ('wniebowzięcie', (2017, 8, 15)),
    ('wniebowzięcie najświętszej maryi panny', (2017, 8, 15)),
]


@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_national_holiday(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ('święto pracy 2020', (2020, 5, 1)),
    ('święto niepodległości 2019', (2019, 11, 11)),
    ('konstytucji 3 maja 2020', (2020, 5, 3)),
])
def test_explicit_year(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


# -- collision regression pins: the bare month / weekday / numeric-date tokens
#    the holiday names embed must stay byte-identical to their pre-holiday
#    reading (a whole-month span, a single weekday, a plain day-date). --
def test_bare_month_unchanged():
    assert start('maja') == AstroDate(2017, 5, 1)
    assert span('maja').width == timedelta(days=31)


def test_bare_weekday_unchanged():
    assert start('poniedziałek') == AstroDate(2017, 7, 3)
    assert span('poniedziałek').width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ('3 maja', (2018, 5, 3)),
])
def test_numeric_date_unchanged(text, ymd):
    # a plain numeric day-date the holiday name embeds stays a 1-day date.
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)
