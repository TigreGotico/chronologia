# -*- coding: utf-8 -*-
"""Oracle sweep: explicit-year Basque calendar dates.

Canonical big-endian order ``YEARko MONTHgen DAYa`` ("2020ko martxoaren 8a").
The absolutive day suffix -a is used uniformly; the number-fold strips it.  A
full date is a single day: ``[date, date+1day)``.  Expected values come from
independent ``datetime`` arithmetic -- the parser is never consulted for gold.
"""
from calendar import monthrange
from datetime import datetime, timedelta

import pytest

from ._corpus import ad, start, start_end
from ._sweep import MONTH_GEN

# historically-flavoured years spanning several centuries
YEARS = [1789, 1936, 1969, 2001, 2024]


def _cases():
    out = []
    for y in YEARS:
        for mo in range(1, 13):
            last = monthrange(y, mo)[1]
            for d in (1, 9, 17, 25, last):
                out.append((f"{y}ko {MONTH_GEN[mo]} {d}a", y, mo, d))
    # de-dup (25 may coincide with `last` in Feb) preserving order
    seen, uniq = set(), []
    for c in out:
        if c[0] not in seen:
            seen.add(c[0])
            uniq.append(c)
    return uniq


CASES = _cases()


@pytest.mark.parametrize("text,y,mo,d", CASES)
def test_full_date_start(text, y, mo, d):
    assert start(text) == ad(datetime(y, mo, d))


@pytest.mark.parametrize("text,y,mo,d", CASES)
def test_full_date_span_one_day(text, y, mo, d):
    s, e = start_end(text)
    assert s == ad(datetime(y, mo, d))
    assert e == ad(datetime(y, mo, d) + timedelta(days=1))
