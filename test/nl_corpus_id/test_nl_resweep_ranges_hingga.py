# -*- coding: utf-8 -*-
"""Second-pass sweep: closed day ranges phrased with ``hingga`` ("until"/"to"),
the register-neutral synonym of ``sampai`` used by ``test_sweep_ranges.py``.
Both the bare ``d1 hingga d2 Bulan YYYY`` and the ``dari ... hingga ...``
phrasing are exercised. Gold is the same closed-day-range identity as the
``sampai`` sweep -- [d1 00:00, (d2+1) 00:00) -- computed by independent
arithmetic, never from the parser.

Years (2021, 2023, 2025) avoid every year already used by
``test_sweep_ranges.py`` (2019, 2020). Anchor fixed but irrelevant given
explicit years, per the existing range-sweep convention.
"""
from datetime import date, datetime, timedelta

import pytest

from ._corpus import AstroDate, start_end

A = datetime(2017, 6, 27, 13, 4)

MON = ("Januari Februari Maret April Mei Juni Juli Agustus September "
       "Oktober November Desember").split()

_YEARS = (2021, 2023, 2025)


def _cases():
    out = []
    for y in _YEARS:
        for m in range(1, 13):
            mn = MON[m - 1]
            for d1, d2, tmpl in ((3, 10, "dari {d1} hingga {d2} {mn} {y}"),
                                 (7, 18, "{d1} hingga {d2} {mn} {y}")):
                text = tmpl.format(d1=d1, d2=d2, mn=mn, y=y)
                end = date(y, m, d2) + timedelta(days=1)
                out.append((text, AstroDate(y, m, d1),
                            AstroDate(end.year, end.month, end.day)))
    return out


@pytest.mark.parametrize("text,s,e", _cases())
def test_closed_day_range_hingga(text, s, e):
    assert start_end(text, A) == (s, e)
