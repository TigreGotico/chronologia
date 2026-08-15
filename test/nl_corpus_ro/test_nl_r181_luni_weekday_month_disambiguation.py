# -*- coding: utf-8 -*-
"""ro -- "luni" (Monday) is homographic with "luni", the plural of "lună"
(month): the weekday token and the month-unit token are the exact same
surface string. Two finders read the "fiecare <word>" frame and one of them
was reaching a plural-month verdict on a bare weekday.

* :func:`~chronologia.extract.nseries._recur_date_anchored`'s "day-of-month
  tied to every month" branch treated a BARE "fiecare luni" (no leading
  count) as "every month" and then swallowed a following clock phrase's
  hour as a POSTPOSED day-of-month qualifier: "în fiecare luni la ora 15"
  read as FREQ=MONTHLY;BYMONTHDAY=15, dropping the weekday, contradicting a
  clock hour of 15 being misread as a day number. Fixed by declining that
  branch whenever the bare month-unit token immediately after "fiecare" is
  ALSO a bare weekday word -- "fiecare luni" is only ever grammatical as
  "every Monday" (the month-plural reading needs a leading count or the
  singular "lună"), leaving the correct weekday reading to
  :func:`~chronologia.extract.nseries._recur_every`.
* That same :func:`_recur_every` had a second, independent instance of the
  collision: its direct weekday-dict check fired even with a leading
  interval count, so "la fiecare 2 luni" ("every 2 months") read as
  FREQ=WEEKLY;INTERVAL=2;BYDAY=MO ("every 2 Mondays") instead. Fixed by
  skipping that direct match whenever a count precedes a token that is ALSO
  a month-unit word, leaving the unit-interval branch to read it as months.

Romanian has no distinct weekday plural to collide the other way -- "2
luni" is unambiguously "2 months", never "2 Mondays".
"""
from datetime import datetime

import pytest

from chronologia.extract import extract_recurrence

LANG = "ro"
ANCHOR = datetime(2026, 8, 14, 10, 0)

_CASES = [
    # -- the defect: bare "luni" + a clock phrase must keep the WEEKDAY
    # reading, not silently re-read the hour as a day-of-month -------------
    ("în fiecare luni la ora 15", "FREQ=WEEKLY;BYDAY=MO;BYHOUR=15", ""),
    ("fiecare luni la ora 15", "FREQ=WEEKLY;BYDAY=MO;BYHOUR=15", ""),
    # -- controls: a non-homographic weekday, same clock-phrase shape ------
    ("în fiecare marți la ora 9", "FREQ=WEEKLY;BYDAY=TU;BYHOUR=9", ""),
    ("în fiecare miercuri", "FREQ=WEEKLY;BYDAY=WE", ""),
    # -- control: bare "luni" alone, no clock phrase to collide with -------
    ("în fiecare luni", "FREQ=WEEKLY;BYDAY=MO", ""),
    # -- the second collision: "NUM luni" must read as MONTHS, never as an
    # interval count of Mondays ---------------------------------------------
    ("la fiecare 2 luni", "FREQ=MONTHLY;INTERVAL=2", "la"),
    ("la fiecare 3 luni", "FREQ=MONTHLY;INTERVAL=3", "la"),
    # -- control: the genuine singular month reading, unaffected -----------
    ("în fiecare lună", "FREQ=MONTHLY", "în"),
    # -- composes: the interval-months reading with a trailing clock -------
    ("la fiecare 2 luni la ora 10", "FREQ=MONTHLY;INTERVAL=2;BYHOUR=10", "la"),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_luni_weekday_month_disambiguation(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder
