# -*- coding: utf-8 -*-
"""Second-pass sweep: calendar quarters and ISO weeks (bg), FRESH years
disjoint from test_nl_quarter.py and test_nl_iso_week.py.

Quarter N spans months [3N-2 .. 3N]. ISO weeks are Monday-based per the
standard, computed independently with ``date.fromisocalendar`` -- never the
parser.
"""
from datetime import date, timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end

_QUARTER_CASES = [
    ('2 тримесечие 2021', 2021, 4, 2021, 7),
    ('3 тримесечие 2022', 2022, 7, 2022, 10),
    ('Q4 2023', 2023, 10, 2024, 1),
    ('1 тримесечие 2027', 2027, 1, 2027, 4),
    ('Q2 2019', 2019, 4, 2019, 7),
    ('4 тримесечие 2021', 2021, 10, 2022, 1),
    ('Q1 2022', 2022, 1, 2022, 4),
    ('3 тримесечие 2025', 2025, 7, 2025, 10),
]


@pytest.mark.parametrize("text,sy,sm,ey,em", _QUARTER_CASES)
def test_quarter_resweep(text, sy, sm, ey, em):
    s, e = start_end(text)
    assert s == AstroDate(sy, sm, 1)
    assert e == AstroDate(ey, em, 1)


_ISO_CASES = [
    ('седмица 15 2021', 2021, 15),
    ('седмица 5 2022', 2022, 5),
    ('седмица 48 2023', 2023, 48),
    ('седмица 20 2025', 2025, 20),
    ('седмица 33 2019', 2019, 33),
    ('седмица 44 2020', 2020, 44),
    ('седмица 3 2028', 2028, 3),
]


@pytest.mark.parametrize("text,iy,iw", _ISO_CASES)
def test_iso_week_resweep(text, iy, iw):
    mon = date.fromisocalendar(iy, iw, 1)
    s, e = start_end(text)
    assert s == AstroDate(mon.year, mon.month, mon.day)
    nxt = mon + timedelta(days=7)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)
