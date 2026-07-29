# -*- coding: utf-8 -*-
"""Second-pass Catalan holiday sweep -- fresh years, not overlapping the
hand-written cases in ``test_nl_holiday_ref.py`` (which anchors 2017 and
touches only 2016/2017/2018/2020/2026 explicitly).

Anchor is always <year>-06-27 13:04 (Tuesday-shaped like the mission anchor,
but with a swept year), so bare-holiday resolution is pure "next occurrence
on/after 27 June of that year":

* Jan 1 (cap d'any), Jan 6 (reis), May 1 (festa del treball -- see xfail),
  Jun 24 (sant joan -- see xfail) already fell before 27 June -> next hit is
  year+1.
* Sep 11 (diada nacional -- see xfail), Nov 1 (tots sants), Dec 25 (nadal),
  Dec 26 (sant esteve) are still ahead -> next hit is the same year.

Movable feasts (Divendres Sant, Pasqua, Pasqua Granada/Pentecosta) are always
before June, so they too resolve to year+1.  Easter is computed here with the
standard Gauss/anonymous Gregorian algorithm -- independent of the parser,
verified against a published reference table (2016/17/18/20/21/22/23/24/25/26)
before being trusted for the swept years.

``festa del treball`` (Labour Day), ``sant joan`` and ``diada nacional`` do
NOT resolve in this engine: the underlying es.tab entries either carry no
Catalan alias (Fiesta del Trabajo / San Juan) or are decree-only for a narrow
2023-2027 window (Diada Nacional de Catalunya), so they return no span at
every anchor probed here.  Kept as strict xfails with the historically/
astronomically correct gold, per policy -- never a fabricated "matching"
gold.
"""
from datetime import date, timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, parse, span, start, nomatch  # noqa: F401

# fresh years -- disjoint from 2016/2017/2018/2020/2026 used upstream.
_YEARS = [2019, 2021, 2023, 2024, 2025, 2027, 2028, 2029, 2030, 2031,
          2032, 2033, 2034, 2035, 2036, 2037, 2038, 2039, 2040, 2041]


def _easter(year):
    """Anonymous Gregorian (Gauss) algorithm -- independent of the parser."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    ell = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * ell) // 451
    month = (h + ell - 7 * m + 114) // 31
    day = ((h + ell - 7 * m + 114) % 31) + 1
    return date(year, month, day)


# sanity-check the independent Easter arithmetic against a published table
# before trusting it for the swept years below.
_EASTER_REFERENCE = {
    2016: (3, 27), 2017: (4, 16), 2018: (4, 1), 2020: (4, 12),
    2021: (4, 4), 2022: (4, 17), 2023: (4, 9), 2024: (3, 31),
    2025: (4, 20), 2026: (4, 5),
}
for _y, (_m, _d) in _EASTER_REFERENCE.items():
    assert _easter(_y) == date(_y, _m, _d), "Easter arithmetic disagrees with reference table"


def _anchor(year):
    return date(year, 6, 27)


def _next_fixed(year, month, day):
    d = date(year, month, day)
    a = _anchor(year)
    return d if d >= a else date(year + 1, month, day)


def _next_movable(year, offset_from_easter):
    a = _anchor(year)
    d = _easter(year) + timedelta(days=offset_from_easter)
    if d >= a:
        return d
    return _easter(year + 1) + timedelta(days=offset_from_easter)


# ---------------------------------------------------------------------------
# fixed-date holidays that DO resolve in this engine.
# ---------------------------------------------------------------------------

_FIXED = [
    ("cap d'any", 1, 1),
    ("reis", 1, 6),
    ("tots sants", 11, 1),
    ("nadal", 12, 25),
    ("sant esteve", 12, 26),
]


def _fixed_cases():
    out = []
    for y in _YEARS:
        for text, mo, da in _FIXED:
            gold = _next_fixed(y, mo, da)
            out.append((text, y, gold))
    return out


_FIXED_CASES = _fixed_cases()


@pytest.mark.parametrize(
    "text,year,gold", _FIXED_CASES,
    ids=["%s@%d" % (t, y) for t, y, _ in _FIXED_CASES],
)
def test_fixed_holiday_fresh_years(text, year, gold):
    anchor = date(year, 6, 27)
    from datetime import datetime as _dt
    a = _dt(anchor.year, anchor.month, anchor.day, 13, 4)
    assert start(text, a) == AstroDate(gold.year, gold.month, gold.day)
    assert span(text, a).width == timedelta(days=1)


# ---------------------------------------------------------------------------
# movable feasts (Easter-relative) that DO resolve.
# ---------------------------------------------------------------------------

_MOVABLE = [
    ("divendres sant", -2),
    ("pasqua", 0),
    ("pasqua granada", 49),
    ("pentecosta", 49),
]


def _movable_cases():
    out = []
    for y in _YEARS:
        for text, off in _MOVABLE:
            gold = _next_movable(y, off)
            out.append((text, y, gold))
    return out


_MOVABLE_CASES = _movable_cases()


@pytest.mark.parametrize(
    "text,year,gold", _MOVABLE_CASES,
    ids=["%s@%d" % (t, y) for t, y, _ in _MOVABLE_CASES],
)
def test_movable_holiday_fresh_years(text, year, gold):
    from datetime import datetime as _dt
    a = _dt(year, 6, 27, 13, 4)
    assert start(text, a) == AstroDate(gold.year, gold.month, gold.day)
    assert span(text, a).width == timedelta(days=1)


# ---------------------------------------------------------------------------
# holidays this engine does NOT resolve for generic/out-of-window years --
# strict xfail, gold = the historically correct date, never a fake match.
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    reason="'festa del treball' (Fiesta del Trabajo, 1 May) carries no "
           "Catalan alias in es.tab -- bare lookup returns no span",
    strict=True,
)
@pytest.mark.parametrize("year", [2019, 2024, 2029, 2035])
def test_festa_del_treball_unresolved(year):
    from datetime import datetime as _dt
    a = _dt(year, 6, 27, 13, 4)
    gold = _next_fixed(year, 5, 1)
    assert start("festa del treball", a) == AstroDate(gold.year, gold.month, gold.day)


@pytest.mark.xfail(
    reason="'sant joan' (San Juan, 24 Jun, ES-CT) is a decree-only regional "
           "entry with no Catalan label -- bare lookup returns no span",
    strict=True,
)
@pytest.mark.parametrize("year", [2019, 2024, 2029, 2035])
def test_sant_joan_unresolved(year):
    from datetime import datetime as _dt
    a = _dt(year, 6, 27, 13, 4)
    gold = _next_fixed(year, 6, 24)
    assert start("sant joan", a) == AstroDate(gold.year, gold.month, gold.day)


@pytest.mark.xfail(
    reason="'diada nacional' (Diada Nacional de Catalunya, 11 Sep) is a "
           "decree-only entry limited to 2023-2027 -- bare lookup returns "
           "no span for years outside that window",
    strict=True,
)
@pytest.mark.parametrize("year", [2019, 2029, 2035, 2041])
def test_diada_nacional_unresolved(year):
    from datetime import datetime as _dt
    a = _dt(year, 6, 27, 13, 4)
    gold = _next_fixed(year, 9, 11)
    assert start("diada nacional", a) == AstroDate(gold.year, gold.month, gold.day)
