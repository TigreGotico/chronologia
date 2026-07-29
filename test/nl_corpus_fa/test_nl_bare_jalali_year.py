# -*- coding: utf-8 -*-
"""Persian bare-year calendar corpus -- Solar-Hijri default + escapes.

A bare 4-digit year in Persian text reads on the PRIMARY Solar-Hijri (Jalali)
calendar, bounded to the civil window (1200..1500 SH).  Gold Gregorian spans
are computed by the independent Borkowski oracle in ``_jalali`` -- never read
back from the parser.  Years 1403 and 1404 are deliberately omitted: the
oracle's docstring flags 1404 as the borderline equinox/Nowruz case where the
arithmetic and the engine disagree by a day, and 1403's year-END lands on that
same 1404 Nowruz, so neither year's gold is certain.

Escapes that must keep reading Gregorian:
 * the explicit میلادی ("AD / Gregorian") marker (a separate ``era_ad``
   construction), and
 * Gregorian-scale years outside the civil Solar-Hijri window ("2024").
"""
from datetime import datetime

import pytest

from ._corpus import ad, start_end
from ._jalali import j2g

# Contemporary Solar-Hijri civil years across the window (1404 excluded).
_SH_YEARS = [1200, 1300, 1350, 1380, 1399, 1400, 1401, 1402, 1450, 1500]


def _sh_gold(y):
    s = j2g(y, 1, 1)
    e = j2g(y + 1, 1, 1)
    return (ad(datetime(s.year, s.month, s.day)),
            ad(datetime(e.year, e.month, e.day)))


@pytest.mark.parametrize("y", _SH_YEARS)
def test_bare_year_is_solar_hijri(y):
    assert start_end(str(y)) == _sh_gold(y)


@pytest.mark.parametrize("y", _SH_YEARS)
def test_sal_prefixed_year_is_solar_hijri(y):
    assert start_end("سال %d" % y) == _sh_gold(y)


# --- Gregorian escapes -----------------------------------------------------

def _greg_year(y):
    return ad(datetime(y, 1, 1)), ad(datetime(y + 1, 1, 1))


@pytest.mark.parametrize("y", [1402, 1403, 1450])
def test_miladi_marker_forces_gregorian(y):
    """میلادی ("AD") pins the literal Gregorian year even inside the civil
    Solar-Hijri window -- the deliberate escape hatch."""
    assert start_end("%d میلادی" % y) == _greg_year(y)


@pytest.mark.parametrize("y", [1600, 1900, 2000, 2024, 2100])
def test_gregorian_scale_year_stays_gregorian(y):
    """Years outside the civil Solar-Hijri window read as written Gregorian:
    a Persian speaker naming 2024 means 2024 AD, not SH 2024."""
    assert start_end(str(y)) == _greg_year(y)
