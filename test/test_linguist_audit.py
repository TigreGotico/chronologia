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
