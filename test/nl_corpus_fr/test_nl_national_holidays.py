# -*- coding: utf-8 -*-
"""French national / civil holidays bound by name (``holiday_ref``).

Anchor 2017-06-27 (a Tuesday, 13:04).  Bare rule = next occurrence on or after
the anchor.  Each fixed civil date is hand-verified against its official source:

* Fête du Travail -- 1 May (International Workers' Day).
* Fête Nationale / le quatorze juillet -- 14 Jul (Bastille Day, loi 1880).
* Armistice -- 11 Nov (Armistice of 1918).
* Fête de la Victoire / Victoire 1945 -- 8 May (loi n° 81-893).

Assomption (15 Aug) and Toussaint (1 Nov) already bind through the shared
``assumption`` / ``all_saints`` keys (see ``test_nl_holiday_ref.py``).
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, parse, span, start, nomatch

_BARE = [
    ("fête du travail", (2018, 5, 1)),
    ("premier mai", (2018, 5, 1)),
    ("fête nationale", (2017, 7, 14)),
    ("quatorze juillet", (2017, 7, 14)),
    ("le quatorze juillet", (2017, 7, 14)),
    ("armistice", (2017, 11, 11)),
    ("jour de l'armistice", (2017, 11, 11)),
    ("le onze novembre", (2017, 11, 11)),
    ("fête de la victoire", (2018, 5, 8)),
    ("victoire 1945", (2018, 5, 8)),
    ("le huit mai", (2018, 5, 8)),
]


@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_national_holiday(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ("fête nationale 2019", (2019, 7, 14)),
    ("armistice 2019", (2019, 11, 11)),
    ("fête du travail 2020", (2020, 5, 1)),
])
def test_explicit_year(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


# -- collision regression pins --
@pytest.mark.parametrize("text,ymd,days", [
    ("mai", (2017, 5, 1), 31),
    ("juillet", (2017, 7, 1), 31),
    ("novembre", (2017, 11, 1), 30),
])
def test_bare_month_unchanged(text, ymd, days):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=days)


def test_bare_weekday_unchanged():
    assert start("lundi") == AstroDate(2017, 7, 3)
    assert span("lundi").width == timedelta(days=1)
