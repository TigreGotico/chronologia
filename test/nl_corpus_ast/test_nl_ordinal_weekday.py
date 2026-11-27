"""Ordinal weekday-of-month: ``el terceru llunes de marzu`` (issue #326).

Ordinals 1..5 (primeru..quintu) resolve for Asturian.  Without an explicit year the
month takes the year the month alone takes (ruling 1, which changed on
26 November 2026: it used to be the anchor year 2017 for every month; a month that
ended before the anchor, January to May, is now 2018; so is an occurrence in June that
ended before the anchor, 2017-06-27 13:04); a trailing ``de <year>`` pins it.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import start_end, ad, ANCHOR
from ._gen import MON, ORD, WD, nth_weekday


def _bare_cases():
    out = []
    for m in range(1, 13):
        for w, wn in WD.items():
            for n, on in ORD.items():
                # ruling 1: a part of a month takes its month's year
                y = ANCHOR.year + (m < ANCHOR.month)
                d = nth_weekday(y, m, w, n)
                if m == ANCHOR.month and d is not None \
                        and datetime(d.year, d.month, d.day) + timedelta(days=1) <= ANCHOR:
                    # ruling 1 (26 November 2026): a part of a month is read as a
                    # span; a weekday of June 2017 before the anchor has ended,
                    # so it is that weekday of June 2018 (weekdays recomputed)
                    d = nth_weekday(y + 1, m, w, n)
                if d is None:
                    continue
                out.append((f"el {on} {wn} de {MON[m]}", datetime(d.year, d.month, d.day)))
    return out


@pytest.mark.parametrize("text,expected", _bare_cases())
def test_ordinal_weekday_next_occurrence(text, expected):
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
