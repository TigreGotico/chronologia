# -*- coding: utf-8 -*-
"""Composition profonde (fr) : un décalage / comptage de jours ouvrables sur
une référence elle-même composée -- le "énième jour de la semaine du mois"
("le dernier vendredi de novembre").  Valeurs attendues dérivées par
arithmétique de dates indépendante de l'analyseur.
"""
import calendar
from datetime import datetime, timedelta

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate
from chronologia.civil_holidays import is_civil_holiday

from ._corpus import ANCHOR, parse, span

MON, FRI = 0, 4


def nth_weekday(year, month, weekday, n):
    last = calendar.monthrange(year, month)[1]
    days = [d for d in range(1, last + 1)
            if datetime(year, month, d).weekday() == weekday]
    return datetime(year, month, days[n if n < 0 else n - 1])


def nth_business_day(base, n, sign, jur):
    day = datetime(base.year, base.month, base.day)
    step = timedelta(days=1 if sign > 0 else -1)
    seen = 0
    while seen < n:
        day += step
        if day.weekday() >= 5:
            continue
        if jur and is_civil_holiday(day, jur, categories=("public",)):
            continue
        seen += 1
    return day


def test_jour_avant_le_dernier_vendredi_de_novembre():
    ref = nth_weekday(ANCHOR.year, 11, FRI, -1)
    expect = ref - timedelta(days=1)
    s = span('le jour avant le dernier vendredi de novembre')
    assert s.start == AstroDate(expect.year, expect.month, expect.day)
    assert parse('le jour avant le dernier vendredi de novembre')[1] == ""


def test_deux_semaines_apres_le_premier_lundi_de_mars():
    ref = nth_weekday(ANCHOR.year, 3, MON, 1)
    expect = ref + timedelta(weeks=2)
    assert span('deux semaines après le premier lundi de mars'
                ).start == AstroDate(expect.year, expect.month, expect.day)


def test_trois_jours_ouvrables_apres_noel():
    expect = nth_business_day(datetime(ANCHOR.year, 12, 25), 3, 1, "FR")
    r = extract_timespan('3 jours ouvrables après noël', "fr", ANCHOR,
                         jurisdiction="FR")
    assert r is not None
    assert r[0].start == AstroDate(expect.year, expect.month, expect.day)
