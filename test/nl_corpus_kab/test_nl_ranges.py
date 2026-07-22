"""Open-ended ranges (kab): Kabyle frames both ends with a LEADING word --
"armi <date>" (until; open start) and "seg <date>" (since; open end) -- so the
engine's leading-marker range machinery expresses them natively."""
from datetime import datetime
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, ad

A = datetime(2017, 6, 27, 13, 4)

def test_armi_open_start():
    s, e = start_end("armi 2020", A)
    assert s == ad(A)
    assert e == AstroDate(2021, 1, 1)

def test_seg_open_end():
    s, e = start_end("seg 2010", A)
    assert s == AstroDate(2010, 1, 1)
    assert e == ad(A)

@pytest.mark.parametrize("text,ey", [("armi 2019", 2020), ("armi 2025", 2026)])
def test_armi_years(text, ey):
    s, e = start_end(text, A)
    assert s == ad(A)
    assert e == AstroDate(ey, 1, 1)

@pytest.mark.parametrize("text,sy", [("seg 2000", 2000), ("seg 2015", 2015)])
def test_seg_years(text, sy):
    s, e = start_end(text, A)
    assert s == AstroDate(sy, 1, 1)
    assert e == ad(A)
