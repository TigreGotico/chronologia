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
        unit = "dies" if n != 1 else "dia"
        out.append((f"fa {n} {unit}", ANCHOR - d))
        out.append((f"{n} {unit} enrere", ANCHOR - d))
        out.append((f"en {n} {unit}", ANCHOR + d))
        out.append((f"dins de {n} {unit}", ANCHOR + d))
    return out

def _week_cases():
    out = []
    for n in (1, 2, 3, 5, 10):
        d = timedelta(weeks=n)
        unit = "setmanes" if n != 1 else "setmana"
        out.append((f"fa {n} {unit}", ANCHOR - d))
        out.append((f"{n} {unit} enrere", ANCHOR - d))
        out.append((f"en {n} {unit}", ANCHOR + d))
        out.append((f"dins de {n} {unit}", ANCHOR + d))
    return out

def _month_cases():
    out = []
    for n in (1, 2, 3, 5, 10):
        d = relativedelta(months=n)
        unit = "mesos" if n != 1 else "mes"
        out.append((f"fa {n} {unit}", ANCHOR - d))
        out.append((f"{n} {unit} enrere", ANCHOR - d))
        out.append((f"en {n} {unit}", ANCHOR + d))
        out.append((f"dins de {n} {unit}", ANCHOR + d))
    return out

def _year_cases():
    out = []
    for n in (1, 2, 3, 5, 10):
        d = relativedelta(years=n)
        unit = "anys" if n != 1 else "any"
        out.append((f"fa {n} {unit}", ANCHOR - d))
        out.append((f"{n} {unit} enrere", ANCHOR - d))
        out.append((f"en {n} {unit}", ANCHOR + d))
        out.append((f"dins de {n} {unit}", ANCHOR + d))
    return out


_SPELLED = [("fa dos dies", 2), ("fa tres dies", 3), ("fa cinc dies", 5), ("fa deu dies", 10), ("fa vint dies", 20)]


@pytest.mark.parametrize("text,n", _SPELLED)
def test_spelled_offsets(text, n):
    assert start(text) == ad(ANCHOR - timedelta(days=n))


@pytest.mark.parametrize("text,expected",
                         _day_cases() + _week_cases()
                         + _month_cases() + _year_cases())
def test_offsets(text, expected):
    assert start(text) == ad(expected)


@pytest.mark.parametrize("text,off", [("avui", 0), ("ahir", -1), ("demà", 1)])
def test_named_days(text, off):
    exp = (ANCHOR + timedelta(days=off)).replace(hour=0, minute=0, second=0,
                                                 microsecond=0)
    assert start(text) == ad(exp)


def test_weekday_next():
    # pròxim dilluns: the next occurrence of weekday 0 strictly after anchor
    ahead = ((0 - ANCHOR.weekday()) % 7) or 7
    exp = (ANCHOR + timedelta(days=ahead)).replace(hour=0, minute=0,
                                                   second=0, microsecond=0)
    assert start("pròxim dilluns") == ad(exp)


# --- postfix "last <weekday>" idiom regression (bug: flipped to next) ---
from datetime import datetime as _dt  # noqa: E402
from ._corpus import parse as _parse  # noqa: E402

_FRI = _dt(2026, 7, 24, 12, 0)  # anchor: Friday

@pytest.mark.parametrize("text,y,m,d", [
    ("dimarts passat", 2026, 7, 21),      # postfix last
    ("proxim dimarts", 2026, 7, 28),      # prefix next
    ("dimarts que ve", 2026, 7, 28),      # postfix next
    ("dimarts", 2026, 7, 28),             # bare weekday -> next
    ("setmana passada", 2026, 7, 13),     # unit noun, unaffected
])
def test_weekday_postfix_idiom(text, y, m, d):
    assert start(text, _FRI) == ad(_dt(y, m, d))

@pytest.mark.parametrize("text", ["dimarts passat", "dimarts que ve"])
def test_weekday_postfix_marker_consumed(text):
    assert _parse(text, _FRI).remainder == ""
