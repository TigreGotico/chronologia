# -*- coding: utf-8 -*-
"""R120, Spanish: "la semana después/antes de <evento>" resolves as a WEEK
span, not a single day -- mirrors ``test_nl_corpus_en/test_nl_r120_week_after_event.py``.

The bare, DEFINITE "la semana" (no explicit count) names the calendar week
itself, same grain as "the week of X"; a counted/indefinite "una semana" or
"2 semanas" stays a plain arithmetic point offset, unaffected.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, span, start_end


def ad(d):
    return AstroDate(d.year, d.month, d.day)

PASCUA = date(2018, 4, 1)      # domingo
NAVIDAD = date(2017, 12, 25)   # lunes


def _week_of(d):
    back = (d.weekday() - 0) % 7
    s = d - timedelta(days=back)
    return s, s + timedelta(days=7)


@pytest.mark.parametrize("text,shifted", [
    ("la semana después de pascua", PASCUA + timedelta(days=7)),
    ("la semana antes de navidad", NAVIDAD - timedelta(days=7)),
])
def test_la_semana_despues_antes_is_week_wide(text, shifted):
    exp_start, exp_end = _week_of(shifted)
    s, e = start_end(text)
    assert (s, e) == (ad(exp_start), ad(exp_end))
    assert span(text).width == timedelta(days=7)


# -- CONTROL: counted/indefinite "semana" stays a single-day point --------

@pytest.mark.parametrize("text,expected", [
    ("dos semanas después de pascua", PASCUA + timedelta(days=14)),
    ("una semana después de pascua", PASCUA + timedelta(days=7)),
    ("1 semana después de pascua", PASCUA + timedelta(days=7)),
])
def test_counted_or_indefinite_semana_stays_a_point(text, expected):
    s, e = start_end(text)
    assert s == ad(expected)
    assert e == ad(expected + timedelta(days=1))
    assert span(text).width == timedelta(days=1)


# -- CONTROL: "el día después/antes de X" is unaffected -------------------

@pytest.mark.parametrize("text,expected", [
    ("el día después de pascua", PASCUA + timedelta(days=1)),
    ("el día antes de navidad", NAVIDAD - timedelta(days=1)),
])
def test_el_dia_despues_antes_stays_a_point(text, expected):
    s, e = start_end(text)
    assert s == ad(expected)
    assert span(text).width == timedelta(days=1)
