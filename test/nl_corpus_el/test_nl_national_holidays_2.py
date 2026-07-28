# -*- coding: utf-8 -*-
"""Greek national / civil holidays bound by name (round 2, ``holiday_ref``).

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
    ('πρωτομαγιά', (2018, 5, 1)),
    ('εργατική πρωτομαγιά', (2018, 5, 1)),
    ('25η μαρτίου', (2018, 3, 25)),
    ('εικοστή πέμπτη μαρτίου', (2018, 3, 25)),
    ('ευαγγελισμός της θεοτόκου', (2018, 3, 25)),
    ('28η οκτωβρίου', (2017, 10, 28)),
    ('επέτειος του όχι', (2017, 10, 28)),
    ('ημέρα του όχι', (2017, 10, 28)),
    ('του όχι', (2017, 10, 28)),
]


@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_national_holiday(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ('25η μαρτίου 2019', (2019, 3, 25)),
])
def test_explicit_year(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


# -- collision regression pins: the bare month / weekday / numeric-date tokens
#    the holiday names embed must stay byte-identical to their pre-holiday
#    reading (a whole-month span, a single weekday, a plain day-date). --
def test_bare_month_unchanged():
    assert start('μάρτιος') == AstroDate(2017, 3, 1)
    assert span('μάρτιος').width == timedelta(days=31)


def test_bare_weekday_unchanged():
    assert start('δευτέρα') == AstroDate(2017, 7, 3)
    assert span('δευτέρα').width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ('25 μαρτίου', (2018, 3, 25)),
])
def test_numeric_date_unchanged(text, ymd):
    # a plain numeric day-date the holiday name embeds stays a 1-day date.
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)
