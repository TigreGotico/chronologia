"""The hour-letter clock is a clock behind a clock marker, or alone.

Italian writes "21h30" where a clock marker already announces a clock.  Said
alone, the whole utterance is the clock.  Inside a sentence with no marker it
is a length, a coordinate or a citation, and is not read.
"""
import pytest

from ._corpus import ANCHOR, parse, span

MARKED = [
    ('alle 21h30', 21, 30),
    ('ore 21h30', 21, 30),
    ('alle 20h', 20, 0),
]

# Said alone, the whole utterance is the clock.  At 13:04, 21:30 and 20:00
# are still ahead today and 02:30 is tomorrow.
# Words after the clock do not take its marker away.  "alle" ("a" + "le") is
# the clock marker and an article at once.  21:30 and 15:00 are still ahead
# today at 13:04.
TRAILING = [
    ('ci vediamo alle 21h30 al bar', 21, 30),
    ('alle 21h30 al bar', 21, 30),
    ('alle 15h con Marco', 15, 0),
]

BARE = [
    ('21h30', 27, 21, 30),
    ('20h', 27, 20, 0),
    ('2h30', 28, 2, 30),
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


@pytest.mark.parametrize("text,day,hour,minute", BARE)
def test_bare_h_notation_alone_is_a_clock(text, day, hour, minute):
    s = span(text)
    assert (s.start.month, s.start.day) == (6, day)
    assert (s.start.hour, s.start.minute) == (hour, minute)
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text,hour,minute", TRAILING)
def test_marked_h_clock_with_words_after_it_still_reads(text, hour, minute):
    s = span(text)
    assert (s.start.month, s.start.day) == (6, 27)
    assert (s.start.hour, s.start.minute) == (hour, minute)


@pytest.mark.parametrize("text", [
    'sono le 10 e mezza',
])
def test_a_plain_number_with_a_half_after_a_marker_is_a_clock(text):
    """Only an hour written with the letter stays a bare hour before a
    fraction.  10:30 has passed at 13:04, so the clock is tomorrow's."""
    s = span(text)
    assert (s.start.month, s.start.day, s.start.hour, s.start.minute) == (
        6, 28, 10, 30)

