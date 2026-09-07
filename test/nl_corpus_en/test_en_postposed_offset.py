# -*- coding: utf-8 -*-
"""Offsets whose direction marker follows the duration.

English names a forward offset two ways.  The marker leads in "in two
hours"; it trails in "two hours from now".  Backwards it is "two hours
ago" leading nothing and "two hours earlier" trailing.  All four name the
same instants, so each pair is asserted against one arithmetic gold.

The gold is computed from the anchor with timedelta, never read back from
the parser.  The remainder is asserted everywhere: the defect these cover
left the direction word stranded while the duration resolved, which is a
wrong answer wearing the shape of a right one.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, nomatch, parse, start


@pytest.mark.parametrize("text,delta", [
    ("2 hours from now", timedelta(hours=2)),
    ("two hours from now", timedelta(hours=2)),
    ("5 minutes from now", timedelta(minutes=5)),
    ("1 weeks from now", timedelta(weeks=1)),
    ("3 days from now", timedelta(days=3)),
])
def test_postposed_future_marker(text, delta):
    assert start(text) == ANCHOR + delta
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text,delta", [
    ("5 minutes earlier", timedelta(minutes=5)),
    ("2 hours earlier", timedelta(hours=2)),
    ("3 days earlier", timedelta(days=3)),
])
def test_postposed_past_marker(text, delta):
    assert start(text) == ANCHOR - delta
    assert parse(text)[1] == ""


@pytest.mark.parametrize("lead,trail", [
    ("in 2 hours", "2 hours from now"),
    ("in 5 minutes", "5 minutes from now"),
])
def test_the_two_future_spellings_agree(lead, trail):
    assert start(lead) == start(trail)


@pytest.mark.parametrize("lead,trail", [
    ("5 minutes ago", "5 minutes earlier"),
    ("2 hours ago", "2 hours earlier"),
])
def test_the_two_past_spellings_agree(lead, trail):
    assert start(lead) == start(trail)


@pytest.mark.parametrize("text", ["2 hours", "5 minutes", "3 days"])
def test_a_bare_duration_is_not_a_point_in_time(text):
    """A length is not an instant; extract_duration is the reader for these."""
    nomatch(text)


@pytest.mark.parametrize("text", [
    "later", "earlier", "see you later", "sooner or later",
])
def test_a_bare_direction_word_names_no_time(text):
    """The marker only counts an offset when a duration precedes it."""
    nomatch(text)


def test_now_still_names_the_anchor():
    """"from now" must not swallow the bare present."""
    assert start("now") == ANCHOR
    assert parse("now")[1] == ""


def test_from_still_opens_a_range():
    """"from" as a range preposition is untouched by the offset marker."""
    sp = parse("from monday to friday")[0]
    s, e = sp.start, sp.end
    assert (s.month, s.day) == (7, 3)
    assert (e.month, e.day) == (7, 8)
