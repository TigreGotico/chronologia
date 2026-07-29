# -*- coding: utf-8 -*-
"""Second-pass sweep: calendar quarters (ru), fresh years x both digit forms.

``test_nl_quarter.py`` pinned a handful of spot cases touching years 2018,
2019, 2020, 2026.  This file sweeps all four quarters, both the "Q<N> <year>"
and "<N> квартал <year>" surfaces, across eight FRESH years that file never
used.  Quarter N spans months [3N-2 .. 3N]; gold is that fixed arithmetic,
independent of the parser.
"""
import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end

# fresh years, disjoint from test_nl_quarter.py's (2018, 2019, 2020, 2026)
_YEARS = (2022, 2023, 2024, 2025, 2027, 2028, 2029, 2030)


def _cases():
    out = []
    for y in _YEARS:
        for q in (1, 2, 3, 4):
            sm = 3 * q - 2
            em = sm + 3
            ey = y
            if em > 12:
                em -= 12
                ey = y + 1
            out.append((f"Q{q} {y}", y, sm, ey, em))
            out.append((f"{q} квартал {y}", y, sm, ey, em))
    return out


_CASES = _cases()


@pytest.mark.parametrize("text,sy,sm,ey,em", _CASES, ids=[c[0] for c in _CASES])
def test_quarter_fresh(text, sy, sm, ey, em):
    s, e = start_end(text)
    assert s == AstroDate(sy, sm, 1), text
    assert e == AstroDate(ey, em, 1)
