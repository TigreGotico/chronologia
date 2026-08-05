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


@pytest.mark.parametrize("gematria,numeric", [
    ("כ״ה בכסלו תשפ״ז", "25 בכסלו תשפ״ז"),   # 25 Kislev 5787
    ("ט״ו בשבט תשפ״ז", "15 בשבט תשפ״ז"),     # Tu BiShvat, 15 Shevat
    ("כ״ה בכסלו", "25 בכסלו"),                # day + month, no year
])
def test_gematria_day_of_month_matches_numeric(gematria, numeric):
    # In Hebrew day-month order the gematria DAY precedes the month; it used to
    # be dropped, fabricating day 1 (a confident wrong date).  It must now fold
    # as the day (raw gematria value, no implied +5000) and resolve identically
    # to the numeric-day spelling.
    from datetime import datetime
    from chronologia import extract_timespan

    def _se(text):
        r = extract_timespan(text, "he", datetime(2027, 3, 15, 9, 0))
        return None if r is None else (r[0].start, r[0].end)

    assert _se(gematria) is not None
    assert _se(gematria) == _se(numeric)


@pytest.mark.parametrize("gematria,numeric", [
    ("ל״ה בכסלו", "35 בכסלו"),   # 35 Kislev: impossible day
    ("ל״א בכסלו", "31 בכסלו"),   # 31 Kislev: impossible day
])
def test_out_of_range_gematria_day_declines_like_numeric(gematria, numeric):
    # an impossible gematria day must resolve to None exactly as the numeric
    # spelling does (calendar_date rejects it), not leave the numeral unfolded
    # and let the bare month resolve to a confident whole-month span.
    from datetime import datetime
    from chronologia import extract_timespan
    a = datetime(2027, 3, 15, 9, 0)
    assert extract_timespan(numeric, "he", a) is None
    assert extract_timespan(gematria, "he", a) is None


def test_gematria_day_does_not_swallow_abbreviations_or_bare_numerals():
    # a gershayim-marked abbreviation (weekend סופ״ש) or a bare marked numeral
    # not before a month must NOT fold as a day-of-month date.
    from datetime import datetime
    from chronologia import extract_timespan
    a = datetime(2027, 3, 15, 9, 0)
    assert extract_timespan("לפנה״ס", "he", a) is None
    assert extract_timespan("כ״ה", "he", a) is None       # bare, no month
    # numeric-day and gematria-year paths are unchanged
    assert extract_timespan("15 אדר 5785", "he", a)[0].start.date().isoformat() == "2025-03-15"
    assert extract_timespan("15 אדר תשפ״ה", "he", a)[0].start.date().isoformat() == "2025-03-15"


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


@pytest.mark.parametrize("gematria,numeric", [
    ("א׳ בניסן תשפ״ה", "1 בניסן תשפ״ה"),    # single-letter geresh: 1 Nisan
    ("ה׳ בכסלו תשפ״ה", "5 בכסלו תשפ״ה"),    # 5 Kislev
    ("י׳ בניסן תשפ״ה", "10 בניסן תשפ״ה"),   # 10 Nisan
    ("כ׳ בניסן תשפ״ה", "20 בניסן תשפ״ה"),   # 20 Nisan
    ("ל׳ בניסן תשפ״ה", "30 בניסן תשפ״ה"),   # 30 Nisan (Nisan always has 30 days)
])
def test_single_letter_geresh_day_matches_numeric(gematria, numeric):
    # Regression for a silent-wrong: a TRAILING geresh marks a single-letter
    # gematria numeral (א׳ = 1, ה׳ = 5, י׳ = 10, כ׳ = 20, ל׳ = 30), unlike the
    # multi-letter gershayim form where the mark sits BETWEEN letters
    # (ט״ו = 15).  Before the tokenizer kept the trailing mark, the word-glue
    # regex dropped it as a stray char, ``is_gematria_numeral`` saw an
    # unmarked letter and refused to fold it, and the numeral fell into the
    # remainder while the bare month resolved to a confident whole-month span
    # -- e.g. "א׳ בניסן תשפ״ה" used to yield the whole of Nisan with
    # remainder "א" instead of the single day 1 Nisan.
    from datetime import datetime
    from chronologia import extract_timespan
    a = datetime(2020, 6, 1, 12, 0)

    def _se(text):
        r = extract_timespan(text, "he", a)
        return None if r is None else (r[0].start, r[0].end)

    assert _se(gematria) is not None
    assert _se(gematria) == _se(numeric)


def test_single_letter_geresh_pinned_gregorian():
    # 1 Nisan 5785, pinned independently: 15 Nisan 5785 is the attested
    # Gregorian date of Passover eve, 2025-04-13 (see test_gematria_pinned_
    # gregorian above for the parallel Adar pin); Nisan always has 30 days,
    # so 1 Nisan = 15 Nisan minus 14 days = 2025-03-30.
    from datetime import datetime
    from chronologia import extract_timespan
    a = datetime(2020, 6, 1, 12, 0)
    got = extract_timespan("א׳ בניסן תשפ״ה", "he", a)
    assert got is not None and got.remainder == ""
    assert got[0].start.date().isoformat() == "2025-03-30"
    assert got[0].end.date().isoformat() == "2025-03-31"


def test_trailing_geresh_does_not_leak_outside_hebrew():
    # the trailing-geresh allowance is restricted to the real geresh/
    # gershayim characters (not their ASCII '/" fallbacks), so it must stay
    # completely inert for English contractions and French elisions, whose
    # apostrophe is the ASCII character and always sits BETWEEN letters.
    from datetime import datetime
    from chronologia import extract_timespan
    a = datetime(2020, 6, 1, 12, 0)
    en = extract_timespan("3 o'clock", "en", a)
    assert en is not None and en[0].start.hour == 3
    fr = extract_timespan("l'après-midi le 3 juin", "fr", a)
    assert fr is not None and fr[0].start.month == 6 and fr[0].start.day == 3


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
