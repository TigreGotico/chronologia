"""Dutch "om de <unit>" interval idiom and werkdag(en) weekday-set recurrence.

"om de" ("around the"/"by the") is the everyday Dutch way to say "every"
for a repeating interval, standing alongside -- not replacing -- "elke"/
"iedere": "om de twee weken" and "elke twee weken" both mean every two
weeks. With an explicit numeral the interval is that number
(FREQ=<unit>;INTERVAL=N).

With NO numeral the bare form ("om de dag", "om de week") is the everyday
Dutch way to say "every OTHER" unit, not "every" plain -- a native speaker
reads "om de dag" as a day skipped every other day, the same reading en
"every other day" gets (FREQ=DAILY;INTERVAL=2), never "elke dag"'s
INTERVAL=1. "om de" is otherwise the ordinary "at" marker ("om 3 uur", at
3 o'clock) and must not be read as this idiom outside "om de <unit>".

"werkdag"/"werkdagen" (weekday/business day, singular/plural) name the
Monday-Friday set under the same two frames English "weekday(s)" gets:
"elke werkdag" (every weekday) and the bare plural "op werkdagen" (on
weekdays), both FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR.
"""
from datetime import datetime

import pytest

from chronologia.extract import extract_recurrence

ANCHOR = datetime(2026, 8, 14, 10, 0)

_CASES = [
    # explicit-numeral "om de N <unit>" interval idiom
    ('om de twee weken', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('om de drie dagen', 'FREQ=DAILY;INTERVAL=3', ''),
    ('om de 2 weken', 'FREQ=WEEKLY;INTERVAL=2', ''),
    # bare "om de <unit>" -- every OTHER unit, not every unit
    ('om de dag', 'FREQ=DAILY;INTERVAL=2', ''),
    ('om de week', 'FREQ=WEEKLY;INTERVAL=2', ''),
    # werkdag(en) weekday-set recurrence
    ('elke werkdag', 'FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR', ''),
    ('op werkdagen', 'FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR', ''),
    # controls that must keep reading exactly as before
    ('elke twee weken', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('elke drie dagen', 'FREQ=DAILY;INTERVAL=3', ''),
    ('elke maandag', 'FREQ=WEEKLY;BYDAY=MO', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_om_de_and_workdays(text, rrule, remainder):
    got = extract_recurrence(text, "nl", anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", [
    'om de hoek',       # "around the corner" -- non-temporal, must stay None
    'om 3 uur',         # "om" the "at" clock marker, no <unit> after "de"
])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, "nl", anchor=ANCHOR) is None
