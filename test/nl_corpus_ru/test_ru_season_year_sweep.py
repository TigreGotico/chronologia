# -*- coding: utf-8 -*-
"""Season + explicit year sweep (ru) -- "весна 2019" etc.

Meteorological northern-hemisphere seasons: весна = Mar-May (Mar1..Jun1), лето
= Jun-Aug, осень = Sep-Nov, зима = Dec..Feb (Dec1 of the named year to Mar1 of
the next).  Gold is that fixed mapping, independent of the parser.  Anchor
2017-06-27."""
import pytest

from ._corpus import AstroDate, start_end

_YEARS = (2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2025)


def _cases():
    out = []
    for year in _YEARS:
        out.append((f"весна {year}", AstroDate(year, 3, 1), AstroDate(year, 6, 1)))
        out.append((f"лето {year}", AstroDate(year, 6, 1), AstroDate(year, 9, 1)))
        out.append((f"осень {year}", AstroDate(year, 9, 1), AstroDate(year, 12, 1)))
        out.append((f"зима {year}", AstroDate(year, 12, 1), AstroDate(year + 1, 3, 1)))
    return out


@pytest.mark.parametrize("text,s,e", _cases())
def test_season_year(text, s, e):
    st, en = start_end(text)
    assert st == s
    assert en == e
