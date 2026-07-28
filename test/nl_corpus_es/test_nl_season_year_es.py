# -*- coding: utf-8 -*-
"""Meteorological seasons anchored to an explicit year in Spanish:
"la primavera de 2019".

Northern-hemisphere meteorological seasons, three whole months each:
``primavera`` = Mar-May, ``verano`` = Jun-Aug, ``otoño`` = Sep-Nov,
``invierno`` = Dec-Feb (winter starts in December of the named year and runs
into the following March).  Gold is closed-form: start = (year, start_month, 1),
end = start + 3 months, with December wrapping the end year.  This complements
``test_nl_scoped_seasons`` (which only spot-checks three years).
"""
from datetime import timedelta

import pytest

from ._corpus import AstroDate, start_end


_SEASONS = [
    ("primavera", 3, 6, 0),
    ("verano", 6, 9, 0),
    ("otoño", 9, 12, 0),
    ("invierno", 12, 3, 1),   # wraps into next year
]
_YEARS = [1955, 1969, 1988, 1999, 2005, 2012, 2018, 2021, 2025, 2030]


def _cases():
    out = []
    for name, sm, em, wrap in _SEASONS:
        for y in _YEARS:
            s = AstroDate(y, sm, 1)
            e = AstroDate(y + wrap, em, 1)
            out.append((f"{name} de {y}", s, e))
    return out


@pytest.mark.parametrize("text,want_s,want_e", _cases())
def test_season_of_year(text, want_s, want_e):
    s, e = start_end(text)
    assert s == want_s, f"{text!r} start {s} != {want_s}"
    assert e == want_e, f"{text!r} end {e} != {want_e}"
