"""Open-ended ranges (el): Greek frames both ends with a LEADING preposition --
"μέχρι <date>" (open start, bounded below by now) and "από <date>" (open end,
bounded above by now) -- so the engine's leading-marker range machinery
expresses them natively. Dash-framed ranges parse language-agnostically."""
from datetime import datetime
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, ad

A = datetime(2017, 6, 27, 13, 4)

@pytest.mark.parametrize("text,s,e", [
    ("ιούνιος - αύγουστος", (2017, 6, 1), (2017, 9, 1)),
    ("ιανουάριος - μάρτιος", (2017, 1, 1), (2017, 4, 1)),
])
def test_dash_range(text, s, e):
    ss, ee = start_end(text, A)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)

def test_mexri_open_start():
    s, e = start_end("μέχρι την παρασκευή", A)
    assert s == ad(A)
    assert e == AstroDate(2017, 7, 1)

def test_apo_open_end():
    s, e = start_end("από το 2010", A)
    assert s == AstroDate(2010, 1, 1)
    assert e == ad(A)
