# -*- coding: utf-8 -*-
"""Portuguese national / civil holidays bound by name (``holiday_ref``).

Anchor 2017-06-27 (a Tuesday, 13:04).  Bare rule = next occurrence on or after
the anchor.  Each fixed civil date is hand-verified against its official source:

* Dia da Liberdade -- 25 Apr (1974 Carnation Revolution, Lei n.º 7/74).
* Dia do Trabalhador -- 1 May (International Workers' Day).
* Dia de Portugal, de Camões e das Comunidades -- 10 Jun.
* Implantação da República -- 5 Oct (1910).
* Restauração da Independência -- 1 Dec (1640).
* Imaculada Conceição -- 8 Dec (Solemnity of the Immaculate Conception).
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, parse, span, start, nomatch

_BARE = [
    ("dia da liberdade", (2018, 4, 25)),
    ("dia do trabalhador", (2018, 5, 1)),
    ("dia do trabalho", (2018, 5, 1)),
    ("primeiro de maio", (2018, 5, 1)),
    ("dia de portugal", (2018, 6, 10)),
    ("dia de camões", (2018, 6, 10)),
    ("implantação da república", (2017, 10, 5)),
    ("dia da república", (2017, 10, 5)),
    ("restauração da independência", (2017, 12, 1)),
    ("dia da restauração", (2017, 12, 1)),
    ("imaculada conceição", (2017, 12, 8)),
    ("nossa senhora da conceição", (2017, 12, 8)),
]


@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_national_holiday(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ("dia da liberdade 2019", (2019, 4, 25)),
    ("dia de portugal 2019", (2019, 6, 10)),
    ("implantação da república 2019", (2019, 10, 5)),
])
def test_explicit_year(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


# -- collision regression pins --
@pytest.mark.parametrize("text,ymd,days", [
    ("abril", (2017, 4, 1), 30),
    ("junho", (2017, 6, 1), 30),
    ("outubro", (2017, 10, 1), 31),
])
def test_bare_month_unchanged(text, ymd, days):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=days)


def test_bare_weekday_unchanged():
    assert start("segunda-feira") == AstroDate(2017, 7, 3)
    assert span("segunda-feira").width == timedelta(days=1)
