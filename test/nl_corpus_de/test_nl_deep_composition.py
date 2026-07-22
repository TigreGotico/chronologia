# -*- coding: utf-8 -*-
"""Tiefe Komposition (de): ein Versatz / eine Werktags-Zählung über eine
Referenz, die selbst zusammengesetzt ist -- der "n-te Wochentag des Monats"
("der erste Montag im März").  (Deutsch kennt kein ``ordlast``-Vokabular, daher
"letzte" nicht; hier ordinale Formen.)  Erwartungswerte aus vom Parser
unabhängiger Datumsarithmetik.
"""
import calendar
from datetime import datetime, timedelta

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate
from chronologia.civil_holidays import is_civil_holiday

from ._corpus import ANCHOR, parse, span

MON = 0


def nth_weekday(year, month, weekday, n):
    last = calendar.monthrange(year, month)[1]
    days = [d for d in range(1, last + 1)
            if datetime(year, month, d).weekday() == weekday]
    return datetime(year, month, days[n - 1])


def nth_business_day(base, n, jur):
    day = datetime(base.year, base.month, base.day)
    seen = 0
    while seen < n:
        day += timedelta(days=1)
        if day.weekday() >= 5:
            continue
        if jur and is_civil_holiday(day, jur, categories=("public",)):
            continue
        seen += 1
    return day


def test_tag_vor_dem_zweiten_montag_im_mai():
    ref = nth_weekday(ANCHOR.year, 5, MON, 2)
    expect = ref - timedelta(days=1)
    s = span('der Tag vor dem zweiten Montag im Mai')
    assert s.start == AstroDate(expect.year, expect.month, expect.day)
    assert parse('der Tag vor dem zweiten Montag im Mai')[1] == ""


def test_zwei_wochen_nach_dem_ersten_montag_im_maerz():
    ref = nth_weekday(ANCHOR.year, 3, MON, 1)
    expect = ref + timedelta(weeks=2)
    assert span('zwei Wochen nach dem ersten Montag im März'
                ).start == AstroDate(expect.year, expect.month, expect.day)


def test_fuenf_werktage_nach_weihnachten():
    expect = nth_business_day(datetime(ANCHOR.year, 12, 25), 5, "DE")
    r = extract_timespan('5 Werktage nach Weihnachten', "de", ANCHOR,
                         jurisdiction="DE")
    assert r is not None
    assert r[0].start == AstroDate(expect.year, expect.month, expect.day)
