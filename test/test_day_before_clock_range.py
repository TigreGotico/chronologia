"""A day named before a range of clock times dates the range.

"between 10am and 11am on monday" already reads Monday 10:00-11:00; the same
words with the day first, "monday between 10 and 11 am", read the anchor's own
day with "monday" left in the remainder, and "tomorrow between 10am and 11am"
read today.  The day before the range's lead now dates the range as the day
after it does.  Expected values are counted from the anchor, Friday
2026-11-27 10:00.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

A = datetime(2026, 11, 27, 10, 0)     # a Friday
MON = (2026, 11, 30)
SAT = (2026, 11, 28)


def _read(text, lang):
    r = extract_timespan(text, lang, A)
    assert r is not None, text
    s, e = r.span.start, r.span.end
    return (s.year, s.month, s.day, s.hour), (e.year, e.month, e.day, e.hour), r.remainder


@pytest.mark.parametrize("text,lang,day", [
    ("monday between 10 and 11 am", "en", MON),
    ("monday from 10 to 11 am", "en", MON),
    ("on monday between 10am and 11am", "en", MON),
    ("tomorrow between 10am and 11am", "en", SAT),
    ("lundi entre 10h et 11h", "fr", MON),
    ("demain entre 10h et 11h", "fr", SAT),
    ("le lundi 30 novembre entre 10h et 11h", "fr", MON),
    ("montag zwischen 10 und 11 uhr", "de", MON),
    ("segunda-feira entre as 10h e as 11h", "pt", MON),
])
def test_the_day_before_the_range_dates_it(text, lang, day):
    start, end, rem = _read(text, lang)
    assert (start, end[:3], rem) == ((*day, 10), day, "")
    assert end[3] == 11


def test_words_before_the_day_stay_in_the_remainder():
    start, _end, rem = _read("the meeting is on monday from 10am to 11am", "en")
    assert start == (*MON, 10) and rem == "the meeting is"


def test_a_range_that_crosses_midnight_starts_on_the_day():
    start, end, rem = _read("tomorrow from 11pm to 1am", "en")
    assert (start, end, rem) == ((*SAT, 23), (2026, 11, 29, 1), "")


@pytest.mark.parametrize("text,lang", [
    ("between 10am and 11am on monday", "en"),      # the day after: unchanged
    ("entre 10h et 11h lundi", "fr"),
])
def test_the_day_after_the_range_still_dates_it(text, lang):
    start, _end, rem = _read(text, lang)
    assert start == (*MON, 10) and rem == ""


def test_a_range_of_dates_is_not_moved_onto_the_day():
    # the range names its own dates, so the day before it stays unread
    r = extract_timespan("monday from june 3 to june 5", "en", A)
    assert r is not None
    assert (r.span.start.month, r.span.start.day) == (6, 3)


def test_a_verb_particle_before_a_named_day_stays_in_the_remainder():
    # "on" before "tomorrow" belongs to the verb (_fold_date_article)
    start, _end, rem = _read("turn the lights on tomorrow from 10am to 11am", "en")
    assert start == (*SAT, 10) and rem == "turn the lights on"


def test_an_end_read_without_the_anchor_day_is_not_moved():
    # "now" is the anchor instant: the day before the range does not move it
    r = extract_timespan("monday from now to 11am", "en", A)
    assert r is not None
    assert (r.span.start.day, r.span.start.hour, r.remainder) == (27, 10, "monday")


def test_a_zoned_end_moves_with_the_day():
    # the same range as "from noon to 3:30 utc+2", one day on
    r = extract_timespan("tomorrow from noon to 3:30 utc+2", "en", A)
    base = extract_timespan("from noon to 3:30 utc+2", "en", A)
    assert r is not None and base is not None and r.remainder == ""
    assert r.span.start.day == base.span.start.day + 1
    assert (r.span.start.hour, r.span.end.hour, r.span.end.minute) == (
        base.span.start.hour, base.span.end.hour, base.span.end.minute)
