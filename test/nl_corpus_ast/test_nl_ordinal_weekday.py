"""Ordinal weekday-of-month: ``el terceru llunes de marzu`` (issue #326).

Ordinals 1..5 (primeru..quintu) resolve for Asturian.  Without an explicit year the
month resolves inside the anchor year 2017; a trailing ``de <year>`` pins it.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import start_end, ad
from ._gen import MON, ORD, WD, nth_weekday


def _bare_cases():
    out = []
    for m in range(1, 13):
        for w, wn in WD.items():
            for n, on in ORD.items():
                d = nth_weekday(2017, m, w, n)
                if d is None:
                    continue
                out.append((f"el {on} {wn} de {MON[m]}", datetime(d.year, d.month, d.day)))
    return out


@pytest.mark.parametrize("text,expected", _bare_cases())
def test_ordinal_weekday_anchor_year(text, expected):
    s, e = start_end(text)
    assert s == ad(expected)
    assert e - s == timedelta(days=1)


def _year_cases():
    out = []
    for y in (2018, 2019, 2020, 2024, 2025):
        for m in (3, 6, 11):
            for w, wn in WD.items():
                for n, on in ORD.items():
                    d = nth_weekday(y, m, w, n)
                    if d is None:
                        continue
                    out.append((f"el {on} {wn} de {MON[m]} de {y}",
                                datetime(d.year, d.month, d.day)))
    return out


@pytest.mark.parametrize("text,expected", _year_cases())
def test_ordinal_weekday_explicit_year(text, expected):
    s, e = start_end(text)
    assert s == ad(expected)
    assert e - s == timedelta(days=1)
