# -*- coding: utf-8 -*-
"""Clock readings in Malay."""
import pytest
from ._corpus import start


@pytest.mark.parametrize("text,h,m", [
    ("15:30", 15, 30), ("09:00", 9, 0), ("23:59", 23, 59),
    ("06:15", 6, 15), ("00:00", 0, 0), ("12:00", 12, 0)])
def test_iso_clock(text, h, m):
    s = start(text)
    assert (s.hour, s.minute) == (h, m)


@pytest.mark.parametrize("text,h", [
    ("pukul 3", 3), ("jam 9", 9), ("pukul 7", 7), ("jam 11", 11),
    ("pukul 8", 8)])
def test_at_hour(text, h):
    assert start(text).hour == h


# -- THE MALAY HALF TRAP: "setengah tiga" == 02:30 (half TOWARD three), NOT
# 03:30 -- the German-style toward-hour reading, the OPPOSITE of English
# "half three" == 03:30.
# Source: Kamus Dewan (DBP) "setengah jam" == 30 min; toward-hour clock
# corroborated across Malay usage.
@pytest.mark.parametrize("text,h,m", [
    ("setengah tiga", 2, 30),          # half toward three -- NOT 3:30
    ("pukul setengah tiga", 2, 30),
    ("setengah sembilan", 8, 30),
    ("setengah lima", 4, 30),
])
def test_setengah_is_half_toward(text, h, m):
    s = start(text)
    assert (s.hour, s.minute) == (h, m)
