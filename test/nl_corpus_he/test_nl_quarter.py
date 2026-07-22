# -*- coding: utf-8 -*-
"""Calendar quarters (he).  Quarter N spans months [3N-2 .. 3N]; edges
hand-derived (anchor 2017-06-27, in Q2).

Hebrew writes the quarter head-first: ``רבעון 3`` ("quarter 3").  The spoken
ordinal form ``רבעון שלישי`` ("third quarter") needs Hebrew spelled ordinals
folded to a number, which the shared numfold does not provide for Hebrew --
out of scope here (engine follow-up), covered by ``test_spelled_ordinal_pending``.
A postposed relative marker (``הבא`` next / ``הזה`` this) shifts by quarters."""
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, parse

_CASES = [
    ('רבעון 3', 2017, 7, 2017, 10),
    ('רבעון 1', 2017, 1, 2017, 4),
    ('רבעון 2', 2017, 4, 2017, 7),
    ('רבעון 4', 2017, 10, 2018, 1),
    ('רבעון 3 2026', 2026, 7, 2026, 10),
    ('רבעון 1 2020', 2020, 1, 2020, 4),
    ('הרבעון הבא', 2017, 7, 2017, 10),
    ('הרבעון הזה', 2017, 4, 2017, 7),
]


@pytest.mark.parametrize("text,sy,sm,ey,em", _CASES)
def test_quarter(text, sy, sm, ey, em):
    s, e = start_end(text)
    assert s == AstroDate(sy, sm, 1)
    assert e == AstroDate(ey, em, 1)


@pytest.mark.parametrize("text", ['רבעון 5 2026', 'רבעון 0'])
def test_not_a_quarter(text):
    r = parse(text)
    if r is not None:
        s, e = r[0].start, r[0].end
        assert not (s.day == 1 and s.month in (1, 4, 7, 10)
                    and (e.year - s.year) * 12 + (e.month - s.month) == 3)


@pytest.mark.xfail(reason="Hebrew spelled ordinals (שלישי) are not folded to a "
                          "number by the shared numfold; engine follow-up",
                   strict=True)
def test_spelled_ordinal_pending():
    s, e = start_end('רבעון שלישי')
    assert s == AstroDate(2017, 7, 1) and e == AstroDate(2017, 10, 1)
