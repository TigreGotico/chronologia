# -*- coding: utf-8 -*-
"""A spoken length is not a point in time.

The noun that opens a clock time is, in several languages, the same one
that counts hours. "2 hodiny 30 minut" is two and a half hours, and reading
it as a clock answers two o'clock and leaves the thirty minutes behind --
a wrong answer wearing the shape of a right one.

A phrase the duration reader consumes whole is a length. The clock reading
is refused for those, and only for those: a clock time with a preposition
in front of it is consumed whole by the clock and only partly by the
duration reader, so it is unaffected.
"""
from datetime import datetime

import pytest

from chronologia import extract_duration, extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)


@pytest.mark.parametrize("text,lang,seconds", [
    ("2 hodiny 30 minut", "cs", 9000),
    ("2 heures 30 minutes", "fr", 9000),
    ("два часа и тридесет минути", "bg", 9000),
    ("2 sata 30 minuta", "hr", 9000),
    ("2 hodiny 30 minút", "sk", 9000),
])
def test_a_spoken_length_names_no_point_in_time(text, lang, seconds):
    assert extract_timespan(text, lang, ANCHOR) is None
    got = extract_duration(text, lang)
    assert got.duration.total_seconds() == seconds
    assert got.remainder == ""


@pytest.mark.parametrize("text,lang,hour", [
    ("ve 2 hodiny", "cs", 2),
    ("à 2 heures", "fr", 2),
    ("23:30", "sk", 23),
    ("u 23:30", "hr", 23),
    ("at 9am", "en", 9),
])
def test_a_clock_time_still_reads(text, lang, hour):
    got = extract_timespan(text, lang, ANCHOR)
    assert got is not None, text
    assert got.span.start.hour == hour
    assert got.remainder == ""


@pytest.mark.parametrize("text,lang", [("in 2 hours", "en"), ("o 2 hodiny", "sk")])
def test_an_offset_still_reads(text, lang):
    """The same words count an offset; that reading is not a clock either."""
    got = extract_timespan(text, lang, ANCHOR)
    assert got is not None, text
    assert (got.span.start.hour, got.span.start.minute) == (15, 4)
