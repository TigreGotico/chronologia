"""German "Kalenderwoche" (calendar week), the full word next to "KW": "KW
12" already resolved through ``marker_week_num``'s abbreviation, but the
un-abbreviated ordinal prose ("die 12. Kalenderwoche") named no surface at
all and the token stranded.  Expected Mondays come from the stdlib
``date.fromisocalendar``, independent of the parser under test.
"""
from datetime import date, datetime, timedelta

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch

ANCHOR = datetime(2026, 6, 15, 12, 0)


@pytest.mark.parametrize("text,iy,iw", [
    ("die 12. Kalenderwoche", 2026, 12),
    ("Kalenderwoche 12", 2026, 12),
    ("die 12. Kalenderwoche 2024", 2024, 12),
])
def test_kalenderwoche(text, iy, iw):
    monday = date.fromisocalendar(iy, iw, 1)
    nxt = monday + timedelta(days=7)
    s, e = start_end(text, anchor=ANCHOR)
    assert s == AstroDate(monday.year, monday.month, monday.day)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)


def test_kalenderwoche_crosses_year_boundary():
    # ISO week 1 of 2026 starts in December 2025 -- the ordinal-prose
    # "Kalenderwoche" surface must resolve the same boundary-crossing week
    # the digit "KW" form already does.
    monday = date.fromisocalendar(2026, 1, 1)
    nxt = monday + timedelta(days=7)
    s, e = start_end("die 1. Kalenderwoche 2026", anchor=ANCHOR)
    assert s == AstroDate(monday.year, monday.month, monday.day)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)


def test_kalenderwoche_unattested_bare_word_still_refuses():
    nomatch("Kalenderwoche", anchor=ANCHOR)
