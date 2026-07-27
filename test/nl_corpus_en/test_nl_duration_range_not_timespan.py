"""A "for N to M <duration-unit>" phrase is a duration RANGE, not a timespan.

"cook on low for 6 to 8 hours" names a length of time (six-to-eight hours),
not two times of day.  The subtractive-clock reading ("6 to 8" == six minutes
to eight o'clock == 07:54) hijacked such phrases, fabricating a bogus
minute-wide clock span and stranding the duration unit in the remainder --
a silent-wrong.  A phrase whose only temporal content is a "for <duration>"
(a single duration or a duration range) belongs to :func:`extract_duration`;
:func:`extract_timespan` must return ``None``.

The discriminator is the trailing DURATION UNIT (hours/minutes/days/...) with
no clock cue.  A genuine clock range carries a meridiem or an explicit clock
("6 to 8 pm", "from 9 to 5", "3:30 to 4:30") and stays a real timespan; those
are pinned here as regressions so the veto never widens.
"""
from ._corpus import nomatch, start_end, ad, ANCHOR
from datetime import datetime


# -- the veto: a "for N to M <unit>" duration range is not a timespan --------

def test_bare_for_duration_range_hours_is_not_a_timespan():
    # was: 2017-06-28 07:54, remainder "cook on low for hours"  (BOGUS)
    nomatch("cook on low for 6 to 8 hours")


def test_bare_for_duration_range_minutes_is_not_a_timespan():
    # was: 2017-06-28 09:55, remainder "let stand for minutes"  (BOGUS)
    nomatch("let stand for 5 to 10 minutes")


def test_for_duration_range_hours_no_lead_words_is_not_a_timespan():
    # was: 2017-06-28 07:54, remainder "for hours"  (BOGUS)
    nomatch("for 6 to 8 hours")


def test_for_duration_range_double_digit_minutes_is_not_a_timespan():
    nomatch("simmer gently for 20 to 25 minutes")


def test_for_duration_range_hyphen_form_is_not_a_timespan():
    nomatch("bake for 40-45 minutes")


def test_explicit_lead_duration_range_hours_is_not_a_timespan():
    # was: 2017-06-28 06:00..08:00, remainder "hours"  (BOGUS clock range)
    nomatch("from 6 to 8 hours")


def test_explicit_lead_duration_range_minutes_is_not_a_timespan():
    # was: 2017-06-28 05:00..10:00, remainder "minutes"  (BOGUS clock range)
    nomatch("between 5 and 10 minutes")


def test_single_for_duration_is_not_a_timespan():
    # unchanged behaviour: a lone "for <duration>" was already None
    nomatch("for 2 hours")
    nomatch("cook for 20 minutes")


# -- regression pins: real clock ranges still resolve in extract_timespan ----

def test_bare_clock_range_from_to_still_a_timespan():
    s, e = start_end("from 6 to 8")
    assert (s, e) == (ad(datetime(2017, 6, 28, 6, 0)),
                      ad(datetime(2017, 6, 28, 8, 1)))


def test_clock_range_with_meridiem_still_a_timespan():
    s, e = start_end("6 to 8 pm")
    assert (s, e) == (ad(datetime(2017, 6, 27, 18, 0)),
                      ad(datetime(2017, 6, 27, 20, 1)))


def test_between_clock_range_still_a_timespan():
    s, e = start_end("between 3 and 5")
    assert (s, e) == (ad(datetime(2017, 6, 28, 3, 0)),
                      ad(datetime(2017, 6, 28, 5, 1)))


def test_working_day_clock_range_still_a_timespan():
    s, e = start_end("from 9 to 5")
    assert (s, e) == (ad(datetime(2017, 6, 28, 9, 0)),
                      ad(datetime(2017, 6, 28, 17, 1)))


def test_meridiem_bracketed_clock_range_still_a_timespan():
    s, e = start_end("from 9am to 5pm")
    assert (s, e) == (ad(datetime(2017, 6, 28, 9, 0)),
                      ad(datetime(2017, 6, 28, 17, 1)))


def test_explicit_clock_literal_range_still_a_timespan():
    s, e = start_end("3:30 to 4:30")
    assert (s, e) == (ad(datetime(2017, 6, 28, 3, 30)),
                      ad(datetime(2017, 6, 28, 4, 31)))


def test_subtractive_clock_still_reads_when_no_unit_trails():
    # "10 to 6" == ten minutes to six == 05:50 -- a real time, untouched
    s, e = start_end("10 to 6")
    assert (s, e) == (ad(datetime(2017, 6, 28, 5, 50)),
                      ad(datetime(2017, 6, 28, 5, 51)))
