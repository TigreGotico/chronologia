# -*- coding: utf-8 -*-
"""Polish meteorological season + explicit year, swept across many years.

Seasons are northern-hemisphere meteorological three-month blocks:
wiosna = Mar-May (Mar 1 -> Jun 1), lato = Jun-Aug (Jun 1 -> Sep 1),
jesień = Sep-Nov (Sep 1 -> Dec 1), zima = Dec-Feb (Dec 1 -> Mar 1 next year).
Edges are hand-derived here; the parser is never consulted for the gold.

Anchor: Tuesday 2017-06-27 13:04.
"""
import pytest

from ._corpus import AstroDate, span

# (surface, start_month, start_year_offset, end_month, end_year_offset)
_SEASONS = [
    ("wiosna", 3, 0, 6, 0),
    ("lato", 6, 0, 9, 0),
    ("jesień", 9, 0, 12, 0),
    ("zima", 12, 0, 3, 1),
]

_YEARS = (2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025)

# spans already asserted elsewhere in the corpus (test_nl_dates_ranges.py)
_EXISTING = {("lato", 2020), ("zima", 2019)}


def _cases():
    out = []
    for y in _YEARS:
        for name, sm, so, em, eo in _SEASONS:
            if (name, y) in _EXISTING:
                continue
            gs = AstroDate(y + so, sm, 1)
            ge = AstroDate(y + eo, em, 1)
            out.append((f"{name} {y}", gs, ge))
    return out


_CASES = _cases()


@pytest.mark.parametrize("text,gs,ge", _CASES, ids=[c[0] for c in _CASES])
def test_season_year(text, gs, ge):
    s = span(text)
    assert (s.start, s.end) == (gs, ge)
