# -*- coding: utf-8 -*-
"""The Tamil clock, pinned in BOTH directions.

The single worst thing this locale could do is run the clock backwards.
ஒன்பதரை is nine-and-a-half, which is 9:30; a reader carrying over the European
"half nine" habit subtracts and gets 8:30, and every reading in the language is
then an hour out with nothing in the output to show it.  Each forward case
below therefore asserts the forward minute AND denies the mirrored one, and the
one construction that genuinely counts backwards -- குறைவு, "less" -- is pinned
just as hard in its own direction against its own mirror.
"""
import pytest

from ._corpus import minute_at, nomatch, start_end


@pytest.mark.parametrize("text,expected", [
    # the fused half hour: the fraction அரை suffixed to the numeral for nine.
    ("ஒன்பதரை", minute_at(2027, 5, 13, 9, 30)),
    ("ஒன்பதரை மணி", minute_at(2027, 5, 13, 9, 30)),
    # the quarter, the numeral carrying the emphatic -ஏ and கால் after it.
    ("ஒன்பதே கால்", minute_at(2027, 5, 13, 9, 15)),
    ("ஒன்பதே கால் மணி", minute_at(2027, 5, 13, 9, 15)),
])
def test_the_fused_fraction_counts_forward(text, expected):
    assert start_end(text) == expected


@pytest.mark.parametrize("text,wrong_hour,wrong_minute", [
    ("ஒன்பதரை", 8, 30),
    ("ஒன்பதே கால்", 8, 45),
])
def test_the_fused_fraction_is_not_the_european_subtractive_reading(
        text, wrong_hour, wrong_minute):
    """The refutation of the forward reading, stated as its own case: a
    backward clock is silently wrong in every phrase it touches."""
    got = start_end(text)[0]
    assert (got.hour, got.minute) != (wrong_hour, wrong_minute)


@pytest.mark.parametrize("text,expected", [
    # மேல் "above, past" -- the minutes are counted forward from the named hour
    ("மூன்று மணிக்கு பத்து நிமிடம் மேல்", minute_at(2027, 5, 13, 3, 10)),
    ("ஒன்பது மணிக்கு இருபது நிமிடம் மேல்", minute_at(2027, 5, 13, 9, 20)),
    ("பதினொன்று மணிக்கு பதினைந்து நிமிடம் மேல்", minute_at(2027, 5, 13, 11, 15)),
])
def test_mel_counts_forward_from_the_named_hour(text, expected):
    assert start_end(text) == expected


@pytest.mark.parametrize("text,expected", [
    # குறைவு "less" -- the named hour is the UPCOMING one, so the reading
    # lands in the hour before it: six less fifteen minutes is 5:45.
    ("ஆறு மணிக்கு பதினைந்து நிமிடம் குறைவு", minute_at(2027, 5, 13, 5, 45)),
    ("பத்து மணிக்கு பத்து நிமிடம் குறைவு", minute_at(2027, 5, 13, 9, 50)),
    ("மூன்று மணிக்கு இருபது நிமிடம் குறைவு", minute_at(2027, 5, 13, 2, 40)),
])
def test_kuraivu_counts_back_off_the_upcoming_hour(text, expected):
    assert start_end(text) == expected


@pytest.mark.parametrize("text,forbidden", [
    # the mirror of each backward case: reading குறைவு forward would put the
    # minutes INTO the named hour instead of before it.
    ("ஆறு மணிக்கு பதினைந்து நிமிடம் குறைவு", (6, 15)),
    ("பத்து மணிக்கு பத்து நிமிடம் குறைவு", (10, 10)),
    ("மூன்று மணிக்கு இருபது நிமிடம் குறைவு", (3, 20)),
])
def test_kuraivu_is_not_read_as_a_forward_tail(text, forbidden):
    got = start_end(text)[0]
    assert (got.hour, got.minute) != forbidden


@pytest.mark.parametrize("text,expected", [
    ("ஏழு மணி", minute_at(2027, 5, 13, 7, 0)),
    ("எட்டு மணிக்கு", minute_at(2027, 5, 13, 8, 0)),
    ("இருபது மணி", minute_at(2027, 5, 12, 20, 0)),
    # an unmarked minute tail takes the forward direction the fused
    # fractions establish.
    ("ஏழு மணி இருபது நிமிடம்", minute_at(2027, 5, 13, 7, 20)),
])
def test_the_bare_hour_and_its_unmarked_minute_tail(text, expected):
    assert start_end(text) == expected


@pytest.mark.parametrize("text", [
    "ஒன்பதே முக்கால்",
    "ஒன்பது மணி முக்கால்",
])
def test_three_quarters_refuses(text):
    """முக்கால் is a fraction word of the language, but no source works it out
    on a clock.  Reading it as three quarters past by analogy with அரை and
    கால் would be an analogy, not evidence, so the phrase answers nothing --
    and the numeral inside it must not survive as a bare day-of-month either."""
    nomatch(text)
