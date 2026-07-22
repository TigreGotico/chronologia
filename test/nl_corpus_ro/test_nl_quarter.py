"""Calendar quarters (ro). Quarter N spans months [3N-2 .. 3N]; edges
hand-derived (anchor 2017-06-27, in Q2). Out-of-range is not a quarter."""
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, parse

_CASES = [('Q3 2026', 2026, 7, 2026, 10), ('Q1 2020', 2020, 1, 2020, 4), ('Q2 2018', 2018, 4, 2018, 7), ('acest trimestru', 2017, 4, 2017, 7), ('trimestrul viitor', 2017, 7, 2017, 10), ('trimestrul trecut', 2017, 1, 2017, 4)]

@pytest.mark.parametrize("text,sy,sm,ey,em", _CASES)
def test_quarter(text, sy, sm, ey, em):
    s, e = start_end(text)
    assert s == AstroDate(sy, sm, 1)
    assert e == AstroDate(ey, em, 1)

@pytest.mark.parametrize("text", ['Q5 2026', 'Q0 2020'])
def test_not_a_quarter(text):
    r = parse(text)
    if r is not None:
        s, e = r[0].start, r[0].end
        assert not (s.day == 1 and s.month in (1, 4, 7, 10)
                    and (e.year - s.year) * 12 + (e.month - s.month) == 3)
