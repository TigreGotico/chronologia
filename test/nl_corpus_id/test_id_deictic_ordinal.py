# -*- coding: utf-8 -*-
"""Indonesian ordinal-weekday word order and deictic daypart selection.

Idiomatic native sentences are the tests; every gold is computed by INDEPENDENT
arithmetic (``calendar`` for the Nth weekday of a month; ``daypart_span`` -- the
CLDR band primitive, not the extractor -- for the time-of-day band), never read
back from the parser under test.

Indonesian orders an ordinal-weekday-of-month as WEEKDAY + ORDINAL + MONTH
(+ optional YEAR): "Senin ketiga Maret 2019" = the third Monday of March 2019 --
unlike the Romance "ORD WEEKDAY of MONTH". The deictic dayparts "tadi <band>"
(nearest PAST occurrence) and "nanti <band>" (nearest FUTURE occurrence) land on
a day that depends on whether today's band edge has passed the anchor.
Anchor: Tuesday 2017-06-27 13:04.
"""
import calendar
from datetime import date, datetime

import pytest

from chronologia import daypart_span
from chronologia.astrodate import AstroDate
from ._corpus import parse, span

A = datetime(2017, 6, 27, 13, 4)

# Monday=0 .. Sunday=6, matching datetime.weekday().
_WD = {"Senin": 0, "Selasa": 1, "Rabu": 2, "Kamis": 3,
       "Jumat": 4, "Sabtu": 5, "Ahad": 6, "Minggu": 6}
_ORD = {"pertama": 1, "kesatu": 1, "kedua": 2, "ketiga": 3,
        "keempat": 4, "kelima": 5}
_MONTH = {"Januari": 1, "Maret": 3, "Juni": 6, "Agustus": 8, "Desember": 12}


def _nth_weekday(year, month, weekday, n):
    """Day-of-month of the Nth ``weekday`` (Mon=0) in ``year``/``month``,
    computed independently of the parser via the standard-library calendar."""
    days = [d for d in range(1, calendar.monthrange(year, month)[1] + 1)
            if date(year, month, d).weekday() == weekday]
    return days[n - 1]


@pytest.mark.parametrize("weekday,ordinal,month,year", [
    ("Senin", "ketiga", "Maret", 2019),     # third Monday of March 2019
    ("Jumat", "kedua", "Agustus", 2020),     # second Friday of August 2020
    ("Rabu", "pertama", "Januari", 2021),    # first Wednesday of January 2021
    ("Senin", "keempat", "Juni", 2022),      # fourth Monday of June 2022
    ("Ahad", "kedua", "Desember", 2020),     # second Sunday of December 2020
])
def test_ordinal_weekday_of_month_with_year(weekday, ordinal, month, year):
    from datetime import timedelta
    dom = _nth_weekday(year, _MONTH[month], _WD[weekday], _ORD[ordinal])
    got = span(f"{weekday} {ordinal} {month} {year}", A)
    day = date(year, _MONTH[month], dom)
    assert got.start == AstroDate(day.year, day.month, day.day)
    nxt = day + timedelta(days=1)
    assert got.end == AstroDate(nxt.year, nxt.month, nxt.day)


@pytest.mark.parametrize("weekday,ordinal,month", [
    ("Selasa", "kedua", "Desember"),         # second Tuesday, anchor year 2017
    ("Kamis", "ketiga", "Juni"),             # third Thursday, anchor year 2017
])
def test_ordinal_weekday_of_month_bare_year(weekday, ordinal, month):
    year = A.year
    dom = _nth_weekday(year, _MONTH[month], _WD[weekday], _ORD[ordinal])
    got = span(f"{weekday} {ordinal} {month}", A)
    assert got.start == AstroDate(year, _MONTH[month], dom)


def _band(day, name):
    s = daypart_span(AstroDate(day.year, day.month, day.day), name)
    return s.start, s.end


# (phrase, civil day of the band, band key) -- gold from daypart_span.
_DEICTIC = [
    ("pagi ini", date(2017, 6, 27), "morning_id"),    # this morning -> today
    ("tadi pagi", date(2017, 6, 27), "morning_id"),   # nearest past morning: today
    ("tadi malam", date(2017, 6, 26), "night_id"),    # nearest past night: yesterday
    ("nanti malam", date(2017, 6, 27), "night_id"),   # nearest future night: tonight
    ("nanti pagi", date(2017, 6, 28), "morning_id"),  # nearest future morning: tomorrow
]


@pytest.mark.parametrize("text,day,band_key", _DEICTIC)
def test_deictic_daypart_band(text, day, band_key):
    start, end = _band(day, band_key)
    got = span(text, A)
    assert (got.start, got.end) == (start, end)


@pytest.mark.parametrize("text", [p[0] for p in _DEICTIC])
def test_deictic_daypart_fully_consumed(text):
    r = parse(text, A)
    assert r is not None and r[1].strip() == "", f"stranded residue {r[1]!r}"
