# -*- coding: utf-8 -*-
"""Spanish national / civil holidays bound by name (``holiday_ref``).

Anchor 2017-06-27 (a Tuesday, 13:04).  Bare rule = next occurrence on or after
the anchor.  Each fixed civil date is hand-verified against its official source:

* Día del Trabajador / Día del Trabajo -- 1 May (International Workers' Day).
* Inmaculada Concepción -- 8 Dec (Solemnity of the Immaculate Conception).
* Fiesta Nacional de España / Día de la Hispanidad -- 12 Oct (Ley 18/1987).
* Día de la Constitución -- 6 Dec (1978 constitutional referendum).

Reyes/Epifanía (6 Jan), Asunción (15 Aug) and Todos los Santos (1 Nov) already
bind through the shared ``epiphany`` / ``assumption`` / ``all_saints`` keys
(see ``test_nl_holiday_ref.py``) and are not re-tested here.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, parse, span, start, nomatch

_BARE = [
    ("día del trabajador", (2018, 5, 1)),
    ("día del trabajo", (2018, 5, 1)),
    ("primero de mayo", (2018, 5, 1)),
    ("inmaculada concepción", (2017, 12, 8)),
    ("la inmaculada", (2017, 12, 8)),
    ("día de la inmaculada", (2017, 12, 8)),
    ("fiesta nacional", (2017, 10, 12)),
    ("día de la hispanidad", (2017, 10, 12)),
    ("día de la constitución", (2017, 12, 6)),
]


@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_national_holiday(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ("día del trabajador 2020", (2020, 5, 1)),
    ("día de la hispanidad 2019", (2019, 10, 12)),
    ("día de la constitución 2019", (2019, 12, 6)),
])
def test_explicit_year(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


# -- collision regression pins: the month / weekday tokens the holiday names
#    embed must stay byte-identical to their pre-holiday reading. --
@pytest.mark.parametrize("text,ymd,days", [
    ("mayo", (2017, 5, 1), 31),    # bare month May, NOT labour day
    ("abril", (2017, 4, 1), 30),   # bare month April
])
def test_bare_month_unchanged(text, ymd, days):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=days)


def test_bare_weekday_unchanged():
    assert start("lunes") == AstroDate(2017, 7, 3)
    assert span("lunes").width == timedelta(days=1)


def test_explicit_date_unchanged():
    # "8 de mayo" stays a plain day-date (prefer-future), not a holiday name.
    assert start("8 de mayo") == AstroDate(2018, 5, 8)
