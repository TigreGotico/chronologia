# -*- coding: utf-8 -*-
"""Relative day words and clock readings in Kabyle.

Kabyle offers no citable directional 'N units ago / in N units' offset
vocabulary in the legacy corpus (its extract_duration is directionless), so
this locale intentionally ships no relative_offset construction; only the
attested relative-day words resolve.  That gap is documented, not faked."""
from datetime import timedelta
import pytest
from ._corpus import ANCHOR, start

A = ANCHOR


@pytest.mark.parametrize("text,days", [
    ("azekka", 1), ("iḍelli", -1), ("idelli", -1), ("assa", 0),
    ("ass a", 0), ("ass agi", 0)])
def test_named_days(text, days):
    exp = (A + timedelta(days=days)).date()
    assert (start(text).month, start(text).day) == (exp.month, exp.day)


@pytest.mark.parametrize("text,h,m", [
    ("15:30", 15, 30), ("09:00", 9, 0), ("23:59", 23, 59),
    ("06:15", 6, 15), ("00:00", 0, 0), ("12:00", 12, 0), ("13:04", 13, 4)])
def test_iso_clock(text, h, m):
    s = start(text)
    assert (s.hour, s.minute) == (h, m)


@pytest.mark.parametrize("text,h,m", [
    ("15:30 tameddit", 15, 30), ("09:00 ssbeḥ", 9, 0)])
def test_clock_meridiem(text, h, m):
    s = start(text)
    assert (s.hour, s.minute) == (h, m)
