# -*- coding: utf-8 -*-
"""A '-' glued directly to a leading digit run ("-3 times", "in -3 days") is
a freestanding signed number. The number regex only matches the digit run, so
the sign falls between tokens; without withdrawal it silently vanishes and
the magnitude parses as a confident positive (COUNT=3, +3 days) instead of
being declined. Regression for the persona-review sign-drop finding."""
from datetime import datetime
from chronologia import extract_recurrence, extract_timespan


def test_negative_count_declined_not_sign_dropped():
    r = extract_recurrence("the 31st every month, -3 times", "en")
    assert r is not None
    # COUNT must NOT be set to 3 -- the sign is not silently dropped
    assert r.recurrence.count is None
    assert "-3" in r.remainder


def test_negative_duration_not_consumed_as_positive():
    anc = datetime(2017, 6, 27, 13, 4)
    r = extract_timespan("in -3 days", "en", anc)
    # must NOT resolve to anchor + 3 days (sign-dropped reading)
    assert r is None


def test_spaced_bullet_still_consumes_as_duration():
    # a '-' that is NOT glued to the digits (markdown-bullet style) is not a
    # sign at all -- "in - 3 days" must consume exactly like "in 3 days"
    anc = datetime(2017, 6, 27, 13, 4)
    plain = extract_timespan("in 3 days", "en", anc)
    bulleted = extract_timespan("in - 3 days", "en", anc)
    assert bulleted is not None
    assert bulleted.span == plain.span
    assert bulleted.remainder == plain.remainder == ""


def test_date_range_with_hyphen_unaffected():
    # digit-before-'-' is a range separator, not a sign: "1914-1918" must
    # still resolve to the full year range
    anc = datetime(2017, 6, 27, 13, 4)
    r = extract_timespan("from 1914-1918", "en", anc)
    assert r is not None
    assert r.span.start.year == 1914
    assert r.span.end.year == 1919


def test_iso_date_unaffected():
    anc = datetime(2017, 6, 27, 13, 4)
    r = extract_timespan("2026-08-05", "en", anc)
    assert r is not None
    assert (r.span.start.year, r.span.start.month, r.span.start.day) == (2026, 8, 5)


def test_utc_offset_unaffected():
    # letter-before-'-' is a zone offset, not a sign: must still parse
    anc = datetime(2017, 6, 27, 13, 4)
    r = extract_timespan("from noon to 3:30 utc+2", "en", anc)
    assert r is not None


def test_spaced_range_typo_is_not_a_range():
    # "1914 -1918" (a spaced range typo, not a glued range) is exempted from
    # withdrawal because the preceding token is itself a number: the second,
    # glued-minus year is not re-consumed as a range end and keeps its own
    # number reading, so its digits still show up in the remainder.  With no
    # range end to bind, the "from" opens a span running to the anchor.
    anc = datetime(2017, 6, 27, 13, 4)
    r = extract_timespan("from 1914 -1918", "en", anc)
    assert r is not None
    assert r.span.start.year == 1914
    assert (r.span.end.year, r.span.end.month, r.span.end.day) == (2017, 6, 27)
    assert r.remainder == "1918"
