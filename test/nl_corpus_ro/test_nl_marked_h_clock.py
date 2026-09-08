"""The hour-letter clock is a clock only behind a clock marker.

Romanian writes "21h30" where a clock marker already announces a clock; a
bare "21h30" is a duration, a coordinate or a citation to a French source, so
the phrase yields nothing at all rather than the hour alone with "h30" left
over in the remainder.
"""
import pytest

from ._corpus import ANCHOR, nomatch, parse, span

MARKED = [
    ('la ora 21h30', 21, 30),
    ('la ora 20h', 20, 0),
]

BARE = [
    '21h30',
    '20h',
    '2h30',
]


@pytest.mark.parametrize("text,hour,minute", MARKED)
def test_marked_h_clock_reads_hour_and_minute(text, hour, minute):
    s = span(text)
    assert (s.start.year, s.start.month, s.start.day) == (
        ANCHOR.year, ANCHOR.month, ANCHOR.day)
    assert (s.start.hour, s.start.minute) == (hour, minute)


@pytest.mark.parametrize("text,hour,minute", MARKED)
def test_marked_h_clock_consumes_the_whole_phrase(text, hour, minute):
    # the marker and the letter both belong to the clock: leaving either in
    # the remainder is the half-read this pins against.
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text", BARE)
def test_bare_h_notation_is_not_a_clock(text):
    nomatch(text)
