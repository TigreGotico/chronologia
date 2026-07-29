# -*- coding: utf-8 -*-
"""Second-pass sweep: all four calendar quarters ("o Nº trimestre de <ano>")
across fifteen fresh years -- none overlapping the small hand-picked sample
already pinned in test_nl_quarter.py (2018, 2020, 2026).

Quarter N spans months [3N-2 .. 3N]; the gold end is the first day of the
month after the quarter closes -- pure arithmetic, independent of the parser.

Anchor Tuesday 2017-06-27 13:04, irrelevant since every case names its own
year.
"""
import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end

_ORD = {1: "primeiro", 2: "segundo", 3: "terceiro", 4: "quarto"}

_YEARS = [2012, 2014, 2016, 2019, 2021, 2022, 2023, 2025,
          2028, 2031, 2034, 2037, 2040, 2043, 2047]


def _sweep():
    out = []
    for y in _YEARS:
        for q in (1, 2, 3, 4):
            sm = 3 * q - 2
            em = 3 * q + 1
            ey = y
            if em == 13:
                em = 1
                ey = y + 1
            text = f"o {_ORD[q]} trimestre de {y}"
            out.append((text, y, sm, ey, em))
    return out


@pytest.mark.parametrize("text,sy,sm,ey,em", _sweep())
def test_quarter_year_sweep(text, sy, sm, ey, em):
    s, e = start_end(text)
    assert s == AstroDate(sy, sm, 1), f"{text!r} -> start {s}"
    assert e == AstroDate(ey, em, 1), f"{text!r} -> end {e}"
