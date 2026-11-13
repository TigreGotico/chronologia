# -*- coding: utf-8 -*-
""""desde a páscoa" abre na Páscoa mais recente, na sua própria data.

A holiday computed per year falls on another day each year, so "desde" and a
range pulled back a year read that year's own date of the holiday.

Easter comes from ``dateutil.easter`` (the Gregorian computus): 20 April 2025
and 5 April 2026.  Pentecost is Easter plus 49 days, and Carnival Tuesday is
Easter minus 47 days.

The article before the holiday name ("a", "o") stays in the remainder; that
is a separate defect, so these rows pin the span only.
"""
from datetime import datetime, timedelta

import pytest
from dateutil.easter import easter

from ._corpus import ad, parse

JUN20 = datetime(2026, 6, 20, 12, 0)
MAR01 = datetime(2026, 3, 1, 12, 0)


def _day(d):
    return datetime(d.year, d.month, d.day)


EASTER_2025 = _day(easter(2025))
EASTER_2026 = _day(easter(2026))


@pytest.mark.parametrize("text,anchor,expected", [
    ("desde a páscoa", JUN20, EASTER_2026),
    ("desde a páscoa", MAR01, EASTER_2025),
    ("desde páscoa", JUN20, EASTER_2026),
    ("desde o pentecostes", JUN20, EASTER_2026 + timedelta(days=49)),
    ("desde o carnaval", JUN20, EASTER_2026 - timedelta(days=47)),
])
def test_desde_festa_movel_na_propria_data(text, anchor, expected):
    r = parse(text, anchor)
    assert r is not None, f"{text!r} did not parse"
    assert (r.span.start, r.span.end) == (ad(expected), ad(anchor))


@pytest.mark.parametrize("anchor", [JUN20, MAR01])
def test_desde_o_inverno(anchor):
    # chronologia reads the meteorological winter, 1 December to 1 March
    r = parse("desde o inverno", anchor)
    assert r is not None
    assert (r.span.start, r.span.end) == (ad(datetime(2025, 12, 1)),
                                          ad(anchor))
    assert r.remainder == ""


def test_da_semana_que_vem_nao_recua_um_ano():
    # Thursday 2026-12-31: "a semana que vem" is 4 to 11 January 2027, after
    # the right end, so no range is read and the words stay.
    r = parse("da semana que vem até 31 de dezembro",
              datetime(2026, 12, 31, 12, 0))
    assert r is not None
    assert (r.span.start, r.span.end) == (ad(datetime(2027, 1, 4)),
                                          ad(datetime(2027, 1, 11)))
    assert r.remainder != ""


def test_desde_a_pascoa_ate_hoje():
    r = parse("desde a páscoa até hoje", JUN20)
    assert r is not None
    assert (r.span.start, r.span.end) == (ad(EASTER_2026),
                                          ad(datetime(2026, 6, 21)))
