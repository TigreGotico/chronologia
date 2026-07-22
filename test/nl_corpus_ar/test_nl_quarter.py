# -*- coding: utf-8 -*-
"""Calendar quarters (ar).  Quarter N spans months [3N-2 .. 3N]; edges
hand-derived (anchor 2017-06-27, in Q2).

Arabic writes the quarter head-first: ``الربع 3`` ("quarter 3").  The spoken
ordinal form ``الربع الثالث`` ("the third quarter") needs Arabic spelled
ordinals folded to a number, a capability the shared numfold does not yet
provide for Arabic -- it is out of scope here (an engine-level follow-up) and
covered by ``test_spelled_ordinal_pending`` below.  A relative marker
(``القادم`` next / ``الماضي`` last / ``هذا`` this) shifts by whole quarters.
"""
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, parse

# (text, start-year, start-month, end-year, end-month)
_CASES = [
    ('الربع 3', 2017, 7, 2017, 10),
    ('الربع 1', 2017, 1, 2017, 4),
    ('الربع 2', 2017, 4, 2017, 7),
    ('الربع 4', 2017, 10, 2018, 1),
    ('الربع 3 2026', 2026, 7, 2026, 10),
    ('الربع 1 2020', 2020, 1, 2020, 4),
    ('الربع القادم', 2017, 7, 2017, 10),   # next quarter from Q2
    ('هذا الربع', 2017, 4, 2017, 7),        # this quarter
    ('الربع الماضي', 2017, 1, 2017, 4),     # last quarter
]


@pytest.mark.parametrize("text,sy,sm,ey,em", _CASES)
def test_quarter(text, sy, sm, ey, em):
    s, e = start_end(text)
    assert s == AstroDate(sy, sm, 1)
    assert e == AstroDate(ey, em, 1)


@pytest.mark.parametrize("text", ['الربع 5 2026', 'الربع 0'])
def test_not_a_quarter(text):
    r = parse(text)
    if r is not None:
        s, e = r[0].start, r[0].end
        assert not (s.day == 1 and s.month in (1, 4, 7, 10)
                    and (e.year - s.year) * 12 + (e.month - s.month) == 3)


@pytest.mark.xfail(reason="Arabic spelled ordinals (الثالث) are not folded to "
                          "a number by the shared numfold; engine follow-up",
                   strict=True)
def test_spelled_ordinal_pending():
    s, e = start_end('الربع الثالث')
    assert s == AstroDate(2017, 7, 1) and e == AstroDate(2017, 10, 1)
