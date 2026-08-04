# -*- coding: utf-8 -*-
"""Traditional Hebrew *gematria* year numerals (תשפ״ה = 5785) in a date.

A Hebrew-calendar year written with letters must resolve like the same year
written with digits.  The Gregorian expectation is never pinned from the
parser -- it is asserted to equal the numeric-year form, whose spans are
already fixed by ``test_nl_other_calendars`` -- and the gematria→integer
conversion is unit-checked against the independent arithmetic of the numeral
letters (ת=400, ש=300, פ=80, ה=5 → 785, +5000 implied = 5785).

Before this feature the gematria year was dropped: "15 אדר תשפ״ה" parsed to
the anchor-year Adar (2018-03-02 at the corpus anchor) with the numeral left
in the remainder, a confident wrong date.
"""
import pytest

from chronologia.hebrew_numerals import (gematria_value, hebrew_year_value,
                                          is_gematria_numeral)


@pytest.mark.parametrize("gematria,numeric", [
    ("15 אדר תשפ״ה", "15 אדר 5785"),
    ("15 אדר תש״ף", "15 אדר 5780"),
    ("15 אדר תשפ״ד", "15 אדר 5784"),
    ("אדר תשפ״ה", "אדר 5785"),           # bare month-year (no day): BOTH forms
                                          # name no date -> None (parity holds)
    ("15 אדר ה׳תשפ״ה", "15 אדר 5785"),   # explicit full-count thousands
])
def test_gematria_year_matches_numeric(gematria, numeric):
    # true parity: the gematria year must resolve IDENTICALLY to the numeric
    # year -- whether that is a concrete span or None.  A bare he month+year
    # with no day names no date (the numeric "אדר 5785" is None too), so the
    # equality, not a non-None span, is what this pins.
    from datetime import datetime
    from chronologia import extract_timespan

    def _se(text):
        r = extract_timespan(text, "he", datetime(2020, 6, 1, 12, 0))
        return None if r is None else (r[0].start, r[0].end)

    assert _se(gematria) == _se(numeric)


def test_gematria_pinned_gregorian():
    """The reference case, pinned to its fixed Gregorian date (15 Adar 5785)."""
    from datetime import datetime
    from chronologia import extract_timespan
    a = datetime(2020, 6, 1, 12, 0)
    got = extract_timespan("15 אדר תשפ״ה", "he", a)
    assert got is not None and got.remainder == ""
    assert got[0].start.date().isoformat() == "2025-03-15"


def test_numeric_year_unchanged():
    """Regression guard: the numeric Hebrew year must not change."""
    from datetime import datetime
    from chronologia import extract_timespan
    a = datetime(2020, 6, 1, 12, 0)
    assert (extract_timespan("15 אדר 5785", "he", a)[0].start.date().isoformat()
            == "2025-03-15")


@pytest.mark.parametrize("text,value", [
    ("ה", 5), ("תק", 500), ("תשפה", 785), ("תשפד", 784), ("תשף", 780),
])
def test_gematria_value(text, value):
    assert gematria_value(text) == value


@pytest.mark.parametrize("text,year", [
    ("תשפ״ה", 5785), ("תש״ף", 5780), ("תשפ״ד", 5784),
    ("ה׳תשפ״ה", 5785),   # full count, explicit thousands
])
def test_hebrew_year_value(text, year):
    assert hebrew_year_value(text) == year


def test_is_gematria_numeral_requires_mark():
    # a marked numeral is one
    assert is_gematria_numeral("תשפ״ה")
    assert is_gematria_numeral("ה׳תשפ״ה")
    # unmarked letter runs (ordinary words / weekday names) are NOT
    assert not is_gematria_numeral("אדר")      # month name
    assert not is_gematria_numeral("ראשון")    # Sunday
    assert not is_gematria_numeral("שני")      # Monday
