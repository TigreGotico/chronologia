# -*- coding: utf-8 -*-
"""Czech national / civil holidays bound by name (round 2, ``holiday_ref``).

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
    ('svátek práce', (2018, 5, 1)),
    ('den vítězství', (2018, 5, 8)),
    ('cyril a metoděj', (2017, 7, 5)),
    ('svatý cyril a metoděj', (2017, 7, 5)),
    ('den slovanských věrozvěstů', (2017, 7, 5)),
    ('jan hus', (2017, 7, 6)),
    ('den upálení mistra jana husa', (2017, 7, 6)),
    ('den české státnosti', (2017, 9, 28)),
    ('svatý václav', (2017, 9, 28)),
    ('vznik čsr', (2017, 10, 28)),
    ('vznik československa', (2017, 10, 28)),
    ('den vzniku samostatného československého státu', (2017, 10, 28)),
    ('boj za svobodu', (2017, 11, 17)),
    ('den boje za svobodu a demokracii', (2017, 11, 17)),
]


@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_national_holiday(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ('den vítězství 2019', (2019, 5, 8)),
    ('cyril a metoděj 2020', (2020, 7, 5)),
])
def test_explicit_year(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


# -- collision regression pins: the bare month / weekday / numeric-date tokens
#    the holiday names embed must stay byte-identical to their pre-holiday
#    reading (a whole-month span, a single weekday, a plain day-date). --
def test_bare_month_unchanged():
    assert start('květen') == AstroDate(2017, 5, 1)
    assert span('květen').width == timedelta(days=31)


def test_bare_weekday_unchanged():
    assert start('pondělí') == AstroDate(2017, 7, 3)
    assert span('pondělí').width == timedelta(days=1)
