# -*- coding: utf-8 -*-
"""The Anno Mundi era: "anno mundi 5786" -> the Gregorian span of that
year-of-Creation year (Hebrew AM epoch, 3761 BC).

The era arithmetic (chronologia.eras) was already implemented and the
era_anno_mundi vocab shipped, but no construction wired the "anno mundi" marker
into the extraction grammar, so the phrase stranded and the number read as a
plain Gregorian year.  Gold is computed INDEPENDENTLY through resolve_era, not
read back from the extractor.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan, resolve_era

_A = datetime(2017, 6, 27, 13, 4)


@pytest.mark.parametrize("text", [
    "anno mundi 5786",
    "5786 anno mundi",
    "the year 5786 anno mundi",
    "in the year 5786 anno mundi",
])
def test_anno_mundi_year_resolves_through_its_epoch(text):
    # independent gold: the Gregorian date resolve_era gives for AM 5786
    gold = resolve_era("anno_mundi", 5786)
    r = extract_timespan(text, "en", _A)
    assert r is not None
    assert r[0].start_datetime.date() == gold
    assert getattr(r, "remainder", "") == ""


def test_anno_mundi_span_end_is_calendar_exact_not_a_gregorian_year():
    # AM is Hebrew-calendar-backed (variable-length years), so the span must end
    # at the true NEXT Rosh Hashanah, not the naive same-day-plus-one-Gregorian-
    # year (which was ~11 days too late).  Gold from the calendar-exact primitive.
    from chronologia.eras import resolve_era_year_span
    gstart, gend = resolve_era_year_span("anno_mundi", 5786)
    r = extract_timespan("anno mundi 5786", "en", _A)
    assert r is not None
    assert r[0].start_datetime.date() == gstart
    assert r[0].end_datetime.date() == gend        # 2026-09-12, not 2026-09-23


def test_anno_mundi_older_year():
    r = extract_timespan("in anno mundi 5000", "en", _A)
    assert r is not None
    assert r[0].start_datetime.date() == resolve_era("anno_mundi", 5000)


@pytest.mark.parametrize("text,want_year", [
    ("the year 5786", 5786),     # no "anno mundi" marker -> a plain Gregorian year
    ("5786", 5786),
    ("the year 2020", 2020),
])
def test_bare_year_is_not_anno_mundi(text, want_year):
    r = extract_timespan(text, "en", _A)
    assert r is not None and r[0].start_datetime.year == want_year


@pytest.mark.parametrize("text", ["9 am", "at 9 am", "3 am tomorrow"])
def test_am_meridiem_is_not_swallowed_by_anno_mundi(text):
    # the era marker is the full phrase "anno mundi", never bare "am", so the
    # ante-meridiem clock reading is untouched.
    r = extract_timespan(text, "en", _A)
    assert r is not None
    assert r[0].start_datetime.hour in (3, 9)
