# -*- coding: utf-8 -*-
"""Calendar quarters (fa).  Quarter N spans months [3N-2 .. 3N]; edges
hand-derived (anchor 2017-06-27, in Q2).

Persian writes the quarter head-first: ``سه‌ماهه ۳`` / ``فصل ۳``.  The spoken
ordinal ``سه‌ماهه سوم`` ("third quarter") needs Persian spelled ordinals folded
to a number, which the shared numfold does not provide -- out of scope here
(engine follow-up), covered by ``test_spelled_ordinal_pending``.  A postposed
relative marker (``آینده`` next / ``گذشته`` last / ``این`` this) shifts by
whole quarters."""
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, parse

_CASES = [
    ('سه‌ماهه 3', 2017, 7, 2017, 10),
    ('سه‌ماهه 1', 2017, 1, 2017, 4),
    ('فصل 2', 2017, 4, 2017, 7),
    ('سه‌ماهه 4', 2017, 10, 2018, 1),
    ('سه‌ماهه 3 2026', 2026, 7, 2026, 10),
    ('فصل 1 2020', 2020, 1, 2020, 4),
    ('فصل آینده', 2017, 7, 2017, 10),
    ('این فصل', 2017, 4, 2017, 7),
    ('فصل گذشته', 2017, 1, 2017, 4),
]


@pytest.mark.parametrize("text,sy,sm,ey,em", _CASES)
def test_quarter(text, sy, sm, ey, em):
    s, e = start_end(text)
    assert s == AstroDate(sy, sm, 1)
    assert e == AstroDate(ey, em, 1)


@pytest.mark.parametrize("text", ['سه‌ماهه 5 2026', 'فصل 0'])
def test_not_a_quarter(text):
    r = parse(text)
    if r is not None:
        s, e = r[0].start, r[0].end
        assert not (s.day == 1 and s.month in (1, 4, 7, 10)
                    and (e.year - s.year) * 12 + (e.month - s.month) == 3)


@pytest.mark.xfail(reason="Persian spelled ordinals (سوم) are not folded to a "
                          "number by the shared numfold; engine follow-up",
                   strict=True)
def test_spelled_ordinal_pending():
    s, e = start_end('سه‌ماهه سوم')
    assert s == AstroDate(2017, 7, 1) and e == AstroDate(2017, 10, 1)
