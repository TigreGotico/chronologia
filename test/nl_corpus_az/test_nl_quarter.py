"""Calendar quarters (az). Quarter N spans months [3N-2 .. 3N]; edges
hand-derived (anchor 2017-06-27, in Q2). Azerbaijani ordinals fold to numbers,
so both word ("üçüncü rüb") and ordinal-dot ("3. rüb") forms resolve."""
from datetime import datetime
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, parse

A = datetime(2017, 6, 27, 13, 4)
_CASES = [
    ("Q3 2026", 2026, 7, 2026, 10),
    ("Q1 2020", 2020, 1, 2020, 4),
    ("3. rüb 2026", 2026, 7, 2026, 10),
    ("üçüncü rüb 2026", 2026, 7, 2026, 10),
    ("2. rüb 2018", 2018, 4, 2018, 7),
    ("bu rüb", 2017, 4, 2017, 7),
    ("gələn rüb", 2017, 7, 2017, 10),
    ("keçən rüb", 2017, 1, 2017, 4),
]

@pytest.mark.parametrize("text,sy,sm,ey,em", _CASES)
def test_quarter(text, sy, sm, ey, em):
    s, e = start_end(text, A)
    assert s == AstroDate(sy, sm, 1)
    assert e == AstroDate(ey, em, 1)

@pytest.mark.parametrize("text", ["Q5 2026", "beşinci rüb", "Q0 2020"])
def test_not_a_quarter(text):
    r = parse(text, A)
    if r is not None:
        s, e = r[0].start, r[0].end
        assert not (s.day == 1 and s.month in (1, 4, 7, 10)
                    and (e.year - s.year) * 12 + (e.month - s.month) == 3)
