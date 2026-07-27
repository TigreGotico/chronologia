"""Multi-weekday recurrence enumerations -> a full ``BYDAY`` rule.

A recurrence that names several weekdays ("every monday, wednesday and
friday", "on mondays, wednesdays and fridays") is one WEEKLY rule listing
every named day on ``BYDAY`` -- RFC 5545 models this placement exactly.  The
older grammar bound only the first weekday and stranded the rest in the
remainder; these cases pin every day.

A **placement-free rate** ("twice a week", "three times a week", "twice
daily") has no single-RRULE reading -- RFC 5545 ``COUNT`` is a total, not a
per-period rate, and there is no "N per period" part -- so it is refused
(``None``) rather than fabricating weekdays the speaker never named.  A rate
that *does* name its days ("3 times a week on monday, wednesday and friday")
is the placed reading: the days win, the redundant rate is consumed.
"""
import pytest

from chronologia import extract_recurrence

LANG = "en-us"

# (text, rrule, byday tuple, remainder)
_MULTI = [
    ("every monday, wednesday and friday",
     "FREQ=WEEKLY;BYDAY=MO,WE,FR", ((None, 0), (None, 2), (None, 4)), ""),
    ("on mondays, wednesdays and fridays",
     "FREQ=WEEKLY;BYDAY=MO,WE,FR", ((None, 0), (None, 2), (None, 4)), ""),
    ("every monday wednesday and friday",
     "FREQ=WEEKLY;BYDAY=MO,WE,FR", ((None, 0), (None, 2), (None, 4)), ""),
    ("every tuesday and thursday",
     "FREQ=WEEKLY;BYDAY=TU,TH", ((None, 1), (None, 3)), ""),
    ("every monday and wednesday",
     "FREQ=WEEKLY;BYDAY=MO,WE", ((None, 0), (None, 2)), ""),
    ("on tuesdays and thursdays",
     "FREQ=WEEKLY;BYDAY=TU,TH", ((None, 1), (None, 3)), ""),
    # placed rate: the named days win, the redundant "3 times a week" is
    # consumed rather than blocking the parse.
    ("3 times a week on monday, wednesday and friday",
     "FREQ=WEEKLY;BYDAY=MO,WE,FR", ((None, 0), (None, 2), (None, 4)), ""),
]


@pytest.mark.parametrize("text,rrule,byday,remainder", _MULTI)
def test_multi_weekday_enumeration_collects_all_days(text, rrule, byday,
                                                     remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got.recurrence.to_string() == rrule
    assert got.recurrence.byday == byday
    assert got.remainder == remainder


# a placement-free rate cannot be an RRULE (no per-period count in RFC 5545)
# and must never fabricate weekdays: refuse cleanly, do not strand a partial.
@pytest.mark.parametrize("text", [
    "twice a week",
    "three times a week",
    "3 times a week",
    "twice daily",
    "twice a day",
    "twice daily at 8am and 8pm",
])
def test_placement_free_rate_is_refused(text):
    assert extract_recurrence(text, LANG) is None
