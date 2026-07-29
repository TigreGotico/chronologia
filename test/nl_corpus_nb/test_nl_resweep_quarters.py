"""nb: calendar quarters, second-pass resweep -- fresh years 2117-2136.

``test_nl_quarter.py`` covers 2018/2020/2026 only. Quarter N spans months
[3N-2 .. 3N]; gold hand-derived, no engine round-trip.
"""
import pytest

from ._corpus import AstroDate, start_end

_Q_START_MONTH = {1: 1, 2: 4, 3: 7, 4: 10}


def _cases():
    out = []
    for y in range(2117, 2137):
        for q in (1, 2, 3, 4):
            sm = _Q_START_MONTH[q]
            ey, em = (y + 1, 1) if q == 4 else (y, sm + 3)
            out.append((f"Q{q} {y}", y, sm, ey, em))
    return out


@pytest.mark.parametrize("text,sy,sm,ey,em", _cases())
def test_quarter_resweep(text, sy, sm, ey, em):
    s, e = start_end(text)
    assert s == AstroDate(sy, sm, 1)
    assert e == AstroDate(ey, em, 1)
