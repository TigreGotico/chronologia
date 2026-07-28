# -*- coding: utf-8 -*-
"""sv: definite-form seasons ("våren/sommaren/hösten/vintern <year>") sweep.

Meteorological, Northern-hemisphere season quarters computed INDEPENDENTLY:
vår = Mar-May, sommar = Jun-Aug, höst = Sep-Nov, vinter = Dec (of year) to
Feb (of year+1). Complements the indefinite-form cases in
``test_sv_scoped_seasons.py`` -- the definite ``-en/-et`` inflection is the new
surface here. Anchor 2017-06-27; year-qualified so no roll applies.
"""
import pytest

from ._corpus import AstroDate, start_end

_YEARS = [2018, 2019, 2020, 2021, 2022]

# name -> (start_month, end_month_exclusive, end_year_offset)
_SEASON = {
    "våren": (3, 6, 0),
    "sommaren": (6, 9, 0),
    "hösten": (9, 12, 0),
    "vintern": (12, 3, 1),
}


def _build():
    cases = []
    for name, (sm, em, off) in _SEASON.items():
        for y in _YEARS:
            gs = AstroDate(y, sm, 1)
            ge = AstroDate(y + off, em, 1)
            cases.append((f"{name} {y}", gs, ge))
    return cases


_CASES = _build()


@pytest.mark.parametrize("text,gs,ge", _CASES, ids=[c[0] for c in _CASES])
def test_season_definite(text, gs, ge):
    assert start_end(text) == (gs, ge)
