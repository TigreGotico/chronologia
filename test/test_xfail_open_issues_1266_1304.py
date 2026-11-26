"""Strict xfails for open issues 1276 to 1304.

Each row asserts the value the issue expects. Strict mode turns the run red
when a fix lands, so the fix removes the mark from its rows.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import (
    ImpossibleDateError,
    extract_candidates,
    extract_event,
    extract_recurrence,
    extract_timespan,
)

ANCHOR = datetime(2026, 11, 22, 9, 0)
URL = "https://github.com/TigreGotico/chronologia/issues/"


def xfail(issue):
    return pytest.mark.xfail(strict=True, reason=URL + str(issue))


def rows(issue, entries):
    return [pytest.param(*entry, marks=xfail(issue)) for entry in entries]


@pytest.mark.parametrize("text,reason", [
    ("the 25th weekday of the month", "no 25th"),
    ("the sixth monday of may", "no 6th Monday"),
])
def test_candidates_raise_mode(text, reason):
    with pytest.raises(ImpossibleDateError, match=reason):
        extract_candidates(text, "en", ANCHOR, impossible="raise")


@pytest.mark.parametrize("lang,text,first,kind", [
    ("en", "tomorrow or every month on the sixth monday", datetime(2026, 11, 23), "named_day"),
    ("pt", "amanhã ou todos os meses no sexto domingo", datetime(2026, 11, 23), "named_day"),
    ("de", "am 3. Juni oder der sechste Montag jedes Monats", datetime(2027, 6, 3), "calendar_date"),
    ("en", "the sixth monday of may, or else on 3 june", datetime(2027, 6, 3), "calendar_date"),
])
def test_candidates_keep_the_valid_date_and_drop_the_refused_weekday(lang, text, first, kind):
    # A sixth Monday (or Sunday) never occurs, so no candidate may read those
    # words as a plain weekday; the valid date beside them stays first.
    found = extract_candidates(text, lang, ANCHOR)
    assert (found[0].span.start.datetime(), found[0].construction) == (first, kind)
    assert "weekday_ref" not in [c.construction for c in found]


@pytest.mark.parametrize("text", [
    "annually on the 30th of february",
    "the sixth monday of may 2027",
    "the sixth monday of may next year",
    # extract_timespan reads the clock "at 7"
    pytest.param("the sixth monday of may at 7", marks=xfail(1276)),
])
def test_candidates_read_nothing_from_a_refused_date(text):
    # extract_timespan gives None for each; no candidate may read a year, a
    # clock or a day of this month out of the refused words.
    assert extract_timespan(text, "en", ANCHOR) is None
    assert extract_candidates(text, "en", ANCHOR) == []


def test_candidates_refused_business_day_has_no_month_fallback():
    assert extract_candidates("the 23rd business day of this month", "en", ANCHOR) == []


def test_sixth_monday_of_every_month_declines():
    text = "the sixth monday of every month"
    assert extract_timespan(text, "en", ANCHOR) is None
    assert extract_candidates(text, "en", ANCHOR) == []


def test_sixth_monday_of_every_month_raises():
    with pytest.raises(ImpossibleDateError, match="no 6th Monday"):
        extract_timespan("the sixth monday of every month", "en", ANCHOR, impossible="raise")


@pytest.mark.parametrize("text,rule", [
    ("the last business day of every month",
     "FREQ=MONTHLY;BYDAY=MO,TU,WE,TH,FR;BYSETPOS=-1"),
    ("the third business day of every month",
     "FREQ=MONTHLY;BYDAY=MO,TU,WE,TH,FR;BYSETPOS=3"),
])
def test_business_day_of_every_month(text, rule):
    result = extract_recurrence(text, "en", ANCHOR)
    assert result is not None
    assert result.recurrence.to_string() == rule
    assert result.remainder == ""


def test_third_weekday_of_march():
    result = extract_timespan("the 3rd weekday of march", "en", ANCHOR)
    assert result is not None
    assert result.span.start.datetime() == datetime(2027, 3, 3)
    assert result.span.end.datetime() == datetime(2027, 3, 4)


def test_twenty_fourth_weekday_of_march_declines():
    assert extract_timespan("the 24th weekday of march", "en", ANCHOR) is None


@pytest.mark.parametrize("lang, text, first, last_monday", [
    ("de", "jeden Montag von Juni bis August", datetime(2027, 6, 7), datetime(2027, 8, 30)),
    ("en", "every monday from june to august", datetime(2027, 6, 7), datetime(2027, 8, 30)),
])
def test_a_weekday_rule_between_two_bounds_starts_at_the_first(lang, text, first, last_monday):
    # 1 June 2027 is a Tuesday, so the first Monday is 7 June.
    # Any UNTIL from the last Monday up to the day before the next one gives the same dates.
    event = extract_event(text, lang, ANCHOR)
    assert event.summary == ""
    assert event.span.start.datetime() == first
    assert last_monday <= event.recurrence.until.datetime() < last_monday + timedelta(days=7)


# (lang, text, anchor, start, end or None, remainder or None)
SPANS = (
    rows(1296, [
        ("en", "alarm at 7, 8 and 9 tonight", datetime(2026, 11, 17, 8, 0), datetime(2026, 11, 17, 19, 0), None, None),
    ])
    + rows(1299, [
        ("es", "mañana tarde a las 5", ANCHOR, datetime(2026, 11, 23, 17, 0), None, ""),
    ])
    + rows(1300, [
        ("ca", "a les deu i quart del dia 14 de març", ANCHOR, datetime(2027, 3, 14, 10, 15), None, ""),
        ("ast", "a les diez y cuartu del día 14 de marzu", ANCHOR, datetime(2027, 3, 14, 10, 15), None, ""),
    ])
    + rows(1301, [
        ("en", "at a quarter past ten on the 14th of march", ANCHOR, datetime(2027, 3, 14, 10, 15), None, ""),
    ])
    + rows(1302, [
        ("es", "el día 14", ANCHOR, datetime(2026, 12, 14), None, None),
        ("gl", "no día 14", ANCHOR, datetime(2026, 12, 14), None, None),
        ("gl", "no día 14 de marzo", ANCHOR, datetime(2027, 3, 14), None, ""),
    ])
    + rows(1303, [
        ("en", "the first 5 business days of the month", ANCHOR, datetime(2026, 11, 2), datetime(2026, 11, 7), None),
        ("en", "the last 3 business days of the month", ANCHOR, datetime(2026, 11, 26), datetime(2026, 12, 1), None),
        ("pt", "os primeiros 5 dias úteis do mês", ANCHOR, datetime(2026, 11, 2), datetime(2026, 11, 7), None),
    ])
    + rows(1304, [
        ("en", "pay rent on the 3 business day of the month", ANCHOR, datetime(2026, 11, 4), None, None),
    ])
)


@pytest.mark.parametrize("lang,text,anchor,start,end,remainder", SPANS)
def test_timespan(lang, text, anchor, start, end, remainder):
    result = extract_timespan(text, lang, anchor)
    assert result is not None
    assert result.span.start.datetime() == start
    if end is not None:
        assert result.span.end.datetime() == end
    if remainder is not None:
        assert result.remainder == remainder


@pytest.mark.parametrize("lang,text,summary", [
    pytest.param("en", "a second meeting tomorrow", "a second meeting", marks=xfail(1297)),
    pytest.param("es", "una reunión mañana", "una reunión", marks=xfail(1297)),
    pytest.param("es", "un segundo café mañana", "un segundo café", marks=xfail(1297)),
])
def test_event_summary_keeps_the_words(lang, text, summary):
    event = extract_event(text, lang, datetime(2026, 11, 22, 9, 0))
    assert event is not None
    assert event.summary == summary


@pytest.mark.xfail(strict=True, reason=URL + "1298")
def test_fr_hours_of_meeting_le_matin_reads_the_morning_band():
    band = extract_timespan("demain matin", "fr", ANCHOR)
    result = extract_timespan("demain deux heures de réunion le matin", "fr", ANCHOR)
    assert result is not None
    assert result.span.start.datetime() == band.span.start.datetime()
    assert result.span.end.datetime() == band.span.end.datetime()


@pytest.mark.parametrize("lang,text", [
    pytest.param("es", "el último viernes del mes que viene", marks=xfail(1295)),
    pytest.param("fr", "le dernier vendredi du mois prochain", marks=xfail(1295)),
])
def test_event_last_friday_of_next_month(lang, text):
    event = extract_event(text, lang, datetime(2026, 10, 17, 9, 0))
    assert event is not None
    assert event.span.start.datetime() == datetime(2026, 11, 27)
    assert event.summary == ""
