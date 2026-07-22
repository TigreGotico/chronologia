# -*- coding: utf-8 -*-
"""Composición profunda (es): un desplazamiento / recuento de días hábiles
sobre una referencia que es a su vez compuesta -- el "enésimo día de la semana
del mes" ("el último viernes de noviembre").  Valores esperados derivados por
aritmética de fechas independiente del parser.
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


def test_dia_antes_del_ultimo_viernes_de_noviembre():
    ref = nth_weekday(ANCHOR.year, 11, FRI, -1)
    expect = ref - timedelta(days=1)
    s = span('el día antes del último viernes de noviembre')
    assert s.start == AstroDate(expect.year, expect.month, expect.day)
    assert parse('el día antes del último viernes de noviembre')[1] == ""


def test_dos_semanas_despues_del_primer_lunes_de_marzo():
    ref = nth_weekday(ANCHOR.year, 3, MON, 1)
    expect = ref + timedelta(weeks=2)
    assert span('dos semanas después del primer lunes de marzo'
                ).start == AstroDate(expect.year, expect.month, expect.day)


def test_tres_dias_habiles_despues_de_la_navidad():
    expect = nth_business_day(datetime(ANCHOR.year, 12, 25), 3, 1, "ES")
    r = extract_timespan('3 días hábiles después de la navidad', "es", ANCHOR,
                         jurisdiction="ES")
    assert r is not None
    assert r[0].start == AstroDate(expect.year, expect.month, expect.day)
