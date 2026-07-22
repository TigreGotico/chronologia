"""Open-ended ranges (et): Estonian frames both ends with a LEADING preposition
-- "kuni <date>" (open start, bounded below by now) and "alates <date>" (open
end, bounded above by now) -- so the engine's leading-marker range machinery
expresses them natively. Dash-framed ranges parse language-agnostically."""
from datetime import datetime
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, ad

A = datetime(2017, 6, 27, 13, 4)

@pytest.mark.parametrize("text,s,e", [
    ("juuni - august", (2017, 6, 1), (2017, 9, 1)),
    ("jaanuar - märts", (2017, 1, 1), (2017, 4, 1)),
])
def test_dash_range(text, s, e):
    ss, ee = start_end(text, A)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)

def test_kuni_open_start():
    s, e = start_end("kuni reede", A)
    assert s == ad(A)
    assert e == AstroDate(2017, 7, 1)

def test_alates_open_end():
    s, e = start_end("alates 2010", A)
    assert s == AstroDate(2010, 1, 1)
    assert e == ad(A)
