# -*- coding: utf-8 -*-
"""English national / civil / observance holidays bound by name (``holiday_ref``).

Anchor 2017-06-27 (a Tuesday, 13:04).  Bare rule = next occurrence on or after
the anchor.  Each fixed civil date is hand-verified against its official source:

* Juneteenth -- 19 Jun (U.S. federal holiday, Pub. L. 117-17).
* Cinco de Mayo -- 5 May (Battle of Puebla, 1862; U.S. cultural observance).
* Groundhog Day -- 2 Feb (North American folk observance).
* Earth Day -- 22 Apr (environmental observance since 1970).
* Armistice Day / Remembrance Day -- 11 Nov (Armistice of 1918).
* All Souls' Day -- 2 Nov (Commemoration of All the Faithful Departed).
* May Day -- 1 May (International Workers' Day).
* April Fools' Day -- 1 Apr (folk day of pranks).
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, parse, span, start, nomatch

_BARE = [
    ("juneteenth", (2018, 6, 19)),
    ("cinco de mayo", (2018, 5, 5)),
    ("groundhog day", (2018, 2, 2)),
    ("groundhog's day", (2018, 2, 2)),
    ("earth day", (2018, 4, 22)),
    ("armistice day", (2017, 11, 11)),
    ("remembrance day", (2017, 11, 11)),
    ("all souls' day", (2017, 11, 2)),
    ("all souls day", (2017, 11, 2)),
    ("may day", (2018, 5, 1)),
    ("international workers' day", (2018, 5, 1)),
    ("april fools' day", (2018, 4, 1)),
    ("april fools day", (2018, 4, 1)),
    ("april fool's day", (2018, 4, 1)),
]


@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_national_holiday(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ("juneteenth 2022", (2022, 6, 19)),
    ("earth day 2020", (2020, 4, 22)),
    ("all souls day 2019", (2019, 11, 2)),
    ("april fools day 2019", (2019, 4, 1)),
    ("cinco de mayo 2020", (2020, 5, 5)),
])
def test_explicit_year(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


# -- collision regression pins: the tokens the multi-word holiday names embed
#    (bare "day", the weekday, the month) must stay byte-identical. --
def test_bare_day_still_nomatch():
    # "day" alone is not a holiday and never was.
    nomatch("day")


def test_bare_weekday_unchanged():
    assert start("monday") == AstroDate(2017, 7, 3)
    assert span("monday").width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd,days", [
    ("february", (2017, 2, 1), 28),
    ("april", (2017, 4, 1), 30),
    ("june", (2017, 6, 1), 30),
    ("november", (2017, 11, 1), 30),
])
def test_bare_month_unchanged(text, ymd, days):
    # "April Fools' Day", "Groundhog Day", etc. must not steal the bare month.
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=days)
