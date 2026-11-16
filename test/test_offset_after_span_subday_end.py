"""A sub-day or business-day offset after a span counts from the span's end.

Meteorological summer is June, July and August (NOAA NCEI, "Meteorological
Versus Astronomical Seasons"), so next summer from 16 November 2026 ends
at 1 September 2027, 00:00.  30 June 2027 is a Wednesday and 31 August 2027
a Tuesday.  Weekends do not count as business days.  1992 has 366 days and
1991 has 365.  Anchor Monday 16 November 2026, 12:00.
"""
from datetime import date, datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2026, 11, 16, 12, 0)


def _day(text, lang="en"):
    span, rest = extract_timespan(text, lang, anchor=ANCHOR)
    assert rest == ""
    assert span.end - span.start == (datetime(2000, 1, 2) - datetime(2000, 1, 1))
    return date(span.start.year, span.start.month, span.start.day)


@pytest.mark.parametrize("text, day", [
    # 1 September 00:00 + 12 hours is 1 September 12:00
    ("12 hours after next summer", date(2027, 9, 1)),
    # 1 July 00:00 + 36 hours is 2 July 12:00
    ("36 hours after june 2027", date(2027, 7, 2)),
    # 1 July 00:00 + 30 minutes is 1 July 00:30
    ("30 minutes after june 2027", date(2027, 7, 1)),
    # 26 December 00:00 + 2 hours
    ("2 hours after christmas", date(2026, 12, 26)),
])
def test_a_sub_day_offset_counts_from_the_end_of_the_reference(text, day):
    assert _day(text) == day


@pytest.mark.parametrize("lang, text, day", [
    # 30 June is the last day; 1, 2 July then 5 July (3 and 4 July are a weekend)
    ("en", "3 business days after june 2027", date(2027, 7, 5)),
    # 31 August is a Tuesday; 1, 2 and 3 September follow
    ("en", "3 business days after next summer", date(2027, 9, 3)),
    ("pt", "3 dias úteis depois de junho de 2027", date(2027, 7, 5)),
    ("de", "3 Werktage nach Juni 2027", date(2027, 7, 5)),
])
def test_a_business_day_offset_counts_from_the_last_day(lang, text, day):
    assert _day(text, lang) == day


@pytest.mark.parametrize("text, day", [
    # controls: a before offset still ends at the start of the reference
    ("12 hours before next summer", date(2027, 5, 31)),
    ("3 business days before june 2027", date(2027, 5, 27)),
    # controls: one civil day or a longer unit is unchanged
    ("a week after march 2027", date(2027, 4, 7)),
    ("a month after march 2027", date(2027, 4, 1)),
    ("5 business days after christmas", date(2027, 1, 1)),
])
def test_other_offsets_keep_their_base(text, day):
    assert _day(text) == day


@pytest.mark.parametrize("text, day", [
    # 1992 is a leap year of 366 days, so a year is not shorter than it
    ("a year after 1992", date(1993, 1, 1)),
    ("a year after 1991", date(1992, 1, 1)),
    ("2 years after 1990", date(1992, 1, 1)),
])
def test_a_year_after_a_year_counts_year_by_year(text, day):
    assert _day(text) == day


@pytest.mark.parametrize("lang, text, reference", [
    ("en", "an hour after tomorrow morning", "tomorrow morning"),
    ("en", "10 minutes after tomorrow morning", "tomorrow morning"),
    ("en", "30 minutes after monday morning", "monday morning"),
    ("en", "2 hours after tomorrow evening", "tomorrow evening"),
    ("en", "an hour after christmas morning", "christmas morning"),
    ("pt", "uma hora depois de amanhã de manhã", "amanhã de manhã"),
    ("es", "una hora después de mañana por la mañana", "mañana por la mañana"),
])
def test_a_sub_day_offset_before_a_part_of_the_day_keeps_its_day(
        lang, text, reference):
    """The part of the day attaches to the shifted day, so the offset must
    not move the reference to the next day."""
    got = extract_timespan(text, lang, anchor=ANCHOR)
    want = extract_timespan(reference, lang, anchor=ANCHOR)
    assert (got.span, got.remainder) == (want.span, "")
