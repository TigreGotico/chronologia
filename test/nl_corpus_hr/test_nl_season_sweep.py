# -*- coding: utf-8 -*-
"""Broad oracle sweep: "<season> <year>" (hr).

Croatian meteorological seasons: proljeće (spring, Mar-Jun), ljeto (summer,
Jun-Sep), jesen (autumn, Sep-Dec), zima (winter, Dec-Mar of next year).  Each
spans three whole months, half-open.  Gold is fixed month arithmetic.

Anchor 2017-06-27.
"""
import pytest

from ._corpus import AstroDate, start_end

# (name, start_month, end_month, end_year_offset)
_SEASONS = [('proljeće', 3, 6, 0), ('ljeto', 6, 9, 0),
            ('jesen', 9, 12, 0), ('zima', 12, 3, 1)]

_CASES = [(f"{n} {y}", y, sm, em, off)
          for y in (2019, 2020, 2021, 2022)
          for (n, sm, em, off) in _SEASONS]


@pytest.mark.parametrize("phrase,y,sm,em,off", _CASES, ids=[c[0] for c in _CASES])
def test_season_year(phrase, y, sm, em, off):
    st, en = start_end(phrase)
    assert st == AstroDate(y, sm, 1), phrase
    assert en == AstroDate(y + off, em, 1), phrase
