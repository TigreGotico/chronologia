# -*- coding: utf-8 -*-
"""Composição profunda (pt): um deslocamento / contagem de dias úteis sobre
uma referência que é ela própria composta -- um "enésimo dia-da-semana do mês"
("a última sexta-feira de novembro") ou um deslocamento aninhado.  Valores
esperados derivados por aritmética de datas independente do parser.
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


def test_dia_antes_da_ultima_sexta_de_novembro():
    ref = nth_weekday(ANCHOR.year, 11, FRI, -1)
    expect = ref - timedelta(days=1)
    s = span('o dia antes da última sexta-feira de novembro')
    assert s.start == AstroDate(expect.year, expect.month, expect.day)
    assert parse('o dia antes da última sexta-feira de novembro')[1] == ""


def test_duas_semanas_depois_da_primeira_segunda_de_marco():
    ref = nth_weekday(ANCHOR.year, 3, MON, 1)
    expect = ref + timedelta(weeks=2)
    assert span('duas semanas depois da primeira segunda-feira de março'
                ).start == AstroDate(expect.year, expect.month, expect.day)


def test_tres_dias_uteis_depois_do_natal():
    expect = nth_business_day(datetime(ANCHOR.year, 12, 25), 3, 1, "PT")
    r = extract_timespan('3 dias úteis depois do natal', "pt", ANCHOR,
                         jurisdiction="PT")
    assert r is not None
    assert r[0].start == AstroDate(expect.year, expect.month, expect.day)
