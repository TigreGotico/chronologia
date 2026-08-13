"""R156: "kell <spelled hour>" immediately before a numeric calendar date
must compose onto that date, not corrupt its day.

The spelled clock-hour word ("üheksa" = nine) sat directly next to the
literal digit day ("25.") with no connector between them.  The shared
number-word fold treated the two as one run and read only the leading
spelled word, discarding the digit day outright -- "kell üheksa 25.
detsembri 2021" resolved to 2021-12-**09** with "kell" stranded, silently
dropping both the clock and the real day.  Gold below is independently
computed: the clock composes onto the date exactly as the equivalent
"date, then kell N" phrasing already does.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start_end, start, nomatch


@pytest.mark.parametrize("text,y,mo,d,h", [
    ("kell üheksa 25. detsembri 2021", 2021, 12, 25, 9),
    ("kell kaheksa 5. juuni 2020", 2020, 6, 5, 8),
])
def test_kell_spelled_hour_before_numeric_date_composes(text, y, mo, d, h):
    s, e = start_end(text)
    assert s == ad(__import__("datetime").datetime(y, mo, d, h, 0))
    assert e == s + timedelta(minutes=1)


# -- controls: must not regress -----------------------------------------

def test_control_bare_numeric_date_unchanged():
    s, e = start_end("25. detsembri 2021")
    assert s == ad(__import__("datetime").datetime(2021, 12, 25))
    assert e == s + timedelta(days=1)


def test_control_kell_alone_unchanged():
    cand = ANCHOR.replace(hour=9, minute=0, second=0, microsecond=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    assert start("kell üheksa") == ad(cand)


def test_control_kell_with_weekday_unchanged():
    # "kell üheksa esmaspäeval" -- the whole-hour clock composes onto the
    # coming Monday exactly as it did before this fix (no numeric date in
    # the phrase for the fold to collide with).
    r = start_end("kell üheksa esmaspäeval")
    s, e = r
    assert s.hour == 9 and s.minute == 0
    assert e - s == timedelta(minutes=1)
    # the mission anchor (2017-06-27) is a Tuesday; the coming Monday is
    # 2017-07-03.
    assert (s.year, s.month, s.day) == (2017, 7, 3)


@pytest.mark.parametrize("text,h,mi", [
    ("veerand seitse", 6, 15),
    ("pool viis", 4, 30),
    ("kolmveerand üheksa", 8, 45),
])
def test_control_counting_clock_forms_unchanged(text, h, mi):
    cand = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    assert start(text) == ad(cand)


# -- recombined variants (attested surfaces only) ------------------------

def test_kell_spelled_hour_before_date_no_year():
    # the year-less form of the same composition -- mined from
    # test_et_calendar_dates.py's "5. juuni" (year-less) control.
    s, e = start_end("kell kaheksa 5. juuni")
    assert s.month == 6 and s.day == 5 and s.hour == 8 and s.minute == 0
    assert e - s == timedelta(minutes=1)


def test_kell_other_spelled_hour_before_date():
    s, e = start_end("kell viis 25. detsembri 2021")
    assert s == ad(__import__("datetime").datetime(2021, 12, 25, 5, 0))
    assert e - s == timedelta(minutes=1)
