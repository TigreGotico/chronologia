"""A length before "before"/"after" is the date's offset, not the event's width.

"dentist three days before christmas" is one day, 22 December.  The event
reader must not take "three days" as the length and date the event from what
is left ("before christmas").  A length with "for" stays a length.  Anchor
30 January 2026, 10:00: the kalends (1st), nones (7th) and ides (15th) of the
months below are still ahead in 2026.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_event

ANCHOR = datetime(2026, 1, 30, 10, 0)


@pytest.mark.parametrize("lang, text, summary, day", [
    ("en", "dentist three days before christmas", "dentist", datetime(2026, 12, 22)),
    ("en", "party 2 days after christmas", "party", datetime(2026, 12, 27)),
    ("en", "team dinner a week before the ides of march", "team dinner",
     datetime(2026, 3, 8)),
    ("en", "pay the rent 3 days after the kalends of april", "pay the rent",
     datetime(2026, 4, 4)),
    ("en", "3 days before the kalends of april", "", datetime(2026, 3, 29)),
    ("en", "the day before the nones of july", "", datetime(2026, 7, 6)),
    ("fr", "dîner 2 jours après les calendes d'avril", "dîner", datetime(2026, 4, 3)),
])
def test_offset_dates_the_event(lang, text, summary, day):
    ev = extract_event(text, lang, anchor=ANCHOR)
    assert (ev.summary, ev.span.start, ev.duration) == (summary, day, None)


def test_offset_from_now_dates_the_event():
    ev = extract_event("dentist in 3 days", "en", anchor=ANCHOR)
    assert (ev.summary, ev.span.start, ev.duration) == (
        "dentist", ANCHOR + timedelta(days=3), None)


@pytest.mark.parametrize("text, summary, start, length", [
    # controls: "for" makes the number a length
    ("holiday for 3 days from tomorrow", "holiday", datetime(2026, 1, 31),
     timedelta(days=3)),
    ("call mom at 5pm for 10 minutes", "call mom", datetime(2026, 1, 30, 17),
     timedelta(minutes=10)),
])
def test_length_with_for_stays_a_length(text, summary, start, length):
    ev = extract_event(text, "en", anchor=ANCHOR)
    assert (ev.summary, ev.span.start, ev.span.end, ev.duration) == (
        summary, start, start + length, length)
