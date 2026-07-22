"""Asturian relative phrases: "en N", "fai/hai N" (prefix past markers),
que-vien / pasau weekdays, named days."""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start, nomatch, span

_NW = {2: "dos", 3: "tres", 4: "cuatro", 5: "cinco", 6: "seis", 10: "diez"}


def _day_cases():
    out = []
    for n in (2, 3, 4, 5, 6, 10):
        out.append((f"fai {n} díes", ANCHOR - timedelta(days=n)))
        out.append((f"hai {n} díes", ANCHOR - timedelta(days=n)))
        out.append((f"en {n} díes", ANCHOR + timedelta(days=n)))
        out.append((f"fai {_NW[n]} díes", ANCHOR - timedelta(days=n)))
        out.append((f"en {_NW[n]} díes", ANCHOR + timedelta(days=n)))
    return out


def _other():
    out = []
    for n in (2, 3, 4):
        out.append((f"fai {n} selmanes", ANCHOR - timedelta(weeks=n)))
        out.append((f"en {n} selmanes", ANCHOR + timedelta(weeks=n)))
        out.append((f"fai {n} meses", ANCHOR - relativedelta(months=n)))
        out.append((f"en {n} meses", ANCHOR + relativedelta(months=n)))
        out.append((f"fai {n} años", ANCHOR - relativedelta(years=n)))
        out.append((f"en {n} años", ANCHOR + relativedelta(years=n)))
    return out


@pytest.mark.parametrize("text,expected", _day_cases() + _other())
def test_relative_offset(text, expected):
    assert start(text) == ad(expected)


@pytest.mark.parametrize("text,expected", [
    ("güei", ANCHOR.replace(hour=0, minute=0)),
    ("mañana", (ANCHOR + timedelta(days=1)).replace(hour=0, minute=0)),
    ("ayeri", (ANCHOR - timedelta(days=1)).replace(hour=0, minute=0)),
    ("trasmañana", (ANCHOR + timedelta(days=2)).replace(hour=0, minute=0)),
    ("pasáu mañana", (ANCHOR + timedelta(days=2)).replace(hour=0, minute=0)),
    ("antayeri", (ANCHOR - timedelta(days=2)).replace(hour=0, minute=0)),
])
def test_named_day(text, expected):
    assert start(text) == ad(expected)


_MID = ANCHOR.replace(hour=0, minute=0)


@pytest.mark.parametrize("text,expected", [
    ("martes que vien", _MID + timedelta(days=7)),
    ("miércoles que vien", _MID + timedelta(days=1)),
    ("vienres que vien", _MID + timedelta(days=3)),
    ("martes pasáu", _MID - timedelta(days=7)),
    ("sábadu pasáu", _MID - timedelta(days=3)),
])
def test_weekday_ref(text, expected):
    assert start(text) == ad(expected)


def test_widths():
    assert span("mañana").width == timedelta(days=1)
    assert span("en 2 selmanes").width == timedelta(weeks=1)


def test_adversarial():
    nomatch("")
    nomatch("hai muncho tiempu")   # marker without a numeric offset
