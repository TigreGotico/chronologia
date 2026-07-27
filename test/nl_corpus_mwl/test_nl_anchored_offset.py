# -*- coding: utf-8 -*-
"""Anchored arithmetic (mwl): ``N <unit> apuis/antes de <date>`` (signed unit
offset) and ``l <weekday> apuis/antes de <date>`` (strict weekday roll) on a
resolved calendar-date reference.  Anchor 2017-06-27; the reference throughout
is ``l 15 de janeiro de 2018`` = Monday 2018-01-15."""
from datetime import date, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import span, start, nomatch

REF = date(2018, 1, 15)
R = "l 15 de janeiro de 2018"


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    (f"3 sumanas apuis de {R}", REF + timedelta(days=21)),
    (f"ua sumana apuis de {R}", REF + timedelta(days=7)),
    (f"5 dies antes de {R}", REF - timedelta(days=5)),
    (f"10 dies apuis de {R}", REF + timedelta(days=10)),
])
def test_unit_offset(text, expected):
    assert start(text) == _ad(expected)


@pytest.mark.parametrize("text,expected", [
    (f"l segunda feira apuis de {R}", date(2018, 1, 22)),
    (f"la sesta feira antes de {R}", date(2018, 1, 12)),
    (f"la quinta feira apuis de {R}", date(2018, 1, 18)),
])
def test_weekday_roll(text, expected):
    assert start(text) == _ad(expected)


# an offset resolves to the single shifted day, not a period-wide span:
# the offset amount is the SHIFT, never the result width (was days=7,
# a silent-wrong -- see en test_nl_anchored_offset_point).
def test_week_offset_is_day_wide():
    assert span(f"3 sumanas apuis de {R}").width == timedelta(days=1)


def test_weekday_roll_is_day_wide():
    assert span(f"l segunda feira apuis de {R}").width == timedelta(days=1)


@pytest.mark.parametrize("text", ["antes de la reunion", "l die apuis de la boda"])
def test_no_reference_no_offset(text):
    nomatch(text)
