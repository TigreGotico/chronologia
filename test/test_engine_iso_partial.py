"""ISO-8601 year-first partial and slash dates.

Regression guard for a silent-wrong bug: a year-first numeric date that was
not the strict ``YYYY-MM-DD`` dash form dropped its tail and collapsed to the
bare year.  "2024-03" (ISO year-month) returned the whole *year* 2024 with
"03" stranded in the remainder; "2024/03/06" (slash, year-first) likewise
bound only the year and stranded "03/06".

The one ``iso_date`` construction now covers three year-first shapes, all
unambiguously Y-M-D (year-first order is locale-independent -- no ``dmy`` swap
ever applies, unlike the day/month-ambiguous ``numeric_date`` family):

* ``YYYY-MM-DD`` / ``YYYY/MM/DD`` -> a **day-wide** span;
* ``YYYY-MM`` (year-month, dash only per ISO-8601) -> the **month-wide** span
  the named month occupies -- the same width "June 2027" resolves to.

An invalid month in the year-month form ("2024-13") names no month, and an
impossible day ("2024/02/31") names no day: both resolve to nothing rather
than silently collapsing to the bare year.  The slash year-month "2024/03" is
deliberately out of scope (ISO-8601 writes the year-month only with a dash).

Behaviour is hand-derived against the fixed anchor.
"""
import pytest
from engine_helpers import ANCHOR

from chronologia.astrodate import AstroDate
from chronologia.extract import DateTimeEngine, extract_timespan
from chronologia.extract.loader import load_lang_spec
from chronologia.resolution import DateTimeResolution

EN = DateTimeEngine(load_lang_spec("en"))
PT = DateTimeEngine(load_lang_spec("pt"))


def _one(engine, text):
    res = engine.resolve(text, ANCHOR)
    assert len(res) == 1, f"{text!r} -> {res}"
    return res[0]


def _none(engine, text):
    assert engine.resolve(text, ANCHOR) == [], text


# -- ISO year-month "YYYY-MM" -> a month-wide span -------------------------

def test_iso_year_month_is_month_wide():
    r = _one(EN, "2024-03")
    assert r.value.start == AstroDate(2024, 3, 1)
    assert r.value.end == AstroDate(2024, 4, 1)
    assert r.value.resolution == DateTimeResolution.MONTH


def test_iso_year_month_december_wraps_the_year():
    r = _one(EN, "2024-12")
    assert r.value.start == AstroDate(2024, 12, 1)
    assert r.value.end == AstroDate(2025, 1, 1)


def test_iso_year_month_is_locale_independent():
    # year-first is Y-M-D everywhere; a day-first locale reads it identically.
    assert _one(PT, "2024-03").value.start == AstroDate(2024, 3, 1)


def test_iso_year_month_in_a_sentence_leaves_remainder():
    r = extract_timespan("report for 2024-03 is due", "en-us", ANCHOR)
    assert r.span.start == AstroDate(2024, 3, 1)
    assert r.span.end == AstroDate(2024, 4, 1)
    assert r.remainder == "report for is due"


# -- year-first slash full date "YYYY/MM/DD" -> day-wide, no dmy swap -------

def test_slash_year_first_full_date():
    r = _one(EN, "2024/03/06")
    assert r.value.start == AstroDate(2024, 3, 6)
    assert r.value.end == AstroDate(2024, 3, 7)
    assert r.value.resolution == DateTimeResolution.DAY


def test_slash_year_first_is_iso_order_not_locale_dmy():
    # day-first locale must NOT swap a year-first surface: still 6 March.
    assert _one(PT, "2024/03/06").value.start == AstroDate(2024, 3, 6)


def test_slash_year_first_one_digit_components():
    assert _one(EN, "2024/3/6").value.start == AstroDate(2024, 3, 6)


# -- the strict dash full date is unchanged --------------------------------

def test_full_dash_iso_still_day_wide():
    r = _one(EN, "2024-03-06")
    assert r.value.start == AstroDate(2024, 3, 6)
    assert r.value.end == AstroDate(2024, 3, 7)
    assert r.value.resolution == DateTimeResolution.DAY


# -- adversarial: invalid month / impossible day resolve to nothing --------

@pytest.mark.parametrize("engine", [EN, PT])
@pytest.mark.parametrize("text", [
    "2024-13",       # month 13 names no month (must NOT collapse to year 2024)
    "2024-00",       # month 0 is impossible
    "2024/13/06",    # year-first slash, month 13
    "2024/02/31",    # February has no 31st
    "2024/06/00",    # day 0 is impossible
])
def test_invalid_iso_partial_resolves_to_none(engine, text):
    _none(engine, text)


def test_iso_year_month_does_not_collapse_to_bare_year():
    # the whole point of the fix: an invalid year-month yields NO date, never
    # the silently-wrong bare year that the old tail-drop produced.
    assert extract_timespan("2024-13", "en-us", ANCHOR) is None


# -- adversarial: non-date numeric shapes stay non-dates -------------------

def test_decimal_is_not_a_date():
    assert extract_timespan("3.14", "en-us", ANCHOR) is None


def test_bare_fraction_is_not_a_date():
    assert extract_timespan("1/2 cup of flour", "en-us", ANCHOR) is None


def test_bare_year_still_year_wide():
    r = extract_timespan("2024", "en-us", ANCHOR)
    assert r.span.start == AstroDate(2024, 1, 1)
    assert r.span.end == AstroDate(2025, 1, 1)


def test_the_year_phrase_unchanged():
    r = extract_timespan("the year 2024", "en-us", ANCHOR)
    assert r.span.start == AstroDate(2024, 1, 1)
    assert r.span.end == AstroDate(2025, 1, 1)


def test_day_first_numeric_date_still_dmy():
    # the 1-2-digit-first numeric_date family is untouched: month-first en.
    assert extract_timespan("12/11/2024", "en-us", ANCHOR).span.start \
        == AstroDate(2024, 12, 11)


def test_slash_year_month_is_out_of_scope_bare_year():
    # "2024/03" (slash year-month) is deliberately not an ISO year-month; the
    # engine reads the leading year only, as before -- documented follow-up.
    r = extract_timespan("2024/03", "en-us", ANCHOR)
    assert r.span.start == AstroDate(2024, 1, 1)
    assert r.span.end == AstroDate(2025, 1, 1)
