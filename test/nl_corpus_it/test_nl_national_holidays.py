# -*- coding: utf-8 -*-
"""Italian national / civil holidays bound by name (``holiday_ref``).

Anchor 2017-06-27 (a Tuesday, 13:04).  Bare rule = next occurrence on or after
the anchor.  Each fixed civil date is hand-verified against its official source:

* Festa della Liberazione -- 25 Apr (Liberation Day, 1945).
* Festa del Lavoro -- 1 May (International Workers' Day).
* Festa della Repubblica -- 2 Jun (Republic Day, 1946 referendum).
* Immacolata -- 8 Dec (Solemnity of the Immaculate Conception).

Ferragosto (15 Aug) already binds through the shared ``assumption`` key
(see ``test_nl_holiday_ref.py``).
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, parse, span, start, nomatch

_BARE = [
    ("festa della liberazione", (2018, 4, 25)),
    ("anniversario della liberazione", (2018, 4, 25)),
    ("festa del lavoro", (2018, 5, 1)),
    ("primo maggio", (2018, 5, 1)),
    ("festa della repubblica", (2018, 6, 2)),
    ("immacolata", (2017, 12, 8)),
    ("immacolata concezione", (2017, 12, 8)),
]


@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_national_holiday(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ("festa della liberazione 2021", (2021, 4, 25)),
    ("festa della repubblica 2021", (2021, 6, 2)),
    ("festa del lavoro 2020", (2020, 5, 1)),
])
def test_explicit_year(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


# -- collision regression pins --
@pytest.mark.parametrize("text,ymd,days", [
    ("maggio", (2017, 5, 1), 31),
    ("aprile", (2017, 4, 1), 30),
    ("giugno", (2017, 6, 1), 30),
])
def test_bare_month_unchanged(text, ymd, days):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=days)


def test_bare_weekday_unchanged():
    assert start("lunedì") == AstroDate(2017, 7, 3)
    assert span("lunedì").width == timedelta(days=1)
