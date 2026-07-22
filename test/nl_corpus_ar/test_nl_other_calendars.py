# -*- coding: utf-8 -*-
"""The pre-existing Hijri (islamic-civil) calendar dates keep working after
the Gregorian build-out.  Expected Gregorian spans are fixed astronomical
conversions of the Hijri date, hand-checked, not pinned from the parser."""
import pytest

from ._corpus import AstroDate, start_end


@pytest.mark.parametrize("text,s,e", [
    ("محرم 1442", (2020, 8, 20), (2020, 9, 19)),
    ("رمضان 1442", (2021, 4, 13), (2021, 5, 13)),
    ("15 رمضان 1442", (2021, 4, 27), (2021, 4, 28)),
    ("شوال 1440", (2019, 6, 5), (2019, 7, 4)),
    ("1 محرم 1445", (2023, 7, 19), (2023, 7, 20)),
])
def test_hijri_dates(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)
