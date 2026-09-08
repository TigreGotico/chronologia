"""The singular second is a unit, not the ordinal "2nd", when a count precedes it.

In English and the Romance languages the word for the unit of time and the
ordinal "second" are the same word ("second", "segundo", "seconde",
"secondo", "segon", "segonda").  After a count the only reading is the unit:
"one second" is a length, never "1 2nd".  The ordinal reading survives
everywhere else ("the second of May", "twenty second of May").

Gold is arithmetic on the anchor, never the parser's own output.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_duration, extract_timespan
from chronologia.astrodate import AstroDate

ANCHOR = datetime(2017, 6, 27, 13, 4)
ONE_SECOND = timedelta(seconds=1)


def _ad(dt):
    return AstroDate(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)


@pytest.mark.parametrize("lang,text", [
    ("en", "1 second"), ("en", "one second"), ("en", "a second"),
    ("es", "1 segundo"), ("es", "un segundo"),
    ("pt", "1 segundo"), ("pt", "um segundo"),
    ("fr", "1 seconde"), ("fr", "une seconde"),
    ("it", "1 secondo"), ("it", "un secondo"),
    ("ca", "1 segon"), ("ca", "un segon"),
    ("gl", "1 segundo"), ("gl", "un segundo"),
    ("ast", "1 segundu"), ("ast", "un segundu"),
    ("oc", "1 segonda"), ("oc", "una segonda"),
])
def test_one_second_is_a_length(lang, text):
    got = extract_duration(text, lang)
    assert got is not None, f"{lang} {text!r} read no length"
    assert got.duration == ONE_SECOND
    assert got.remainder == ""


@pytest.mark.parametrize("lang,text", [
    ("en", "in 1 second"), ("en", "in one second"), ("en", "in a second"),
    ("es", "en 1 segundo"), ("pt", "em 1 segundo"), ("fr", "dans 1 seconde"),
    ("it", "tra 1 secondo"), ("ca", "dins 1 segon"), ("oc", "dins 1 segonda"),
])
def test_in_one_second_is_one_second_ahead(lang, text):
    r = extract_timespan(text, lang, ANCHOR)
    assert r is not None, f"{lang} {text!r} did not parse"
    assert r.span.start == _ad(ANCHOR + ONE_SECOND)
    assert r.span.end == _ad(ANCHOR + 2 * ONE_SECOND)
    assert r.remainder == ""


@pytest.mark.parametrize("text,day", [
    ("the second of may", 2),
    ("second of may", 2),
    ("twenty second of may", 22),
    ("the twenty-second of may", 22),
])
def test_the_ordinal_reading_survives(text, day):
    r = extract_timespan(text, "en", ANCHOR)
    assert r is not None
    # May 2017 is already past at the anchor, so the next May is 2018.
    assert r.span.start == AstroDate(2018, 5, day)
    assert r.span.end == AstroDate(2018, 5, day + 1)


def test_a_bare_second_is_no_length():
    assert extract_duration("second", "en") is None


def test_article_before_a_noun_keeps_the_ordinal():
    """"a second chance" is no length, and "a second week of march" is the
    second week of March (the 13th to the 20th in 2017), not one second."""
    assert extract_duration("a second chance", "en") is None
    assert extract_timespan("a second chance", "en", ANCHOR) is None
    r = extract_timespan("a second week of march", "en", ANCHOR)
    assert r is not None
    assert r.span.start == AstroDate(2017, 3, 13)
    assert r.span.end == AstroDate(2017, 3, 20)


def test_ordinal_list_before_a_weekday_keeps_its_recurrence():
    """The word in the unit table must not cut the ordinal list short."""
    from chronologia import extract_recurrence
    r = extract_recurrence("every second and fourth tuesday", "en")
    assert r is not None and r.remainder == ""
    assert r.recurrence.freq == "MONTHLY"
    assert r.recurrence.byday == ((2, 1), (4, 1))
