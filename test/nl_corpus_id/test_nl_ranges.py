"""Open-ended ranges (id): Indonesian frames both ends with a LEADING word --
"sampai <date>" (open start) and "sejak <date>" (open end) -- so the engine's
leading-marker range machinery expresses them natively."""
from datetime import datetime
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, ad

A = datetime(2017, 6, 27, 13, 4)

@pytest.mark.parametrize("text,s,e", [
    ("juni - agustus", (2017, 6, 1), (2017, 9, 1)),
    ("januari - maret", (2017, 1, 1), (2017, 4, 1)),
])
def test_dash_range(text, s, e):
    ss, ee = start_end(text, A)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)

def test_sampai_open_start():
    s, e = start_end("sampai jumat", A)
    assert s == ad(A)
    assert e == AstroDate(2017, 7, 1)

def test_sejak_open_end():
    s, e = start_end("sejak 2010", A)
    assert s == AstroDate(2010, 1, 1)
    assert e == ad(A)
