"""Recurrence: a recurring phrase -> an RFC 5545 ``RRULE``.

The contract is ``extract_recurrence(text, "en")`` -> the repo's
:class:`~chronologia.recurrence.Recurrence` plus the leftover text.  Expected
values are the hand-written canonical RRULE strings.
"""
import pytest

from chronologia.extract import extract_recurrence

LANG = "en"

# (text, expected RRULE string, expected remainder)
_CASES = [
    ("every friday", "FREQ=WEEKLY;BYDAY=FR", ""),
    ("every monday", "FREQ=WEEKLY;BYDAY=MO", ""),
    ("every day", "FREQ=DAILY", ""),
    ("every week", "FREQ=WEEKLY", ""),
    ("every month", "FREQ=MONTHLY", ""),
    ("every year", "FREQ=YEARLY", ""),
    ("every other week", "FREQ=WEEKLY;INTERVAL=2", ""),
    ("every 2 weeks", "FREQ=WEEKLY;INTERVAL=2", ""),
    ("every other tuesday", "FREQ=WEEKLY;INTERVAL=2;BYDAY=TU", ""),
    ("every weekday", "FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR", ""),
    ("daily", "FREQ=DAILY", ""),
    ("weekly", "FREQ=WEEKLY", ""),
    ("monthly", "FREQ=MONTHLY", ""),
    ("annually", "FREQ=YEARLY", ""),
    # single-word frequency adverbs and the weekday/weekend sets: no new
    # mechanism -- these bind the same lone-freq-word / weekly-BYDAY reading
    # as "daily"/"weekly"/"every weekday" above.
    ("fortnightly", "FREQ=WEEKLY;INTERVAL=2", ""),
    # "biweekly" is ambiguous in careful usage (Merriam-Webster's usage note:
    # both "every two weeks" and "twice a week" are attested); this resolver
    # takes the standard scheduling/RRULE convention -- every two weeks --
    # same as "fortnightly".  The rarer "twice a week" (a frequency-*count*
    # reading, not a plain INTERVAL bump) is a documented follow-up.
    ("biweekly", "FREQ=WEEKLY;INTERVAL=2", ""),
    ("quarterly", "FREQ=MONTHLY;INTERVAL=3", ""),
    # a calendar quarter is three months, so "every quarter" is the same
    # MONTHLY;INTERVAL=3 rule as the lone "quarterly" adverb; "every other
    # quarter" bumps it to every sixth month.  The quarter noun is read ONLY
    # under an "every" determiner -- the bare "quarter" stays a duration/clock
    # fraction (see the guards in test_nl_duration / clock tests).
    ("every quarter", "FREQ=MONTHLY;INTERVAL=3", ""),
    ("every other quarter", "FREQ=MONTHLY;INTERVAL=6", ""),
    # an explicit trailing occurrence count "<N> times" folds to COUNT -- the
    # RFC 5545 total.  "0 times" is degenerate (no occurrences): declined, left
    # unconsumed in the remainder rather than emitted as COUNT=0.
    ("every day 3 times", "FREQ=DAILY;COUNT=3", ""),
    ("daily 5 times", "FREQ=DAILY;COUNT=5", ""),
    ("every monday 4 times", "FREQ=WEEKLY;COUNT=4;BYDAY=MO", ""),
    ("every day 0 times", "FREQ=DAILY", "0 times"),
    ("on weekdays", "FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR", ""),
    ("on weekends", "FREQ=WEEKLY;BYDAY=SA,SU", ""),
    ("first monday of every month", "FREQ=MONTHLY;BYDAY=1MO", ""),
    ("last friday of every month", "FREQ=MONTHLY;BYDAY=-1FR", ""),
    ("the third thursday of november", "FREQ=YEARLY;BYMONTH=11;BYDAY=3TH", ""),
    # date-anchored recurrence: the single-span engine reads the date part.
    ("every 10th of may", "FREQ=YEARLY;BYMONTH=5;BYMONTHDAY=10", ""),
    ("every may 10", "FREQ=YEARLY;BYMONTH=5;BYMONTHDAY=10", ""),
    ("every year on may 10", "FREQ=YEARLY;BYMONTH=5;BYMONTHDAY=10", ""),
    ("the 10th of every month", "FREQ=MONTHLY;BYMONTHDAY=10", ""),
    ("every month on the 10th", "FREQ=MONTHLY;BYMONTHDAY=10", ""),
    ("the 1st of every month", "FREQ=MONTHLY;BYMONTHDAY=1", ""),
    # an explicit "day" noun between the ordinal and "of" must not drop the
    # day-of-month constraint (the bare "the 1st of every month" above proves
    # the lift); and the bare "last" marker is the month-end idiom BYMONTHDAY=-1.
    ("the first day of every month", "FREQ=MONTHLY;BYMONTHDAY=1", ""),
    ("the 15th day of every month", "FREQ=MONTHLY;BYMONTHDAY=15", ""),
    ("the last of every month", "FREQ=MONTHLY;BYMONTHDAY=-1", ""),
    ("the last day of every month", "FREQ=MONTHLY;BYMONTHDAY=-1", ""),
    # a trailing "<N> times" count must not be swallowed as the day-of-month:
    # the ordinal day AND the COUNT both survive.
    ("the 3rd of every month 5 times", "FREQ=MONTHLY;COUNT=5;BYMONTHDAY=3", ""),
    ("the last day of every month 3 times", "FREQ=MONTHLY;COUNT=3;BYMONTHDAY=-1", ""),
    ("every month 5 times", "FREQ=MONTHLY;COUNT=5", ""),
    ("every christmas", "FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25", ""),
    ("every halloween", "FREQ=YEARLY;BYMONTH=10;BYMONTHDAY=31", ""),
    ("every valentines day", "FREQ=YEARLY;BYMONTH=2;BYMONTHDAY=14", ""),
    ("every thanksgiving", "FREQ=YEARLY;BYMONTH=11;BYDAY=4TH", ""),
    # clock pin: BYHOUR / BYMINUTE fold onto the rule.
    ("daily at 9", "FREQ=DAILY;BYHOUR=9", ""),
    ("every day at 9am", "FREQ=DAILY;BYHOUR=9", ""),
    ("daily at noon", "FREQ=DAILY;BYHOUR=12", ""),
    ("every day at midnight", "FREQ=DAILY;BYHOUR=0", ""),
    ("every wednesday at 9", "FREQ=WEEKLY;BYDAY=WE;BYHOUR=9", ""),
    ("every wednesday at 9:30", "FREQ=WEEKLY;BYDAY=WE;BYHOUR=9;BYMINUTE=30", ""),
    ("every 10th of may at 9am", "FREQ=YEARLY;BYMONTH=5;BYMONTHDAY=10;BYHOUR=9", ""),
    # Elliptical nth-weekday: people drop the "of the month" tail in speech.
    # "every last friday" means what "every last friday of the month" means --
    # the tail is redundant once "every" has framed the phrase as recurring.
    ("every last friday", "FREQ=MONTHLY;BYDAY=-1FR", ""),
    ("every first friday", "FREQ=MONTHLY;BYDAY=1FR", ""),
    ("every last monday", "FREQ=MONTHLY;BYDAY=-1MO", ""),
    # from two upwards a bare ordinal+weekday is the interval reading ("every
    # third thursday" = every three thursdays); the month-of reading needs the
    # explicit tail.  Only "first" is unambiguous, an interval of one being
    # degenerate.
    ("every third thursday", "FREQ=WEEKLY;INTERVAL=3;BYDAY=TH", ""),
    ("every third thursday of the month", "FREQ=MONTHLY;BYDAY=3TH", ""),
    ("every second tuesday", "FREQ=WEEKLY;INTERVAL=2;BYDAY=TU", ""),
    ("every second tuesday of the month", "FREQ=MONTHLY;BYDAY=2TU", ""),
    ("every first friday", "FREQ=MONTHLY;BYDAY=1FR", ""),
    ("every first friday of the month", "FREQ=MONTHLY;BYDAY=1FR", ""),
    ("every last friday at 5pm", "FREQ=MONTHLY;BYDAY=-1FR;BYHOUR=17", ""),
    # Elliptical day-of-month: "every 1st" == "every 1st of the month" ==
    # the already-working "the 1st of every month".
    ("every 1st of the month", "FREQ=MONTHLY;BYMONTHDAY=1", ""),
    ("every 1st", "FREQ=MONTHLY;BYMONTHDAY=1", ""),
    ("every 15th", "FREQ=MONTHLY;BYMONTHDAY=15", ""),
    ("every 15th of the month", "FREQ=MONTHLY;BYMONTHDAY=15", ""),
    ("every 1st at 9", "FREQ=MONTHLY;BYMONTHDAY=1;BYHOUR=9", ""),
    # "once a <unit>": one occurrence per period IS the plain per-period
    # frequency -- once a week is exactly FREQ=WEEKLY, so the count word
    # contributes no RRULE part of its own.
    ("once a day", "FREQ=DAILY", ""),
    ("once a week", "FREQ=WEEKLY", ""),
    ("once a month", "FREQ=MONTHLY", ""),
    ("once a year", "FREQ=YEARLY", ""),
    ("once per week", "FREQ=WEEKLY", ""),
    ("once a week on monday", "FREQ=WEEKLY;BYDAY=MO", ""),
    ("once a week on friday", "FREQ=WEEKLY;BYDAY=FR", ""),
    ("once a week on monday at 9", "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9", ""),
    ("once a day at 9:30", "FREQ=DAILY;BYHOUR=9;BYMINUTE=30", ""),
]


# Movable-feast recurrence: a real object whose occurrences() works but whose
# to_string() refuses to lie (no RFC 5545 rule expresses a computus/lunar feast).
from chronologia.recurrence import HolidayRecurrence   # noqa: E402


@pytest.mark.parametrize("text,key", [
    ("every easter", "easter"),
    ("every good friday", "good_friday"),
])
def test_movable_holiday_recurrence(text, key):
    got = extract_recurrence(text, LANG)
    assert got is not None
    assert got[0] == HolidayRecurrence(key)
    assert got[1] == ""
    with pytest.raises(ValueError):
        got[0].to_string()


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


# Bounded recurrence: an "until <date>" folds to UNTIL; a "for <duration>"
# folds to COUNT -- the number of occurrences the fixed-width duration spans at
# the rule's frequency (14 days -> 14 daily hits; 6 weeks -> 6 weekly hits).
# The UNTIL date is resolved against a fixed anchor so the RRULE is stable.
from datetime import datetime               # noqa: E402

_BOUND_ANCHOR = datetime(2017, 6, 27, 13, 4)
_BOUND_CASES = [
    ("every friday until june", "FREQ=WEEKLY;UNTIL=20170601T000000;BYDAY=FR", ""),
    ("every monday until december", "FREQ=WEEKLY;UNTIL=20171201T000000;BYDAY=MO", ""),
    ("daily until 2020", "FREQ=DAILY;UNTIL=20200101T000000", ""),
    ("every week till march", "FREQ=WEEKLY;UNTIL=20170301T000000", ""),
    ("daily for two weeks", "FREQ=DAILY;COUNT=14", ""),
    ("daily for a week", "FREQ=DAILY;COUNT=7", ""),
    ("every day for 3 days", "FREQ=DAILY;COUNT=3", ""),
    ("every monday for 6 weeks", "FREQ=WEEKLY;COUNT=6;BYDAY=MO", ""),
    ("every friday for three weeks", "FREQ=WEEKLY;COUNT=3;BYDAY=FR", ""),
    ("weekly for 4 weeks", "FREQ=WEEKLY;COUNT=4", ""),
    # COUNT and UNTIL are mutually exclusive (RFC 5545): an explicit UNTIL bound
    # wins and the trailing "N times" is left in the remainder -- it must NOT
    # add COUNT onto the UNTIL rule (which raised an unhandled ValueError out of
    # the public extractor).
    ("every day 5 times until march", "FREQ=DAILY;UNTIL=20170301T000000", "5 times"),
]


@pytest.mark.parametrize("text,rrule,remainder", _BOUND_CASES)
def test_bounded_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=_BOUND_ANCHOR)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


# adversarial: a one-off reference is not a recurrence.
@pytest.mark.parametrize("text", [
    "friday", "next friday", "in 3 days", "june 5th",
    "I went to the office", "the weekend was fun",
    # The elliptical readings fire ONLY under an explicit "every": without it
    # these are single dates, not rules.  "last friday" is the friday just
    # gone; "the 1st" is one day of one month.
    "last friday", "the last friday", "the 1st", "the 15th", "first friday",
    "the first friday", "on the 1st",
    # a frequency *count* above one has no single-RRULE reading (it needs
    # BYSETPOS / per-period COUNT), so it is left unread rather than guessed
    # into a wrong interval.
    "twice a week", "three times a month", "twice a day", "3 times a day",
    # a bare count word with no period names nothing.
    "once", "once a", "once a friday",
])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None


# A cardinal count before a UNIT is an INTERVAL, never a day-of-month: the
# elliptical BYMONTHDAY reading must never swallow "every 2 weeks".  A bare
# cardinal with no unit and no ordinal surface ("every 2") is not evidence
# enough for either reading and stays unread.
@pytest.mark.parametrize("text,rrule", [
    ("every 2 weeks", "FREQ=WEEKLY;INTERVAL=2"),
    ("every 3 weeks", "FREQ=WEEKLY;INTERVAL=3"),
    ("every 2 days", "FREQ=DAILY;INTERVAL=2"),
    ("every 2 months", "FREQ=MONTHLY;INTERVAL=2"),
    ("every 6 months", "FREQ=MONTHLY;INTERVAL=6"),
])
def test_cardinal_plus_unit_stays_an_interval(text, rrule):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule


@pytest.mark.parametrize("text", ["every 2", "every 5"])
def test_bare_cardinal_under_every_is_not_a_day_of_month(text):
    assert extract_recurrence(text, LANG) is None


# A bare ordinal + weekday under "every" is the INTERVAL reading from two
# upwards ("every third tuesday" = every three tuesdays); only "first" and
# "last" fire the monthly nth-weekday reading bare, and the monthly reading
# from two upwards needs an explicit "of the month" tail.  That ruling is a
# fact about the *phrase*, so the digit surface and the spelled surface must
# land on the same rule -- and neither may drop the weekday to the remainder.
@pytest.mark.parametrize("digit,spelled,rrule", [
    ("every 2nd friday", "every second friday", "FREQ=WEEKLY;INTERVAL=2;BYDAY=FR"),
    ("every 3rd tuesday", "every third tuesday", "FREQ=WEEKLY;INTERVAL=3;BYDAY=TU"),
    ("every 4th monday", "every fourth monday", "FREQ=WEEKLY;INTERVAL=4;BYDAY=MO"),
    ("every 2nd sunday", "every second sunday", "FREQ=WEEKLY;INTERVAL=2;BYDAY=SU"),
    ("every 3rd saturday", "every third saturday", "FREQ=WEEKLY;INTERVAL=3;BYDAY=SA"),
])
def test_digit_and_spelled_ordinal_weekday_agree(digit, spelled, rrule):
    for text in (digit, spelled):
        got = extract_recurrence(text, LANG)
        assert got is not None, f"{text!r} did not parse as a recurrence"
        assert got[0].to_string() == rrule, text
        assert got[1] == "", f"{text!r} stranded {got[1]!r} in the remainder"


# The ordinal-weekday ruling must not cost the readings that surround it: a
# bare ordinal with no weekday is still a day of the month, an explicit "of
# the month" tail still buys the monthly nth-weekday reading, and "first" /
# "last" still fire bare.
@pytest.mark.parametrize("text,rrule", [
    ("every 1st", "FREQ=MONTHLY;BYMONTHDAY=1"),
    ("every 15th", "FREQ=MONTHLY;BYMONTHDAY=15"),
    ("every 3rd tuesday of the month", "FREQ=MONTHLY;BYDAY=3TU"),
    ("every 2nd friday of the month", "FREQ=MONTHLY;BYDAY=2FR"),
    ("every first friday", "FREQ=MONTHLY;BYDAY=1FR"),
    ("every 1st friday", "FREQ=MONTHLY;BYDAY=1FR"),
    ("every last friday", "FREQ=MONTHLY;BYDAY=-1FR"),
    ("every 2 weeks", "FREQ=WEEKLY;INTERVAL=2"),
])
def test_ordinal_readings_around_the_weekday_ruling(text, rrule):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == ""


# "weekend" is the sibling class noun of "weekday" and reads in the same
# determiner + class-noun frame; the days come from the locale's weekend
# convention (Saturday+Sunday in en).  The bare noun still names one weekend,
# not a rule, so it stays unread without "on" or "every".
@pytest.mark.parametrize("text,rrule", [
    ("every weekend", "FREQ=WEEKLY;BYDAY=SA,SU"),
    ("on weekends", "FREQ=WEEKLY;BYDAY=SA,SU"),
    ("every weekday", "FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"),
    ("on weekdays", "FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"),
])
def test_weekend_and_weekday_class_nouns(text, rrule):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == ""


@pytest.mark.parametrize("text", ["weekend", "weekends", "the weekend was fun"])
def test_bare_weekend_is_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None


import datetime as _dt


@pytest.mark.parametrize("anchor", [
    _dt.datetime(2017, 6, 27, 13, 4),   # non-leap year
    _dt.datetime(2020, 1, 1),           # leap year
])
@pytest.mark.parametrize("text", ["every 29th of february", "every february 29th"])
def test_leap_day_recurrence_is_anchor_independent(text, anchor):
    # A recurring date is well-formed independently of whether the anchor's own
    # year contains it: "every 29th of february" must be the leap-day rule
    # YEARLY;BYMONTH=2;BYMONTHDAY=29 whatever the anchor.  Regression: the yearly
    # branch resolved the date to a concrete datetime, which is None in a
    # non-leap year, so the frame was dropped and the greedy catch-all mis-read
    # it as MONTHLY;BYMONTHDAY=29 (firing 11x a year).
    got = extract_recurrence(text, LANG, anchor=anchor)
    assert got is not None
    assert got[0].to_string() == "FREQ=YEARLY;BYMONTH=2;BYMONTHDAY=29"
    assert got[1] == ""


@pytest.mark.parametrize("text", [
    "every 31st of april",    # April never has a 31st
    "every 30th of february",
])
def test_impossible_recurring_date_is_no_recurrence(text):
    # A named date that recurs in no year is not a recurrence -- and must NOT
    # fall through to a wrong MONTHLY;BYMONTHDAY rule.
    assert extract_recurrence(text, LANG,
                              anchor=_dt.datetime(2017, 6, 27, 13, 4)) is None


import datetime as _dt2


@pytest.mark.parametrize("text,rrule", [
    ("every 2 weeks on tuesday", "FREQ=WEEKLY;INTERVAL=2;BYDAY=TU"),
    ("every 3 months on the 5th", "FREQ=MONTHLY;INTERVAL=3;BYMONTHDAY=5"),
    ("every 6 months on the 15th", "FREQ=MONTHLY;INTERVAL=6;BYMONTHDAY=15"),
])
def test_every_n_unit_with_trailing_placement(text, rrule):
    # "every N <unit>" may carry a trailing "on <weekday>" / "on the <Nth>" that
    # pins the day. Regression: the units branch of _recur_every ignored it, so
    # BYDAY/BYMONTHDAY were dropped, the qualifier stranded in the remainder, and
    # occurrences() silently fell back to the anchor's own weekday/day.
    got = extract_recurrence(text, LANG, anchor=_dt2.datetime(2017, 6, 28, 13, 4))
    assert got is not None
    assert got[0].to_string() == rrule
    assert got[1] == ""
