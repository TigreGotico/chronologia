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
        unit = "días" if n != 1 else "día"
        out.append((f"hai {n} {unit}", ANCHOR - d))
        out.append((f"{n} {unit} atrás", ANCHOR - d))
        out.append((f"en {n} {unit}", ANCHOR + d))
        out.append((f"dentro de {n} {unit}", ANCHOR + d))
    return out

def _week_cases():
    out = []
    for n in (1, 2, 3, 5, 10):
        d = timedelta(weeks=n)
        unit = "semanas" if n != 1 else "semana"
        out.append((f"hai {n} {unit}", ANCHOR - d))
        out.append((f"{n} {unit} atrás", ANCHOR - d))
        out.append((f"en {n} {unit}", ANCHOR + d))
        out.append((f"dentro de {n} {unit}", ANCHOR + d))
    return out

def _month_cases():
    out = []
    for n in (1, 2, 3, 5, 10):
        d = relativedelta(months=n)
        unit = "meses" if n != 1 else "mes"
        out.append((f"hai {n} {unit}", ANCHOR - d))
        out.append((f"{n} {unit} atrás", ANCHOR - d))
        out.append((f"en {n} {unit}", ANCHOR + d))
        out.append((f"dentro de {n} {unit}", ANCHOR + d))
    return out

def _year_cases():
    out = []
    for n in (1, 2, 3, 5, 10):
        d = relativedelta(years=n)
        unit = "anos" if n != 1 else "ano"
        out.append((f"hai {n} {unit}", ANCHOR - d))
        out.append((f"{n} {unit} atrás", ANCHOR - d))
        out.append((f"en {n} {unit}", ANCHOR + d))
        out.append((f"dentro de {n} {unit}", ANCHOR + d))
    return out


_SPELLED = [("hai dous días", 2), ("hai tres días", 3), ("hai cinco días", 5), ("hai dez días", 10), ("hai vinte días", 20)]


@pytest.mark.parametrize("text,n", _SPELLED)
def test_spelled_offsets(text, n):
    assert start(text) == ad(ANCHOR - timedelta(days=n))


@pytest.mark.parametrize("text,expected",
                         _day_cases() + _week_cases()
                         + _month_cases() + _year_cases())
def test_offsets(text, expected):
    assert start(text) == ad(expected)


@pytest.mark.parametrize("text,off", [("hoxe", 0), ("onte", -1), ("mañá", 1), ("antonte", -2)])
def test_named_days(text, off):
    exp = (ANCHOR + timedelta(days=off)).replace(hour=0, minute=0, second=0,
                                                 microsecond=0)
    assert start(text) == ad(exp)


def test_weekday_next():
    # próxima luns: the next occurrence of weekday 0 strictly after anchor
    ahead = ((0 - ANCHOR.weekday()) % 7) or 7
    exp = (ANCHOR + timedelta(days=ahead)).replace(hour=0, minute=0,
                                                   second=0, microsecond=0)
    assert start("próxima luns") == ad(exp)
