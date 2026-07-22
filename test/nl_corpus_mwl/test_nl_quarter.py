# -*- coding: utf-8 -*-
"""Calendar quarters (mwl).  Quarter N spans months [3N-2 .. 3N]; edges
hand-derived (anchor 2017-06-27, in Q2).

Mirandese uses the ``T3`` short form, a digit before the head noun, and the
spelled ordinal (``l terceiro trimestre``) -- ``fold_mwl`` folds Mirandese
ordinals ``segundo``/``terceiro``/``quarto`` to a number, so those spoken
forms resolve.  A relative marker (``que ben`` next / ``passado`` last /
``este`` this) shifts by whole quarters."""
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, parse

_CASES = [
    ('T3', 2017, 7, 2017, 10),
    ('3 trimestre', 2017, 7, 2017, 10),
    ('2 trimestre', 2017, 4, 2017, 7),
    ('T1 2020', 2020, 1, 2020, 4),
    ('T3 2026', 2026, 7, 2026, 10),
    ('T4', 2017, 10, 2018, 1),
    ('trimestre que ben', 2017, 7, 2017, 10),
    ('este trimestre', 2017, 4, 2017, 7),
    ('trimestre passado', 2017, 1, 2017, 4),
    ('l terceiro trimestre', 2017, 7, 2017, 10),
    ('l segundo trimestre', 2017, 4, 2017, 7),
]


@pytest.mark.parametrize("text,sy,sm,ey,em", _CASES)
def test_quarter(text, sy, sm, ey, em):
    s, e = start_end(text)
    assert s == AstroDate(sy, sm, 1)
    assert e == AstroDate(ey, em, 1)


@pytest.mark.parametrize("text", ['T5 2026', 'T0'])
def test_not_a_quarter(text):
    r = parse(text)
    if r is not None:
        s, e = r[0].start, r[0].end
        assert not (s.day == 1 and s.month in (1, 4, 7, 10)
                    and (e.year - s.year) * 12 + (e.month - s.month) == 3)
