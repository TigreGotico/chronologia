# -*- coding: utf-8 -*-
"""Relative offsets (both directions), named days, weekday reference."""
from datetime import timedelta  # noqa: F401

import pytest
from dateutil.relativedelta import relativedelta  # noqa: F401

from ._corpus import ANCHOR, ad, start, nomatch

def _day_cases():
    out = []
    for n in (1, 2, 3, 5, 10):
        d = timedelta(days=n)
        unit = "dias" if n != 1 else "dia"
        out.append((f"há {n} {unit}", ANCHOR - d))
        out.append((f"{n} {unit} atrás", ANCHOR - d))
        out.append((f"em {n} {unit}", ANCHOR + d))
        out.append((f"dentro de {n} {unit}", ANCHOR + d))
    return out

def _week_cases():
    out = []
    for n in (1, 2, 3, 5, 10):
        d = timedelta(weeks=n)
        unit = "semanas" if n != 1 else "semana"
        out.append((f"há {n} {unit}", ANCHOR - d))
        out.append((f"{n} {unit} atrás", ANCHOR - d))
        out.append((f"em {n} {unit}", ANCHOR + d))
        out.append((f"dentro de {n} {unit}", ANCHOR + d))
    return out

def _month_cases():
    out = []
    for n in (1, 2, 3, 5, 10):
        d = relativedelta(months=n)
        unit = "meses" if n != 1 else "mês"
        out.append((f"há {n} {unit}", ANCHOR - d))
        out.append((f"{n} {unit} atrás", ANCHOR - d))
        out.append((f"em {n} {unit}", ANCHOR + d))
        out.append((f"dentro de {n} {unit}", ANCHOR + d))
    return out

def _year_cases():
    out = []
    for n in (1, 2, 3, 5, 10):
        d = relativedelta(years=n)
        unit = "anos" if n != 1 else "ano"
        out.append((f"há {n} {unit}", ANCHOR - d))
        out.append((f"{n} {unit} atrás", ANCHOR - d))
        out.append((f"em {n} {unit}", ANCHOR + d))
        out.append((f"dentro de {n} {unit}", ANCHOR + d))
    return out


_SPELLED = [("há dois dias", 2), ("há três dias", 3), ("há cinco dias", 5), ("há dez dias", 10), ("há vinte dias", 20)]


@pytest.mark.parametrize("text,n", _SPELLED)
def test_spelled_offsets(text, n):
    assert start(text) == ad(ANCHOR - timedelta(days=n))


@pytest.mark.parametrize("text,expected",
                         _day_cases() + _week_cases()
                         + _month_cases() + _year_cases())
def test_offsets(text, expected):
    assert start(text) == ad(expected)


# -- "daqui a ..." future offsets ----------------------------------------
# "daqui a" is the most common European-Portuguese way to say "in X from now"
# (Ciberduvidas/Priberam: "daqui a" = from this moment forward), the future
# twin of "dentro de".  The trailing preposition ("a"/"de") is absorbed the
# same way "dentro de" absorbs "de", and the count composes as a plain number,
# a quantifier ("uma"=1, "meia"=0.5), or a number x quantifier product
# ("tres quartos" = 3 x 0.25 hora = 45 min).

@pytest.mark.parametrize("text,expected", [
    ("daqui a uma semana", ANCHOR + timedelta(weeks=1)),
    ("daqui a dois dias", ANCHOR + timedelta(days=2)),
    ("daqui a três meses", ANCHOR + relativedelta(months=3)),
    ("daqui a um ano", ANCHOR + relativedelta(years=1)),
    ("daqui a 15 minutos", ANCHOR + timedelta(minutes=15)),
    ("daqui a meia hora", ANCHOR + timedelta(minutes=30)),
    ("daqui a três quartos de hora", ANCHOR + timedelta(minutes=45)),
])
def test_daqui_a_future(text, expected):
    assert start(text) == ad(expected)


# the same fractional-duration offsets also compose after "dentro de"
@pytest.mark.parametrize("text,expected", [
    ("dentro de meia hora", ANCHOR + timedelta(minutes=30)),
    ("dentro de três quartos de hora", ANCHOR + timedelta(minutes=45)),
])
def test_dentro_de_fractional(text, expected):
    assert start(text) == ad(expected)


# adversarial: "daqui a 15 minutos" is a future offset, NOT the clock time
# 15:00 -- the offset reading must win, so the resolved minute is anchor+15.
def test_daqui_a_minutes_not_clock():
    s = start("daqui a 15 minutos")
    assert (s.hour, s.minute) == (13, 19)
    assert s != ad(ANCHOR.replace(hour=15, minute=0))


@pytest.mark.parametrize("text,off", [("hoje", 0), ("ontem", -1), ("amanhã", 1), ("anteontem", -2)])
def test_named_days(text, off):
    exp = (ANCHOR + timedelta(days=off)).replace(hour=0, minute=0, second=0,
                                                 microsecond=0)
    assert start(text) == ad(exp)


def test_weekday_next():
    # próxima segunda: the next occurrence of weekday 0 strictly after anchor
    ahead = ((0 - ANCHOR.weekday()) % 7) or 7
    exp = (ANCHOR + timedelta(days=ahead)).replace(hour=0, minute=0,
                                                   second=0, microsecond=0)
    assert start("próxima segunda") == ad(exp)
