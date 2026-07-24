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


# -- closed ranges: "sampai"/"hingga" as the range TERMINATOR ---------------
# KBBI, s.v. "sampai", sense 6 "hingga" -- "perjanjian itu berlaku sampai tahun
# depan", the agreement running through next year: the named limit is part of
# the period.  Both words were declared only as the open "until" marker, so a
# closed range said with one of them degraded into the open reading -- the left
# endpoint to the anchor instant -- with the terminator left in the remainder.
@pytest.mark.parametrize("text", [
    "5 Juni sampai 12 Juni",
    "5 Juni hingga 12 Juni",
    "dari 5 Juni sampai 12 Juni",
    "5 sampai 12 Juni",
])
def test_closed_range_ends_after_the_named_day(text):
    ss, ee = start_end(text, A)
    assert ss == AstroDate(2018, 6, 5) and ee == AstroDate(2018, 6, 13)


def test_closed_range_crosses_the_month():
    ss, ee = start_end("28 Juni sampai 3 Juli", A)
    assert ss == AstroDate(2017, 6, 28) and ee == AstroDate(2017, 7, 4)


# -- adversarial: the OPEN reading is untouched, because a leading marker has
# no left endpoint to split on.
def test_leading_sampai_is_still_the_open_until():
    ss, ee = start_end("sampai 12 Juni", A)
    assert ss == ad(A) and ee == AstroDate(2018, 6, 13)


@pytest.mark.parametrize("text", ["sampai", "sampai jumpa", "5 sampai"])
def test_closed_range_garbage_never_raises(text):
    from ._corpus import parse
    parse(text, A)
