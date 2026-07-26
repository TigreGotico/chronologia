"""Calendar halves (it): "first/second half of <year>" splits the year
at July 1 so the two halves tile with no gap; the deictic "half of the
century/millennium" halves the anchor's period. Edges hand-derived (anchor
2017-06-27). half_period inherits the shared BASE_GRAMMAR; this locale supplies
the period-noun surface (marker_half). Regression guard against the silent-wrong
where the half phrase stranded and the whole year/period was returned."""
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end

_CASES = [
    ('la prima metà del 2020', 2020, 1, 1, 2020, 7, 1),
    ('la seconda metà del 2020', 2020, 7, 1, 2021, 1, 1),
]

@pytest.mark.parametrize("text,sy,sm,sd,ey,em,ed", _CASES)
def test_half_period(text, sy, sm, sd, ey, em, ed):
    s, e = start_end(text)
    assert s == AstroDate(sy, sm, sd)
    assert e == AstroDate(ey, em, ed)
