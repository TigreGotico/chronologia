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
