"""Regression locks for the linguist-audit fixes.

Gold is independent of the extraction parser: Islamic-month dates are computed
through the separately gold-tested ``islamic_civil`` calendar, and the
weekday/month facts are cited to canonical sources in the commit.
"""
from datetime import datetime

import pytest

from chronologia import CALENDARS, extract_timespan

_A = datetime(2026, 7, 31, 12, 0)


def test_aragonese_december_is_aviento():
    # an: December is "Aviento" (Latin adventum), not the Castilian "deciembre".
    # Biquipedia (an.wikipedia.org/wiki/Mes).
    r = extract_timespan("o mes de aviento", "an", _A)
    assert r is not None and r[0].start_datetime.month == 12


@pytest.mark.parametrize("month_name,month_no", [
    ("ربيع الأول", 3),
    ("ربيع الآخر", 4),
    ("جمادى الأولى", 5),
    ("جمادى الآخرة", 6),
    ("ذو القعدة", 11),
    ("ذو الحجة", 12),
])
def test_arabic_islamic_months_bind_to_the_right_month(month_name, month_no):
    # These six months previously carried only Latin transliterations, so an
    # Arabic-script date silently failed (or, for ربيع, misparsed as the season
    # "spring"). Gold: the date the (independently gold-tested) islamic_civil
    # calendar gives for day 15 of that month in 1446 AH.
    from chronologia.calendars import islamic_civil_to_jdn, jdn_to_gregorian
    ey, em, ed = jdn_to_gregorian(islamic_civil_to_jdn(1446, month_no, 15))
    r = extract_timespan(f"خمسة عشر {month_name} 1446", "ar", _A)
    assert r is not None, f"{month_name} did not bind"
    got = r[0].start
    assert (got.year, got.month, got.day) == (ey, em, ed)


def test_arabic_rabi_not_caught_as_spring():
    # bare "ربيع الأول" must resolve as an Islamic month reference, not the
    # season vocab "ربيع" (spring).
    r = extract_timespan("ربيع الأول 1446", "ar", _A)
    assert r is not None
    # a whole-month span (~29-30 days), not a season (~quarter year)
    assert 27 <= r[0].width.days <= 31


def test_czech_last_friday_of_month():
    # cs gained marker_ordlast ("poslední"). Last Friday of May 2026 = 2026-05-29
    # (independent: May 2026 Fridays are 1, 8, 15, 22, 29).
    r = extract_timespan("poslední pátek v květnu", "cs", _A)
    assert r is not None
    assert r[0].start_datetime.date().isoformat() == "2026-05-29"


# --- since <weekday> resolves to the most recent PAST occurrence (weekly cycle,
#     not a year-back), and Slavic genitive weekday forms enable until/since ---
_TUE = datetime(2017, 6, 27, 13, 4)   # Tuesday; last Mon=06-26, last Fri=06-23, next Fri=06-30


@pytest.mark.parametrize("text,lang,start,end", [
    ("since monday", "en", "2017-06-26", "2017-06-27"),
    ("since friday", "en", "2017-06-23", "2017-06-27"),
    ("с понедельника", "ru", "2017-06-26", "2017-06-27"),
    ("od piątku", "pl", "2017-06-23", "2017-06-27"),       # since Friday
    ("od pátku", "cs", "2017-06-23", "2017-06-27"),
])
def test_since_weekday_is_most_recent_past(text, lang, start, end):
    r = extract_timespan(text, lang, _TUE)
    assert r is not None
    assert r[0].start_datetime.date().isoformat() == start
    assert r[0].end_datetime.date().isoformat() == end


@pytest.mark.parametrize("text,lang", [
    ("do pátku", "cs"), ("do piątku", "pl"), ("do piatku", "sk"),
    ("do petka", "sl"), ("do petka", "hr"), ("до пятницы", "ru"),
])
def test_until_weekday_genitive_resolves(text, lang):
    # until next Friday: [now, 2017-07-01)
    r = extract_timespan(text, lang, _TUE)
    assert r is not None
    assert r[0].end_datetime.date().isoformat() == "2017-07-01"


def test_since_last_weekday_is_a_real_past_span():
    # "since last friday" at Tue 2017-06-27: [2017-06-23, 2017-06-27)
    r = extract_timespan("since last friday", "en", _TUE)
    assert r is not None
    assert r[0].start_datetime.date().isoformat() == "2017-06-23"
    assert r[0].end_datetime.date().isoformat() == "2017-06-27"


@pytest.mark.parametrize("text", [
    "since this friday", "since next monday",   # qualified weekday, future
    "since tomorrow",                           # now-relative day, always future
    "since 2019",                               # explicit future year
    "since next month", "since next week",      # direction-qualified period, future
    "since next year",
])
def test_since_future_definite_endpoint_never_fabricates_year_old_span(text):
    # A DEFINITE future endpoint (qualified weekday / now-relative day / explicit
    # year) is contradictory for a "since" range.  It must NOT be pulled back a
    # whole year (the old bug gave ~2016 / a 2017 pull-back); the "since" span is
    # refused, leaving at worst an honest partial parse whose own span is never
    # a fabricated year in the past.
    r = extract_timespan(text, "en", _TUE)
    assert r is None or r[0].start_datetime >= datetime(2017, 1, 1)


@pytest.mark.parametrize("text,start,end", [
    ("since yesterday", "2017-06-26", "2017-06-27"),   # past relative day
    ("since july 6", "2016-07-06", "2017-06-27"),       # underspecified anniversary
    ("since christmas", "2016-12-25", "2017-06-27"),    # holiday anniversary
])
def test_since_past_or_anniversary_endpoint_opens_a_real_span(text, start, end):
    # The mirror of the refusal: a genuinely-past relative day opens directly,
    # and an underspecified anniversary whose year prefer_future guessed forward
    # is pulled back to its most recent past occurrence -- these MUST keep working.
    r = extract_timespan(text, "en", _TUE)
    assert r is not None
    assert r[0].start_datetime.date().isoformat() == start
    assert r[0].end_datetime.date().isoformat() == end


# --- "since A until B": a DIRECTIONAL range -- "since" past-anchors the start,
#     "until" future-anchors the end (relative to that start), so the "since"
#     marker is consumed rather than stranded and the span is not both-forward.
@pytest.mark.parametrize("text,start,end,rem", [
    # anchor Tue 2017-06-27: last Monday 06-26 through the following Friday 06-30
    ("since monday until friday", "2017-06-26", "2017-07-01", ""),
    # yesterday (06-26) through the Friday after it
    ("since yesterday until friday", "2017-06-26", "2017-07-01", ""),
    # dated: the recent-past week, NOT a year-long span -- the end is the June 12
    # AFTER the past-anchored June 5 start, not next year's
    ("since june 5 until june 12", "2017-06-05", "2017-06-13", ""),
])
def test_since_until_directional_range(text, start, end, rem):
    r = extract_timespan(text, "en", _TUE)
    assert r is not None
    assert r[0].start_datetime.date().isoformat() == start
    assert r[0].end_datetime.date().isoformat() == end
    assert getattr(r, "remainder", "") == rem   # "since" consumed, not stranded


@pytest.mark.parametrize("hh,mm,text,start", [
    # a bare time-of-day recurs DAILY: "since noon" at 09:00 is YESTERDAY noon
    # (most recent past occurrence), never a year ago (the old year-pull bug).
    (9, 0, "since noon", "2017-06-26T12:00:00"),
    (9, 0, "since 3pm", "2017-06-26T15:00:00"),
    (15, 0, "since noon", "2017-06-27T12:00:00"),   # after noon -> today noon
    (9, 0, "since 8:30am", "2017-06-27T08:30:00"),  # earlier today -> today
])
def test_since_bare_clock_rolls_by_day_not_year(hh, mm, text, start):
    r = extract_timespan(text, "en", datetime(2017, 6, 27, hh, mm))
    assert r is not None
    assert r[0].start_datetime.isoformat() == start


def test_since_quarter_is_a_yearly_anniversary():
    # a quarter recurs YEARLY, like "since july 6": most recent past Q3 start.
    r = extract_timespan("since q3", "en", _TUE)
    assert r is not None
    assert r[0].start_datetime.date().isoformat() == "2016-07-01"


def test_since_dated_clock_stays_yearly_not_daily():
    # a clock time WITH a calendar date ("june 5 at noon") is a yearly
    # anniversary, not a daily recurrence -- rolled back by a year, not a day.
    r = extract_timespan("since june 5 at noon", "en", _TUE)
    assert r is not None
    assert r[0].start_datetime.isoformat() == "2017-06-05T12:00:00"


@pytest.mark.parametrize("text,lang", [
    ("Monday, March 2", "en"),
    ("Monday March 2", "en"),
    ("March 2 Monday", "en"),
    ("lunes 2 de marzo", "es"),
])
def test_weekday_label_on_explicit_date_yields_the_date(text, lang):
    # a weekday sitting next to an explicit calendar date is a confirming LABEL,
    # not a second date: the date is authoritative and the weekday is consumed
    # (was: the bare weekday won by text position and stranded the date).
    r = extract_timespan(text, lang, _TUE)
    assert r is not None
    assert r[0].start_datetime.date().isoformat() == "2018-03-02"
    assert getattr(r, "remainder", "") == ""   # weekday label not stranded


def test_weekday_plus_clock_still_composes_onto_the_weekday():
    # the label rule must NOT hijack "Monday at 3pm" -- with no explicit date,
    # the clock composes onto the weekday as before.
    r = extract_timespan("Monday at 3pm", "en", _TUE)
    assert r is not None
    assert r[0].start_datetime.isoformat() == "2017-07-03T15:00:00"


def test_plain_from_to_range_stays_forward():
    # the directional path must NOT touch a plain "from A to B": both endpoints
    # still roll forward (next Monday .. next Friday), no past-anchoring.
    r = extract_timespan("from monday to friday", "en", _TUE)
    assert r is not None
    assert r[0].start_datetime.date().isoformat() == "2017-07-03"
    assert r[0].end_datetime.date().isoformat() == "2017-07-08"
