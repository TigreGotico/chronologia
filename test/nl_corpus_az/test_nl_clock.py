# -*- coding: utf-8 -*-
"""Clock readings in Azerbaijani."""
import pytest
from ._corpus import nomatch, parse, start


@pytest.mark.parametrize("text,h,m", [
    ("15:30", 15, 30), ("09:00", 9, 0), ("23:59", 23, 59),
    ("06:15", 6, 15), ("00:00", 0, 0), ("12:00", 12, 0)])
def test_iso_clock(text, h, m):
    s = start(text)
    assert (s.hour, s.minute) == (h, m)


@pytest.mark.parametrize("text,h", [
    ("saat 3", 3), ("saat 9", 9), ("saat 7", 7), ("saat 11", 11)])
def test_at_hour(text, h):
    assert start(text).hour == h


# -- the daypart adverbial, which Azerbaijani puts before the time phrase ---
# "axşam saat səkkiz" is the ordinary order; the postposed one is the marked
# variant.  Both must read the same evening hour, because dropping the marker
# is not a missed parse but a twelve-hour error.
@pytest.mark.parametrize("text,h", [
    ("axşam saat səkkiz", 20),
    ("saat səkkiz axşam", 20),
    ("axşam saat 8", 20),
    ("axşam 8", 20),
    ("səhər saat doqquz", 9),
    ("saat doqquz səhər", 9)])
def test_daypart_marker_either_side(text, h):
    s = start(text)
    assert (s.hour, s.minute) == (h, 0)
    assert parse(text).remainder == ""


def test_daypart_marker_over_an_iso_clock():
    s = start("axşam 20:00")
    assert (s.hour, s.minute) == (20, 0)


def test_bare_hour_without_daypart_stays_on_the_named_hour():
    # No marker, no twelve-hour shift: the hour is read exactly as named.
    s = start("saat 8")
    assert (s.hour, s.minute) == (8, 0)


@pytest.mark.parametrize("text", ["axşam", "səhər", "axşam saat"])
def test_daypart_word_alone_is_not_a_clock(text):
    # The marker licenses a bare hour; on its own it names no time at all.
    nomatch(text)
