"""Open-ended ranges (ms): Malay frames both ends with a LEADING word --
"sehingga <date>" (open start) and "sejak <date>" (open end) -- so the engine's
leading-marker range machinery expresses them natively."""
from datetime import datetime
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, ad

A = datetime(2017, 6, 27, 13, 4)

@pytest.mark.parametrize("text,s,e", [
    ("jun - ogos", (2017, 6, 1), (2017, 9, 1)),
    ("januari - mac", (2017, 1, 1), (2017, 4, 1)),
])
def test_dash_range(text, s, e):
    ss, ee = start_end(text, A)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)

def test_sehingga_open_start():
    s, e = start_end("sehingga jumaat", A)
    assert s == ad(A)
    assert e == AstroDate(2017, 7, 1)

def test_sejak_open_end():
    s, e = start_end("sejak 2010", A)
    assert s == AstroDate(2010, 1, 1)
    assert e == ad(A)


# -- closed ranges: "hingga"/"sampai" as the range TERMINATOR ---------------
# Kamus Dewan (DBP), s.v. "hingga" -- "sampai ke had tertentu: Mesyuarat itu
# berlangsung dr pukul sepuluh pagi hingga pukul dua belas tengah hari": the
# named limit closes the period.  Both words were declared only as the open
# "until" marker, so a closed range said with one of them degraded into the
# open reading, with the terminator left in the remainder.
@pytest.mark.parametrize("text", [
    "12 Jun hingga 20 Jun",
    "12 Jun sampai 20 Jun",
    "dari 12 Jun hingga 20 Jun",
    "12 hingga 20 Jun",
])
def test_closed_range_ends_after_the_named_day(text):
    ss, ee = start_end(text, A)
    assert ss == AstroDate(2018, 6, 12) and ee == AstroDate(2018, 6, 21)


def test_closed_range_crosses_the_month():
    ss, ee = start_end("28 Jun hingga 3 Julai", A)
    assert ss == AstroDate(2017, 6, 28) and ee == AstroDate(2017, 7, 4)


def test_leading_hingga_is_still_the_open_until():
    ss, ee = start_end("hingga 20 Jun", A)
    assert ss == ad(A) and ee == AstroDate(2018, 6, 21)


@pytest.mark.parametrize("text", ["hingga", "sampai", "12 hingga"])
def test_closed_range_garbage_never_raises(text):
    from ._corpus import parse
    parse(text, A)
