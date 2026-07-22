"""Occitan relative phrases: "dins N", "fa N" (prefix past marker),
que-ven / passat weekdays, named days."""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start, nomatch, span

_NW = {2: "dos", 3: "tres", 4: "quatre", 5: "cinc", 6: "sièis", 10: "dètz"}


def _day_cases():
    out = []
    for n in (2, 3, 4, 5, 6, 10):
        out.append((f"fa {n} jorns", ANCHOR - timedelta(days=n)))
        out.append((f"dins {n} jorns", ANCHOR + timedelta(days=n)))
        out.append((f"fa {_NW[n]} jorns", ANCHOR - timedelta(days=n)))
        out.append((f"dins {_NW[n]} jorns", ANCHOR + timedelta(days=n)))
    return out


def _other():
    out = []
    for n in (2, 3, 4):
        out.append((f"fa {n} setmanas", ANCHOR - timedelta(weeks=n)))
        out.append((f"dins {n} setmanas", ANCHOR + timedelta(weeks=n)))
        out.append((f"fa {n} meses", ANCHOR - relativedelta(months=n)))
        out.append((f"dins {n} meses", ANCHOR + relativedelta(months=n)))
        out.append((f"fa {n} ans", ANCHOR - relativedelta(years=n)))
        out.append((f"dins {n} ans", ANCHOR + relativedelta(years=n)))
    return out


@pytest.mark.parametrize("text,expected", _day_cases() + _other())
def test_relative_offset(text, expected):
    assert start(text) == ad(expected)


@pytest.mark.parametrize("text,expected", [
    ("uèi", ANCHOR.replace(hour=0, minute=0)),
    ("deman", (ANCHOR + timedelta(days=1)).replace(hour=0, minute=0)),
    ("ièr", (ANCHOR - timedelta(days=1)).replace(hour=0, minute=0)),
    ("passat deman", (ANCHOR + timedelta(days=2)).replace(hour=0, minute=0)),
    ("abans ièr", (ANCHOR - timedelta(days=2)).replace(hour=0, minute=0)),
])
def test_named_day(text, expected):
    assert start(text) == ad(expected)


_MID = ANCHOR.replace(hour=0, minute=0)


@pytest.mark.parametrize("text,expected", [
    ("diluns que ven", _MID + timedelta(days=6)),
    ("dimècres que ven", _MID + timedelta(days=1)),
    ("divendres que ven", _MID + timedelta(days=3)),
    ("dimars passat", _MID - timedelta(days=7)),
    ("dissabte passat", _MID - timedelta(days=3)),
])
def test_weekday_ref(text, expected):
    assert start(text) == ad(expected)


def test_widths():
    assert span("deman").width == timedelta(days=1)
    assert span("dins 2 setmanas").width == timedelta(weeks=1)


def test_adversarial():
    nomatch("")
    nomatch("fa pauc")   # marker without a numeric offset
