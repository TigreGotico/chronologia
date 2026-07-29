# -*- coding: utf-8 -*-
"""Oracle sweep: fuzzy month-thirds ``awal / pertengahan / akhir Bulan YYYY``.

The month is split into three equal spans by total elapsed time; gold is
computed by independent arithmetic -- total = next_month_start - month_start,
boundaries at total/3 and 2*total/3 (exact to the hour for all month lengths).
Explicit year fixes the fold.
"""
from datetime import date, datetime, timedelta

import pytest

from ._corpus import AstroDate, start_end

MON = ("Januari Februari Maret April Mei Juni Juli Agustus September "
       "Oktober November Desember").split()


def _ad(dt):
    return AstroDate(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                     dt.second, dt.microsecond)


def _cases():
    out = []
    for y in (2019, 2020):
        for m in range(1, 13):
            ms = datetime(y, m, 1)
            nm_d = (date(y, m, 1) + timedelta(days=32)).replace(day=1)
            nm = datetime(nm_d.year, nm_d.month, 1)
            total = nm - ms
            b1 = ms + total / 3
            b2 = ms + 2 * total / 3
            mn = MON[m - 1]
            out.append((f"awal {mn} {y}", _ad(ms), _ad(b1)))
            out.append((f"pertengahan {mn} {y}", _ad(b1), _ad(b2)))
            out.append((f"akhir {mn} {y}", _ad(b2), _ad(nm)))
    return out


@pytest.mark.parametrize("text,s,e", _cases())
def test_month_third(text, s, e):
    assert start_end(text) == (s, e)
