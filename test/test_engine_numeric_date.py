"""numeric_date: slash/dash separated numeric dates ("12/11/2024", "5-6-24").

Regression guard for a silent-wrong bug: before this construction the
tokenizer dropped the "/" and "-" separators and the engine bound only the
bare 4-digit year, so "12/11/2024" resolved to the *year* 2024 (Jan 1) and
silently stranded "12/11" in the remainder.  Now the whole numeric date binds
one ``NUMDATE`` literal and resolves day-wide, honouring each locale's ``dmy``
day/month order.

Behaviour under test (hand-derived against the fixed anchor):

* component order follows ``dmy``: dmy=true reads day-first, dmy=false
  month-first;
* the >12 disambiguation swap: the component the locale flag would read as a
  month, when it exceeds 12 and the other is a valid month, is taken as the
  day instead ("13/12/2024" is 13 December even month-first);
* impossible dates resolve to nothing (never fabricated);
* a bare fraction "1/2" (no year component) never reads as a date;
* the bare-year and clock readings are untouched.
"""
from datetime import datetime

import pytest
from engine_helpers import ANCHOR, zz_engine

from chronologia.astrodate import AstroDate
from chronologia.extract import DateTimeEngine, extract_timespan
from chronologia.extract.loader import load_lang_spec
from chronologia.resolution import DateTimeResolution

# real-locale engines: en is month-first (dmy=false), pt is day-first
# (dmy=true) -- the two orders the construction must tell apart.
EN = DateTimeEngine(load_lang_spec("en"))
PT = DateTimeEngine(load_lang_spec("pt"))


def _one(engine, text):
    res = engine.resolve(text, ANCHOR)
    assert len(res) == 1, f"{text!r} -> {res}"
    return res[0]


def _none(engine, text):
    assert engine.resolve(text, ANCHOR) == [], text


# -- en: month-first (dmy=false) -------------------------------------------

def test_en_slash_is_month_first():
    r = _one(EN, "12/11/2024")
    assert r.value.start == AstroDate(2024, 12, 11)      # December 11
    assert r.value.end == AstroDate(2024, 12, 12)
    assert r.value.resolution == DateTimeResolution.DAY


def test_en_slash_explicit_month_first():
    assert _one(EN, "6/15/2024").value.start == AstroDate(2024, 6, 15)


def test_en_dash_is_month_first():
    assert _one(EN, "12-11-2024").value.start == AstroDate(2024, 12, 11)


def test_en_two_digit_year_pivots():
    # 24 -> 2024 via the POSIX %y pivot (00-68 -> 2000s)
    assert _one(EN, "6/15/24").value.start == AstroDate(2024, 6, 15)


def test_en_slash_date_in_a_sentence_leaves_remainder():
    r = extract_timespan("the invoice dated 03/15/2024 is overdue", "en-us",
                         ANCHOR)
    assert r.span.start == AstroDate(2024, 3, 15)
    assert r.remainder == "the invoice dated is overdue"


# -- pt: day-first (dmy=true), incl. the >12 unambiguous swap ---------------

def test_pt_slash_is_day_first():
    assert _one(PT, "15/06/2024").value.start == AstroDate(2024, 6, 15)


def test_pt_first_over_12_swaps_to_day_first_reading():
    # 06/15: the flag says month-of-15 which is impossible, so 15 is the day
    assert _one(PT, "06/15/2024").value.start == AstroDate(2024, 6, 15)


def test_pt_all_ambiguous_follows_locale_flag():
    # 01/02/03: every component <= 12, so no swap -> day 1, month 2, year 2003
    assert _one(PT, "01/02/03").value.start == AstroDate(2003, 2, 1)


# -- en: the mirror-image swap in a month-first locale ---------------------

def test_en_first_over_12_is_day_first():
    # 13/12/2024: 13 can be no month, so month-first is impossible -> 13 Dec
    assert _one(EN, "13/12/2024").value.start == AstroDate(2024, 12, 13)


# -- adversarial: impossible / non-date shapes resolve to nothing ----------

@pytest.mark.parametrize("engine", [EN, PT])
@pytest.mark.parametrize("text", [
    "13/13/2024",    # no valid month in either order
    "00/05/2024",    # day 0 is impossible
    "31/02/2024",    # February has no 31st
    "99/99/99",      # nonsense
])
def test_impossible_numeric_date_resolves_to_none(engine, text):
    _none(engine, text)


def test_bare_fraction_is_not_a_date():
    # "1/2" has no year component -> the NUMDATE literal never matches, so a
    # fraction/score is never mistaken for a date.
    assert extract_timespan("1/2 cup of flour", "en-us", ANCHOR) is None


def test_bare_year_reading_untouched():
    # a lone 4-digit year is still a year-wide span; the numeric date does not
    # shadow it.
    r = _one(EN, "2024")
    assert r.value.start == AstroDate(2024, 1, 1)
    assert r.value.end == AstroDate(2025, 1, 1)
    assert r.value.resolution == DateTimeResolution.YEAR


def test_slashless_clock_phrase_untouched():
    # "5 to 3" is a clock reading, not a date -- unaffected by the construction
    # (a slash/dash is required for a numeric date, and there is none here)
    res = EN.resolve("5 to 3", ANCHOR)
    assert res and res[0].value.start == AstroDate(2017, 6, 28, 2, 55)


# -- zz synthetic locale (dmy=true): construction plumbing + swap ----------

def test_zz_numeric_date_day_first():
    assert _one(zz_engine(), "15/06/2024").value.start == AstroDate(2024, 6, 15)


def test_zz_numeric_date_swap_and_two_digit_year():
    assert _one(zz_engine(), "06/15/24").value.start == AstroDate(2024, 6, 15)


@pytest.mark.parametrize("text", ["13/13/2024", "31/02/2024", "00/00/00"])
def test_zz_numeric_date_impossible_none(text):
    _none(zz_engine(), text)


def test_en_region_subtag_selects_dmy_vs_mdy():
    # English is the one base language whose numeric day/month order splits by
    # region: US mdy, the rest of the anglosphere dmy. '03/04/2020' is March 4
    # in en-us but 3 April in en-gb/au/nz/ie/in/za. The bare 'en' keeps the US
    # default. Regression: _timespan_engine collapsed every en-* to bare 'en'.
    import datetime
    from chronologia import extract_timespan
    A = datetime.datetime(2017, 6, 27, 13, 4)
    for lang in ("en-gb", "en-au", "en-nz", "en-ie", "en-in", "en-za"):
        r = extract_timespan("03/04/2020", lang, A)
        assert (r.span.start.month, r.span.start.day) == (4, 3), lang
    for lang in ("en-us", "en"):
        r = extract_timespan("03/04/2020", lang, A)
        assert (r.span.start.month, r.span.start.day) == (3, 4), lang
    # unambiguous forms and the >12 swap are region-invariant
    for lang in ("en-us", "en-gb"):
        assert extract_timespan("15/06/2020", lang, A).span.start.month == 6
        assert extract_timespan("13/12/2024", lang, A).span.start.day == 13
