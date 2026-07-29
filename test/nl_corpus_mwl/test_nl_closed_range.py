# -*- coding: utf-8 -*-
"""Closed date ranges in mwl via ``zde ... até ...`` (since ... until ...),
both endpoints given. Anchor 2017-06-27 13:04.

Only the ``zde <A> até <B>`` connector is attested to work end-to-end for
mwl; the elliptical Portuguese-style ``de <A> a <B>`` (no ``zde``/``até``
pairing) does NOT parse as a range for this locale -- it collapses onto the
last date fragment instead, so that phrasing is intentionally left untested
here (see gaps note in the PR)."""
from datetime import date
from chronologia.astrodate import AstroDate
from ._corpus import ANCHOR, start_end

_AD = ANCHOR.date()


def _fy(m, d):
    return 2017 if date(2017, m, d) >= _AD else 2018


def test_same_month_day_range():
    s, e = start_end("zde 10 de agosto até 15 de agosto")
    y = _fy(8, 10)
    assert s == AstroDate(y, 8, 10)
    assert e == AstroDate(y, 8, 16)


def test_same_month_day_range_with_year():
    s, e = start_end("zde 10 de agosto de 2020 até 15 de agosto de 2020")
    assert s == AstroDate(2020, 8, 10)
    assert e == AstroDate(2020, 8, 16)


def test_cross_month_day_range():
    s, e = start_end("zde 1 de janeiro até 28 de febreiro")
    y = _fy(1, 1)
    assert s == AstroDate(y, 1, 1)
    assert e == AstroDate(y, 3, 1)


def test_cross_year_boundary_day_range():
    s, e = start_end("zde 25 de dezembre até 1 de janeiro")
    y = _fy(12, 25)
    assert s == AstroDate(y, 12, 25)
    assert e == AstroDate(y + 1, 1, 2)


def test_same_day_range():
    s, e = start_end("zde 3 de márcio até 3 de márcio")
    y = _fy(3, 3)
    assert s == AstroDate(y, 3, 3)
    assert e == AstroDate(y, 3, 4)


def test_day_range_with_article():
    s, e = start_end("zde l 5 de júnio até l 9 de júnio")
    y = _fy(6, 5)
    assert s == AstroDate(y, 6, 5)
    assert e == AstroDate(y, 6, 10)


def test_year_range():
    s, e = start_end("zde 2010 até 2015")
    assert s == AstroDate(2010, 1, 1)
    assert e == AstroDate(2016, 1, 1)


def test_month_range_same_year():
    s, e = start_end("zde janeiro de 2019 até márcio de 2019")
    assert s == AstroDate(2019, 1, 1)
    assert e == AstroDate(2019, 4, 1)


def test_bare_month_range():
    s, e = start_end("zde janeiro até márcio")
    assert s == AstroDate(2017, 1, 1)
    assert e == AstroDate(2017, 4, 1)
