# -*- coding: utf-8 -*-
"""Clock readings in Indonesian."""
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
