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
    # an interval/quarter monthly rule takes a day-of-month placement qualifier,
    # preposed ("the Nth of ...") or postposed ("... on the Nth"), just like
    # "every N months on the Nth" -- the day used to be dropped for these.
    ("the 15th of every 2 months", "FREQ=MONTHLY;INTERVAL=2;BYMONTHDAY=15", ""),
    ("the 15th of every 3 months", "FREQ=MONTHLY;INTERVAL=3;BYMONTHDAY=15", ""),
    ("every quarter on the 15th", "FREQ=MONTHLY;INTERVAL=3;BYMONTHDAY=15", ""),
    ("the 15th of every quarter", "FREQ=MONTHLY;INTERVAL=3;BYMONTHDAY=15", ""),
    ("the first day of every quarter", "FREQ=MONTHLY;INTERVAL=3;BYMONTHDAY=1", ""),
    ("every other quarter on the 3rd", "FREQ=MONTHLY;INTERVAL=6;BYMONTHDAY=3", ""),
    ("the last day of every quarter", "FREQ=MONTHLY;INTERVAL=3;BYMONTHDAY=-1", ""),
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
    # R114: "second-to-last" (and its synonyms "penultimate"/"next-to-last")
    # must map to BYDAY=-2, NOT silently collapse onto the "last" reading
    # while stranding the qualifier ("the second-to-last friday of each
    # month" used to resolve as -1FR with remainder "the second-to").  The
    # controls above ("last friday"/"first monday") prove the un-qualified
    # readings are unchanged.
    ("the second-to-last friday of every month", "FREQ=MONTHLY;BYDAY=-2FR", ""),
    ("the penultimate friday of every month", "FREQ=MONTHLY;BYDAY=-2FR", ""),
    ("the next-to-last friday of every month", "FREQ=MONTHLY;BYDAY=-2FR", ""),
    # "third-to-last" generalises the same idiom to -3.
    ("the third-to-last friday of every month", "FREQ=MONTHLY;BYDAY=-3FR", ""),
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
    # "every year on <holiday>": the year-anchored skeleton must resolve a
    # holiday word the same way the bare "every <holiday>" form does -- not
    # strand it as remainder behind a bare YEARLY rule that would silently
    # fire on the anchor date instead of the holiday (see R100).
    ("every year on christmas", "FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25", ""),
    ("every year on new year's day", "FREQ=YEARLY;BYMONTH=1;BYMONTHDAY=1", ""),
    # "every N years on <holiday/date>": an interval count before the year
    # unit ("every 2 YEARS on christmas") used to break the same filler-skip
    # that "every year on christmas" above relies on -- the literal "years"
    # check required the unit token to sit RIGHT after "every", so a NUMBER in
    # between fell through to the bare INTERVAL=N catch-all and stranded "on
    # christmas", firing on the anchor date instead of 25 December (R103).
    ("every 2 years on christmas", "FREQ=YEARLY;INTERVAL=2;BYMONTH=12;BYMONTHDAY=25", ""),
    # the date-anchored reading ("every N years on <month> <day>") has the
    # identical gap -- same fix, same finder family (_recur_date_anchored).
    ("every 3 years on may 10", "FREQ=YEARLY;INTERVAL=3;BYMONTH=5;BYMONTHDAY=10", ""),
    # bare interval count, no holiday/date tail: unchanged control.
    ("every 2 years", "FREQ=YEARLY;INTERVAL=2", ""),
    # R106: "every other year on <holiday/date>" -- "other" is a word-form
    # interval count (INTERVAL=2), same family as "every 2 years"/"every 2nd
    # year"/"every second year" above.  Before the fix the interval scan only
    # recognised NUMBER tokens before the year unit, so "other" (which the
    # bare "every other year" control already reads via ctx.other, the same
    # ``marker_recur_other.voc`` vocabulary "every other week" uses) fell
    # through and stranded "on christmas"/"on may 10" as remainder behind a
    # bare FREQ=YEARLY;INTERVAL=2 rule that silently fired on the anchor date
    # instead of the named holiday/date.
    ("every other year on christmas", "FREQ=YEARLY;INTERVAL=2;BYMONTH=12;BYMONTHDAY=25", ""),
    ("every second year on christmas", "FREQ=YEARLY;INTERVAL=2;BYMONTH=12;BYMONTHDAY=25", ""),
    ("every 2nd year on christmas", "FREQ=YEARLY;INTERVAL=2;BYMONTH=12;BYMONTHDAY=25", ""),
    ("every other year on may 10", "FREQ=YEARLY;INTERVAL=2;BYMONTH=5;BYMONTHDAY=10", ""),
    # bare "every other year": unchanged control.
    ("every other year", "FREQ=YEARLY;INTERVAL=2", ""),
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
    # a movable feast has no RFC 5545 rule under the year-anchored skeleton
    # either -- "every year on easter" reads the same HolidayRecurrence as
    # the bare "every easter", it does not degrade to a fabricated RRULE.
    ("every year on easter", "easter"),
])
def test_movable_holiday_recurrence(text, key):
    got = extract_recurrence(text, LANG)
    assert got is not None
    assert got[0] == HolidayRecurrence(key)
    assert got[1] == ""
    with pytest.raises(ValueError):
        got[0].to_string()


def test_movable_holiday_with_interval_declines():
    """"every 2 years on easter": :class:`HolidayRecurrence` (a movable feast)
    has no ``interval`` field, so this frame cannot be built AT ALL -- it must
    decline outright (``None``), never fall through to the greedy bare
    ``FREQ=YEARLY;INTERVAL=2`` catch-all that would silently fire on the
    anchor date instead of Easter (R103).
    """
    assert extract_recurrence("every 2 years on easter", LANG) is None


def test_movable_holiday_with_word_interval_declines():
    """R106: "every other year on easter" carries the same word-form
    INTERVAL=2 as "every 2 years on easter" above, and must decline the same
    way -- not fall through to the greedy bare INTERVAL=2 catch-all.
    """
    assert extract_recurrence("every other year on easter", LANG) is None


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


# R78: a stranded "from A to B" range on a recurrence composes onto the rule
# instead of being silently dropped (extract_timespan on the SAME text
# already resolves the span -- the range detector exists, it just was not
# reused here).  Two readings:
#
# * both endpoints bare weekdays -> BYDAY, inclusive and wrap-around
#   ("friday to monday" -> FR,SA,SU,MO): the idiomatic reading of a
#   weekday-bounded recurrence.
# * anything else -> a date-range bound: the right endpoint sets UNTIL,
#   grounded exactly the way "until <date>" grounds it above (so "to august"
#   and "until august" land on the identical UNTIL=20170801T000000) -- the
#   left/"from" endpoint names no field Recurrence has (no DTSTART), same as
#   the still-unimplemented "starting <date>" today.
_RANGE_BOUND_CASES = [
    ("every day from monday to friday",
     "FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR", ""),
    # wrap-around: friday..monday inclusive is FR,SA,SU,MO, not the empty set.
    ("every day from friday to monday",
     "FREQ=DAILY;BYDAY=FR,SA,SU,MO", ""),
    ("weekly from june to august", "FREQ=WEEKLY;UNTIL=20170801T000000", ""),
    # COUNT/UNTIL mutual exclusivity (RFC 5545): the trailing "5 times" would
    # add COUNT, but it sits BEFORE the still-unconsumed range clause, so the
    # existing "N times" guard (nothing unread may follow) correctly declines
    # to set COUNT here -- the range then grounds UNTIL and "5 times" is left
    # in the remainder, exactly as "every day 5 times until march" above.
    ("every day 5 times from june to august",
     "FREQ=DAILY;UNTIL=20170801T000000", "5 times"),
    # R91: a range clause that grounds UNTIL must clear a pre-existing COUNT
    # ATOMICALLY -- Recurrence.__post_init__ validates COUNT/UNTIL mutual
    # exclusivity at construction time, so setting until= first (with count=
    # still set from the earlier "3 times") raised ValueError before a
    # separate follow-up _replace could clear it.  Both fields must land in
    # the SAME _replace call.  UNTIL wins, COUNT is dropped.
    ("every monday from june to august, 3 times",
     "FREQ=WEEKLY;UNTIL=20170801T000000;BYDAY=MO", ""),
    ("every 2 weeks from june to august, 5 times",
     "FREQ=WEEKLY;INTERVAL=2;UNTIL=20170801T000000", ""),
    # controls: no range clause, COUNT must survive unchanged.
    ("every monday 3 times", "FREQ=WEEKLY;COUNT=3;BYDAY=MO", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _RANGE_BOUND_CASES)
def test_range_bound_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=_BOUND_ANCHOR)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


# R83a: a from/to weekday range layered on TOP of an existing weekday-SET base
# ("every weekday" = MO,TU,WE,TH,FR) must INTERSECT with that base, not union
# onto it -- a weekday rule can never include a weekend day, so "every weekday
# from friday to monday" (wrap: FR,SA,SU,MO) must land on {FR,MO}, the days
# both the base and the wrap range agree on, not all 7 days.
_WEEKDAY_INTERSECT_CASES = [
    ("every weekday from friday to monday", "FREQ=WEEKLY;BYDAY=FR,MO", ""),
    # non-wrap control: monday..friday is already a subset of the MO-FR base,
    # so intersection and the old union happen to agree here -- this must not
    # regress.
    ("every weekday from monday to friday",
     "FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _WEEKDAY_INTERSECT_CASES)
def test_weekday_range_intersects_existing_byday(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=_BOUND_ANCHOR)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


# R83a: when the intersection is EMPTY ("every weekday" can never land on a
# weekend day, "every weekend day" can never land on a weekday), the range
# names a rule that can never fire -- decline outright (None) rather than
# fabricate a rule that matches nothing or, via the old union bug, everything.
@pytest.mark.parametrize("text", [
    "every weekday from saturday to sunday",
    "every weekend day from monday to friday",
])
def test_weekday_range_empty_intersection_declines(text):
    assert extract_recurrence(text, LANG, anchor=_BOUND_ANCHOR) is None


# R83b/R89: UNTIL must ground from the date-range "from A to B" clause, not
# from a preceding time-of-day "from A to B" clause ("every monday from 9 to
# 5 from june to august").  Before the R83 fix, the range-bound finder paired
# the FIRST "from" (the clock range) with whatever unconsumed text followed --
# swallowing "june" out of the second clause's payload and grounding UNTIL on
# June (the date range's own LEFT/"from" endpoint, which names no field) --
# instead of August, the date range's right/"to" endpoint.
#
# R89 fixes the clock clause's OWN reading: it used to fall through to
# _apply_clock's generic "N to H" minute-idiom match ("9 to 5" -> 4:51,
# nonsense) or, for an am/pm-qualified range, ground a same-day UNTIL off the
# clock clause's right endpoint (silently expiring the whole rule) while
# stranding the rest of the sentence unconsumed.  A dedicated clock-range
# reading (:func:`_apply_clock_range`) now folds the clause into a BYHOUR
# window-start pin instead, and it must still coexist correctly with the
# date range's UNTIL.
_UNTIL_FROM_RIGHT_CLAUSE_CASES = [
    # control: no time-of-day clause -- UNTIL already grounded correctly
    # before this fix, must not regress.
    ("every monday from june to august",
     "FREQ=WEEKLY;UNTIL=20170801T000000;BYDAY=MO", ""),
    ("every monday from 9 to 5 from june to august",
     "FREQ=WEEKLY;UNTIL=20170801T000000;BYDAY=MO;BYHOUR=9",
     ""),
    ("every monday from 9am to 5pm from june to august",
     "FREQ=WEEKLY;UNTIL=20170801T000000;BYDAY=MO;BYHOUR=9",
     ""),
    # interval variant: the "every other" INTERVAL=2 reading must survive the
    # same two-clause pairing.
    ("every other monday from 9 to 5 from june to august",
     "FREQ=WEEKLY;INTERVAL=2;UNTIL=20170801T000000;BYDAY=MO;"
     "BYHOUR=9", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _UNTIL_FROM_RIGHT_CLAUSE_CASES)
def test_until_grounds_from_rightmost_range_clause(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=_BOUND_ANCHOR)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


# R89: a within-day clock RANGE ("from 9 to 5", "from 9am to 5pm") folds onto
# the rule as a BYHOUR window-start pin -- the same discrete civil-clock PIN
# an "at 9" clause already grounds (RFC 5545's BYHOUR has no window-end
# part).  Two defects fixed here:
#
# * a bare-number range ("from 9 to 5") used to fall through to the clock
#   engine's own "N to H" MINUTE idiom ("quarter to five") and misread
#   "9 to 5" as "9 minutes to 5" -> BYHOUR=4;BYMINUTE=51, plus a stranded
#   "from" in the remainder;
# * an am/pm-qualified range ("from 9am to 5pm") used to ground the right
#   endpoint as a same-day UNTIL, silently expiring the rule the day it was
#   authored.
#
# Bare numbers are read literally -- the same "at 9"/"at 5" convention
# :func:`_apply_clock` already uses -- no am/pm disambiguation is invented.
@pytest.mark.parametrize("text,rrule,remainder", [
    ("every monday from 9 to 5",
     "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9", ""),
    ("every monday from 9am to 5pm",
     "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9", ""),
    ("every day from 8 to 10pm",
     "FREQ=DAILY;BYHOUR=8", ""),
    ("every weekday from 9am to 5pm",
     "FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=9", ""),
    # "between A and B" is the same range grammar as "from A to B".
    ("every monday between 9am and 5pm",
     "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9", ""),
])
def test_clock_range_becomes_byhour_window_start(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=_BOUND_ANCHOR)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder
    # no bogus BYMINUTE, and the rule must never expire the same day it was
    # authored via a stray UNTIL.
    assert got[0].byminute == ()
    assert got[0].until is None


# control: extract_timespan on the identical text is untouched by this fix --
# it already resolved the span correctly before R78 and must keep doing so.
@pytest.mark.parametrize("text,start,end,remainder", [
    ("every day from monday to friday",
     "2017-07-03", "2017-07-08", "every day"),
    ("weekly from june to august", "2017-06-01", "2017-09-01", "weekly"),
])
def test_timespan_on_recurrence_range_text_unchanged(text, start, end, remainder):
    from chronologia.extract import extract_timespan
    got = extract_timespan(text, LANG, anchor=_BOUND_ANCHOR)
    assert got is not None
    assert str(got[0].start.date()) == start
    assert str(got[0].end.date()) == end
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
    "the second-to-last friday of every month",
    "the penultimate friday of every month",
    "the next-to-last friday of every month",
])
def test_second_to_last_friday_occurrences_are_not_the_last_friday(text):
    # R114: the parsed BYDAY=-2FR rule must actually expand to the
    # second-to-last Friday of each month (independently computed: August
    # 2026's Fridays are the 7th/14th/21st/28th, so -2 is the 21st, NOT the
    # 28th the silent-wrong reading used to return).
    from chronologia.recurrence import occurrences, parse_rrule
    got = extract_recurrence(text, LANG,
                             anchor=_dt.datetime(2026, 8, 10, 12, 0))
    assert got is not None
    assert got[0].to_string() == "FREQ=MONTHLY;BYDAY=-2FR"
    rule = parse_rrule(got[0].to_string())
    occs = [str(d) for d in
            occurrences(rule, _dt.datetime(2026, 8, 1), count=3)]
    assert occs == ["2026-08-21", "2026-09-18", "2026-10-23"]


def test_fifth_to_last_friday_of_month_is_no_recurrence():
    # R114 follow-up: "fifth-to-last" is out of the supported -2..-4 range,
    # and out-of-range must decline the WHOLE extraction, not just the
    # nth-weekday reading -- the earlier fix left a residue where the
    # rejected idiom fell through to the generic every-month finder, which
    # still consumed "each month" and returned a bare FREQ=MONTHLY with the
    # entire meaning-bearing phrase ("the fifth-to-last friday of") stranded
    # in the remainder.  That is the same stranded-temporal-words defect
    # signature as an impossible ordinal ("every 31st of april" below): the
    # whole extraction must refuse (None), never a partial rule with the
    # qualifier silently dropped.
    assert extract_recurrence(
        "the fifth-to-last friday of each month", LANG,
        anchor=_dt.datetime(2026, 8, 10, 12, 0)) is None


@pytest.mark.parametrize("text", [
    # controls: bare "each month"/"every month" (no rejected n-to-last shape
    # ahead of it) must still ground as the ordinary MONTHLY rule -- the
    # fifth-to-last refusal above must not make the generic every-month
    # finder itself decline.
    "each month",
    "every month",
])
def test_bare_every_month_control_unchanged(text):
    got = extract_recurrence(text, LANG,
                             anchor=_dt.datetime(2026, 8, 10, 12, 0))
    assert got is not None
    assert got[0].to_string() == "FREQ=MONTHLY"
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


# R94: THREE from/to clauses in one sentence -- a clock range, a weekday
# range, and a date range -- must ALL be claimed.  Before this fix,
# ``_apply_clock_range`` and ``_apply_range_bound`` each ran ONCE and stopped
# at their first match, so a sentence carrying more than two "from X to Y"
# clauses silently dropped or garbled the extras:
#
# * "every weekday from friday to monday from 9 to 5 from june to august" --
#   the weekday-range clause (friday..monday) was never intersected onto the
#   MO-FR base and was left stranded in the remainder, even though the clock
#   clause (9 to 5) and the date clause (june to august) both grounded fine.
# * "every monday from 9am to 5pm from june to august from 1 to 2" -- the
#   bogus trailing "from 1 to 2" was read (rightmost-first) as THE date
#   range, grounding UNTIL to the anchor day at 01:00 (expiring the rule
#   immediately) while the real "from june to august" clause vanished with
#   an empty remainder.
#
# Fix: both apply-passes now iterate, claiming every from-to clause they can
# (rightmost date-range candidates first, per #642), rather than stopping
# after the first hit.  A clause no pass can claim (a bare-number range with
# no clock reading left to claim it) stays stranded in the remainder --
# never silently dropped, never misread as a bogus UNTIL.
_MULTI_CLAUSE_CASES = [
    ("every weekday from friday to monday from 9 to 5 from june to august",
     "FREQ=WEEKLY;UNTIL=20170801T000000;BYDAY=FR,MO;BYHOUR=9", ""),
    # date + weekday + clock in a different textual order: date clause is
    # still rightmost, weekday and clock clauses precede it.
    ("every weekday from 9 to 5 from friday to monday from june to august",
     "FREQ=WEEKLY;UNTIL=20170801T000000;BYDAY=FR,MO;BYHOUR=9", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _MULTI_CLAUSE_CASES)
def test_three_clause_recurrence_claims_every_clause(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=_BOUND_ANCHOR)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


def test_bogus_trailing_range_never_produces_garbage_until():
    # the real date clause ("from june to august") must ground UNTIL, and the
    # bogus trailing "from 1 to 2" must never be misread as a date -- it is
    # either claimed as a second clock reading or left stranded in the
    # remainder, but the rule must NOT silently expire at the anchor day.
    text = "every monday from 9am to 5pm from june to august from 1 to 2"
    got = extract_recurrence(text, LANG, anchor=_BOUND_ANCHOR)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    rec, remainder = got
    assert rec.until is not None
    assert rec.until.month == 8 and rec.until.day == 1, (
        f"UNTIL grounded off the wrong clause: {rec.until!r}")
    assert rec.byday == ((None, 0),), f"unexpected BYDAY: {rec.byday!r}"
    assert rec.byhour == (9,), f"unexpected BYHOUR: {rec.byhour!r}"
    # the bogus clause is never silently dropped: either it stays visible in
    # the remainder, or nothing named "1" / "2" survives unaccounted for --
    # in either case the rule must not have swallowed it into a fake bound.
    assert "1" not in remainder or "from 1 to 2" in remainder


# control: a single bare-number range with no other clause competing for it
# is claimed as a clock reading (existing, pinned behaviour) -- must not
# regress into the multi-clause loop misreading it as a date.
def test_single_bare_number_range_still_reads_as_clock():
    text = "every monday from 1 to 2"
    got = extract_recurrence(text, LANG, anchor=_BOUND_ANCHOR)
    assert got is not None
    rec, remainder = got
    assert rec.until is None
    assert rec.byhour == (1,)
    assert remainder == ""


# R98: a sentence with TWO genuine date-range clauses ("every day from june
# to august from september to october") is ambiguous -- the rightmost-first
# scan in ``_apply_range_bound`` used to ground UNTIL off the rightmost
# clause and strand the other, equally genuine, date-range clause in the
# remainder, next to a rule that looked confidently correct.  There is no
# principled way to prefer one calendar bound over the other, so the whole
# extraction must decline (return None) rather than pick one arbitrarily.
_DOUBLE_DATE_RANGE_CASES = [
    "every day from june to august from september to october",
    "every week from march to may from july to september",
    # a trailing COUNT clause does not rescue the ambiguity -- the two date
    # ranges are still both stranded/grounded arbitrarily underneath it.
    "every week from march to may from july to september, 5 times",
]


@pytest.mark.parametrize("text", _DOUBLE_DATE_RANGE_CASES)
def test_double_date_range_declines_as_ambiguous(text):
    got = extract_recurrence(text, LANG, anchor=_BOUND_ANCHOR)
    assert got is None, f"{text!r} should decline (ambiguous), got {got!r}"


# control: a single date-range clause is unaffected by the ambiguity check --
# pinned pre-R98 behaviour must be unchanged.
def test_single_date_range_still_grounds_until():
    text = "every day from june to august"
    got = extract_recurrence(text, LANG, anchor=_BOUND_ANCHOR)
    assert got is not None
    rec, remainder = got
    assert rec.until is not None
    assert rec.until.month == 8 and rec.until.day == 1
    assert remainder == ""


# --------------------------------------------------------------------------
# "every holiday in <jurisdiction>" -- a whole calendar's holiday set, R108.
# Like the movable-feast HolidayRecurrence above, this has no RFC 5545 rule
# either (it is a lookup across many, mostly-movable dates), so to_string()
# refuses the same way.
# --------------------------------------------------------------------------
from chronologia.recurrence import JurisdictionHolidays   # noqa: E402


@pytest.mark.parametrize("text,jurisdiction", [
    ("every holiday in Portugal", "PT"),
    ("every public holiday in Portugal", "PT"),
    ("all holidays in Portugal", "PT"),
    ("every holiday in Spain", "ES"),
    ("every holiday in France", "FR"),
    ("every holiday in Germany", "DE"),
    ("every holiday in Brazil", "BR"),
    ("every holiday in the United States", "US"),
    ("every holiday in the United Kingdom", "GB"),
])
def test_jurisdiction_holidays_recurrence(text, jurisdiction):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0] == JurisdictionHolidays(jurisdiction)
    assert got[1] == ""
    with pytest.raises(ValueError):
        got[0].to_string()


def test_jurisdiction_holidays_unknown_country_declines():
    """An unmapped country name is never guessed at -- the finder simply
    does not match, leaving the phrase to whatever the rest of the pipeline
    makes of it (nothing, here)."""
    assert extract_recurrence("every holiday in Atlantis", LANG) is None


def test_bare_every_holiday_is_unchanged():
    """R108 adds a NEW frame ("every holiday IN <jurisdiction>"); the bare
    "every holiday" (no jurisdiction) must keep its pre-R108 behaviour --
    pinned here as a control so a future change to this finder cannot
    silently start matching it."""
    assert extract_recurrence("every holiday", LANG) is None


# --------------------------------------------------------------------------
# R111a: "every holiday in Portugal AND Spain" -- a SECOND, recognised
# jurisdiction trailing a connector names more than one jurisdiction, which
# JurisdictionHolidays cannot model (a single ``jurisdiction`` code, not a
# list).  Silently keeping only the first and stranding "and Spain" answered
# a narrower question than the one asked; refuse outright instead.
# --------------------------------------------------------------------------
@pytest.mark.parametrize("text", [
    "every holiday in Portugal and Spain",
    "every holiday in Spain and Portugal",
    "all holidays in France and Germany",
])
def test_jurisdiction_holidays_multi_country_declines(text):
    assert extract_recurrence(text, LANG) is None


def test_jurisdiction_holidays_unknown_trailing_word_unaffected():
    """An unknown word after the connector (not a second recognised
    jurisdiction) is NOT a multi-jurisdiction clause -- current stranding
    behaviour for a genuinely unrecognised tail is unchanged."""
    got = extract_recurrence("every holiday in Portugal please", LANG)
    assert got is not None
    assert got[0] == JurisdictionHolidays("PT")
    assert got[1] == "please"


# --------------------------------------------------------------------------
# R111b: a trailing whole-year scope ("next year", "this year", "in 2027")
# binds as UNTIL -- the end of the named year -- rather than stranding.
# Anchored at 2026-08-11 so "next year" is unambiguously 2027.
# --------------------------------------------------------------------------
from datetime import datetime as _datetime  # noqa: E402

from chronologia.astrodate import AstroDate  # noqa: E402
from chronologia.recurrence import Recurrence, occurrences  # noqa: E402

_ANCHOR = _datetime(2026, 8, 11, 12, 0)


def test_every_monday_next_year_binds_until():
    got = extract_recurrence("every monday next year", LANG, anchor=_ANCHOR)
    assert got is not None
    rec, remainder = got
    assert isinstance(rec, Recurrence)
    assert remainder == ""
    assert rec.until == AstroDate(2028, 1, 1)
    # occurrences, expanded from a dtstart the caller pins inside 2027 (the
    # scoped year -- Recurrence has no DTSTART field of its own, see
    # _apply_year_scope's docstring), all fall within 2027.
    spans = list(occurrences(rec, AstroDate(2027, 1, 1), count=52))
    assert spans
    assert all(s.start.year == 2027 for s in spans)


def test_every_monday_this_year_binds_until():
    got = extract_recurrence("every monday this year", LANG, anchor=_ANCHOR)
    assert got is not None
    rec, remainder = got
    assert remainder == ""
    assert rec.until == AstroDate(2027, 1, 1)


def test_every_monday_in_2027_binds_until():
    got = extract_recurrence("every monday in 2027", LANG, anchor=_ANCHOR)
    assert got is not None
    rec, remainder = got
    assert remainder == ""
    assert rec.until == AstroDate(2028, 1, 1)


def test_every_monday_until_2028_unchanged():
    """Control: the pre-existing "until <year>" bound is untouched by the new
    year-scope pass -- it grounds through _apply_bounds first and the tail is
    already fully consumed by the time _apply_year_scope runs."""
    got = extract_recurrence("every monday until 2028", LANG, anchor=_ANCHOR)
    assert got is not None
    rec, remainder = got
    assert remainder == ""
    assert rec.until == AstroDate(2028, 1, 1)


def test_every_holiday_in_portugal_next_year_declines():
    """JurisdictionHolidays carries no bound field at all -- occurrences()
    takes until/count only as call arguments -- so a trailing year scope on
    one cannot be attached without silently dropping it; refuse outright."""
    assert extract_recurrence(
        "every holiday in Portugal next year", LANG, anchor=_ANCHOR) is None
