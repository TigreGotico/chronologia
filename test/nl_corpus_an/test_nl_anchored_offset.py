# -*- coding: utf-8 -*-
"""Anchored arithmetic (an): ``N <unit> dimpués/antis de <date>`` (signed unit
offset) and ``o <weekday> dimpués/antis de <date>`` (strict weekday roll) on a
resolved calendar-date reference.  Anchor 2018-06-05; the reference throughout
is ``o 15 de chinero de 2019`` = Tuesday 2019-01-15."""
from datetime import date, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import span, start, nomatch

REF = date(2019, 1, 15)
R = "o 15 de chinero de 2019"


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    (f"3 semanas dimpués de {R}", REF + timedelta(days=21)),
    (f"una semana dimpués de {R}", REF + timedelta(days=7)),
    (f"5 diyas antis de {R}", REF - timedelta(days=5)),
    (f"10 diyas dimpués de {R}", REF + timedelta(days=10)),
])
def test_unit_offset(text, expected):
    assert start(text) == _ad(expected)


@pytest.mark.parametrize("text,expected", [
    (f"o luns dimpués de {R}", date(2019, 1, 21)),
    (f"o viernes antis de {R}", date(2019, 1, 11)),
    (f"o miercres dimpués de {R}", date(2019, 1, 16)),
])
def test_weekday_roll(text, expected):
    assert start(text) == _ad(expected)


def test_week_offset_is_week_wide():
    assert span(f"3 semanas dimpués de {R}").width == timedelta(days=7)


def test_weekday_roll_is_day_wide():
    assert span(f"o luns dimpués de {R}").width == timedelta(days=1)


@pytest.mark.parametrize("text", ["antis d'a reunión", "o diya dimpués d'a boda"])
def test_no_reference_no_offset(text):
    nomatch(text)
