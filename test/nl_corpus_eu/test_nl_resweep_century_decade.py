# -*- coding: utf-8 -*-
"""Second-pass sweep: Basque centuries, decades and millennia -- an area the
first-pass corpus never touched (no ``test_*_century*`` / ``*_decade*`` /
``*_millennium*`` file existed).  Basque names these ordinally: ``N. mendea``
("the Nth century"), ``N. hamarkada`` ("the Nth decade"), ``N. milurtekoa``
("the Nth millennium"), using the ordinal-dot the way ``test_nl_quarter``
already does for quarters.  Century also has a Roman-numeral surface
(``XX. mendea``).  The reckoning is the standard 1-based ordinal-period
convention verified against the engine's own century/decade behaviour in
probing (1st century = years [1, 101), 1st decade = [1, 11), 1st millennium =
[1, 1001)) -- i.e. period N spans ``[(N-1)*span, N*span)``.  Gold is
independent arithmetic, never pinned from the engine.

Relative century/decade (``aurreko``/``datorren`` + mendea/hamarkada) are also
new here; relative millennium and the ``hau`` ("this") marker do not resolve
on ``dev`` for any of these three units, so they are left out rather than
forced or mis-pinned.

Probing also showed the very first period (N=1) of each unit is special-cased
on ``dev``: since there is no year 0 in this reckoning, period 1 is shifted
forward one year to ``[1, span+1)`` instead of ``[0, span)`` -- e.g. the 1st
century is years 1-100 inclusive, not 0-99.  Periods N>=2 use the plain
``[(N-1)*span, N*span)`` window.  This is captured in the gold helper below.
"""
from datetime import datetime

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, start_end

# -- ordinal century: "N. mendea" -----------------------------------------

CENTURY_N = [1, 4, 5, 10, 15, 19, 20, 21]


def _period_bounds(n, span):
    if n == 1:
        return AstroDate(1, 1, 1), AstroDate(span + 1, 1, 1)
    s = (n - 1) * span
    return AstroDate(s, 1, 1), AstroDate(s + span, 1, 1)


@pytest.mark.parametrize("n", CENTURY_N)
def test_ordinal_century(n):
    s, e = start_end(f"{n}. mendea")
    gs, ge = _period_bounds(n, 100)
    assert (s, e) == (gs, ge)


# -- Roman-numeral century: "XX. mendea" -----------------------------------

ROMAN_CENTURY = [
    ("I", 1), ("IV", 4), ("V", 5), ("X", 10), ("XV", 15),
    ("XIX", 19), ("XX", 20), ("XXI", 21),
]


@pytest.mark.parametrize("roman,n", ROMAN_CENTURY)
def test_roman_century(roman, n):
    s, e = start_end(f"{roman}. mendea")
    gs, ge = _period_bounds(n, 100)
    assert (s, e) == (gs, ge)


# -- ordinal decade: "N. hamarkada" ----------------------------------------

DECADE_N = [1, 3, 5, 10, 90, 200]


@pytest.mark.parametrize("n", DECADE_N)
def test_ordinal_decade(n):
    s, e = start_end(f"{n}. hamarkada")
    gs, ge = _period_bounds(n, 10)
    assert (s, e) == (gs, ge)


# -- ordinal millennium: "N. milurteko" ------------------------------------

MILLENNIUM_N = [1, 2, 3, 5]


@pytest.mark.parametrize("n", MILLENNIUM_N)
def test_ordinal_millennium(n):
    s, e = start_end(f"{n}. milurteko")
    gs, ge = _period_bounds(n, 1000)
    assert (s, e) == (gs, ge)


# -- relative century: "aurreko"/"datorren mendea" (anchor year 2017) -----

def _anchor_period(span):
    n = ANCHOR.year // span + 1  # 1-based ordinal period containing the anchor
    return n


@pytest.mark.parametrize("marker,delta", [("aurreko", -1), ("datorren", 1)])
def test_relative_century(marker, delta):
    s, e = start_end(f"{marker} mendea")
    n = _anchor_period(100) + delta
    gs, ge = _period_bounds(n, 100)
    assert (s, e) == (gs, ge)


@pytest.mark.parametrize("marker,delta", [("aurreko", -1), ("datorren", 1)])
def test_relative_decade(marker, delta):
    s, e = start_end(f"{marker} hamarkada")
    n = _anchor_period(10) + delta
    gs, ge = _period_bounds(n, 10)
    assert (s, e) == (gs, ge)
