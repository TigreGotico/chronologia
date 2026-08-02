# -*- coding: utf-8 -*-
"""The pre-existing Hebrew (jewish) calendar month spans keep working after
the Gregorian build-out.  Expected Gregorian spans are fixed astronomical
conversions of the Hebrew month, hand-checked, not pinned from the parser."""
import pytest

from ._corpus import AstroDate, start_end


@pytest.mark.parametrize("text,s,e", [
    ("תשרי 5785", (2024, 10, 3), (2024, 11, 2)),
    ("ניסן 5785", (2025, 3, 30), (2025, 4, 29)),
    ("אב 5784", (2024, 8, 5), (2024, 9, 4)),
    ("כסלו 5785", (2024, 12, 2), (2025, 1, 1)),
])
def test_hebrew_calendar_months(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


def test_hebrew_calendar_months_with_bet_prefix():
    """The grammatically standard "בניסן" (be-Nisan, "in Nisan") -- the bet
    prefix glued onto the Hebrew-calendar month -- must resolve like the bare
    "ניסן", not fall through to a bogus Gregorian year (5785)."""
    from datetime import datetime
    from chronologia import extract_timespan
    a = datetime(2017, 6, 27, 13, 4)
    got = extract_timespan("15 בניסן 5785", "he", a)
    assert got is not None and got[0].start.date().isoformat() == "2025-04-13"
    assert got.remainder == ""
    # matches the un-prefixed form
    bare = extract_timespan("15 ניסן 5785", "he", a)
    assert got[0].start == bare[0].start
    # another month + the Gregorian bet-prefix still works
    assert extract_timespan("15 בתשרי 5785", "he", a)[0].start.date().isoformat() == "2024-10-17"
    assert extract_timespan("15 בינואר 2020", "he", a)[0].start.date().isoformat() == "2020-01-15"
