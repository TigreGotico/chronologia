# -*- coding: utf-8 -*-
"""Persian seasons and بین/میان "between" ranges.

Meteorological seasons, N-hemisphere as the engine models Persian (matching
the ar corpus): بهار=MAM, تابستان=JJA, پاییز=SON, زمستان=DJF (December of the
named year through the following March).  Gold by independent arithmetic,
never read back from the parser.
"""
from datetime import date

import pytest

from ._corpus import AstroDate, start_end

# season -> (start month, end-exclusive (year_offset, month))
SEASONS = {
    "بهار": (3, (0, 6)),
    "تابستان": (6, (0, 9)),
    "پاییز": (9, (0, 12)),
    "پائیز": (9, (0, 12)),
    "زمستان": (12, (1, 3)),
}


def _year_cases():
    out = []
    for name, (sm, (yo, em)) in SEASONS.items():
        for y in (2018, 2019, 2020, 2021):
            s = date(y, sm, 1)
            e = date(y + yo, em, 1)
            out.append((f"{name} {y}", s, e))
    return out


@pytest.mark.parametrize("text,s,e", _year_cases())
def test_season_year(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(s.year, s.month, s.day)
    assert ee == AstroDate(e.year, e.month, e.day)


def test_next_summer():
    # ANCHOR (2017-06-27) already sits inside JJA 2017, so "next summer" is
    # the following year's summer.
    ss, ee = start_end("تابستان آینده")
    assert ss == AstroDate(2018, 6, 1)
    assert ee == AstroDate(2018, 9, 1)


def test_last_spring():
    # ANCHOR (2017-06-27) sits after MAM 2017 closes, so "last spring" is the
    # season just past, in the anchor year itself.
    ss, ee = start_end("بهار گذشته")
    assert ss == AstroDate(2017, 3, 1)
    assert ee == AstroDate(2017, 6, 1)


def test_last_winter_crosses_year():
    ss, ee = start_end("زمستان گذشته")
    assert ss == AstroDate(2016, 12, 1)
    assert ee == AstroDate(2017, 3, 1)


@pytest.mark.parametrize("text,s,e", [
    ("بین 2010 و 2020", AstroDate(2010, 1, 1), AstroDate(2021, 1, 1)),
    ("میان 2010 و 2020", AstroDate(2010, 1, 1), AstroDate(2021, 1, 1)),
    ("بین 1990 و 2000", AstroDate(1990, 1, 1), AstroDate(2001, 1, 1)),
])
def test_between_years(text, s, e):
    ss, ee = start_end(text)
    assert ss == s
    assert ee == e


def test_between_years_no_remainder():
    from ._corpus import parse
    r = parse("بین 2010 و 2020")
    assert r is not None
    assert r[1] == ""


def test_between_seasons():
    ss, ee = start_end("بین بهار و تابستان")
    assert ss == AstroDate(2017, 3, 1)
    assert ee == AstroDate(2017, 9, 1)


def test_bare_season_no_year_uses_anchor_year():
    ss, ee = start_end("بهار")
    assert ss == AstroDate(2017, 3, 1)
    assert ee == AstroDate(2017, 6, 1)


def test_between_requires_and_conjunction():
    # "بین 2010" alone, with no "و <B>" pairing, is not a range: the bare
    # year still resolves on its own, with "بین" left unconsumed.
    from ._corpus import parse
    r = parse("بین 2010")
    assert r is not None
    assert r[0].start == AstroDate(2010, 1, 1)
    assert r[1] == "بین"
