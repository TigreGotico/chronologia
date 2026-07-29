# -*- coding: utf-8 -*-
"""Oracle sweep: Basque relative offsets in both directions.

Preposed ``duela N UNIT`` is the past window ``[anchor - N, anchor - (N-1))``;
postposed ``N UNIT barru`` is the future window ``[anchor + N, anchor + (N+1))``.
Units: egun (day), aste (week), hilabete (month), urte (year), ordu (hour),
minutu (minute).  The N values here are disjoint from ``test_eu_relative`` to
avoid duplicates.  Gold is independent ``relativedelta`` arithmetic.
"""
import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start_end

UNIT = {
    "egun": relativedelta(days=1),
    "aste": relativedelta(weeks=1),
    "hilabete": relativedelta(months=1),
    "urte": relativedelta(years=1),
    "ordu": relativedelta(hours=1),
    "minutu": relativedelta(minutes=1),
}

NS = [1, 4, 6, 7, 8, 9, 11, 15]

PAST = [(f"duela {n} {u}", n, u) for u in UNIT for n in NS]
FUT = [(f"{n} {u} barru", n, u) for u in UNIT for n in NS]


@pytest.mark.parametrize("text,n,unit", PAST)
def test_past_offset(text, n, unit):
    d = UNIT[unit]
    s, e = start_end(text)
    assert s == ad(ANCHOR - n * d)
    assert e == ad(ANCHOR - (n - 1) * d)


@pytest.mark.parametrize("text,n,unit", FUT)
def test_future_offset(text, n, unit):
    d = UNIT[unit]
    s, e = start_end(text)
    assert s == ad(ANCHOR + n * d)
    assert e == ad(ANCHOR + (n + 1) * d)
