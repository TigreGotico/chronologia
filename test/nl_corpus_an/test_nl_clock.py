# -*- coding: utf-8 -*-
"""Clock readings in Aragonese."""
import pytest
from ._corpus import start


@pytest.mark.parametrize("text,h,m", [
    ("15:30", 15, 30), ("09:00", 9, 0), ("23:59", 23, 59),
    ("06:15", 6, 15), ("00:00", 0, 0), ("12:00", 12, 0)])
def test_iso_clock(text, h, m):
    s = start(text)
    assert (s.hour, s.minute) == (h, m)


@pytest.mark.parametrize("text,h", [
    ("a las 3", 3), ("a las 9", 9), ("a las 7", 7), ("a las 11", 11)])
def test_at_hour(text, h):
    assert start(text).hour == h


@pytest.mark.parametrize("text,h", [("meydia", 12), ("meyanueyt", 0)])
def test_landmarks(text, h):
    assert start(text).hour == h
