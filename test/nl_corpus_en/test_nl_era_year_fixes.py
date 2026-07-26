"""Era-year extraction fixes.

Four verified silent-wrongs in ERA-YEAR / historical extraction:

1. era-year epoch offset not applied in extraction (the era name was stranded
   and the literal number used as the Gregorian year);
2. malformed ``(None, date)`` half-open spans for pre-year-1 references;
3. ``"the year 1 AM"`` captured by the ante-meridiem clock parser instead of
   read as the Anno Mundi era marker;
4. ``"eve of"`` -1-day offset not applied to a Roman-anchor date.

Reference values are independent of the parser -- they come straight from
:func:`chronologia.resolve_era`, the epoch-correct registry resolver.
"""
import pytest

from chronologia import extract_timespan, resolve_era

from ._corpus import ANCHOR, parse, span


# -- defect 1: era-year epoch offset applied + era name consumed ----------
@pytest.mark.parametrize("text, era_key, value", [
    ("in Saka 1900", "saka", 1900),
    ("in the year 6260 of the Byzantine era", "byzantine_am", 6260),
    ("in the Holocene year 12026", "holocene", 12026),
])
def test_era_year_resolves_through_epoch(text, era_key, value):
    s = span(text)
    expected = resolve_era(era_key, value)
    assert s.start.year == expected.year
    assert parse(text)[1] == ""          # era name fully consumed


def test_bare_five_digit_year_stays_literal():
    # a bare 5-digit year keeps its literal (far-future) Gregorian reading --
    # only an explicit "Holocene year" surface applies the HE == CE + 10000
    # offset.  The literal span is symmetric (both endpoints out of datetime
    # range), so it is not a malformed None-start span.
    s = span("the year 12026")
    assert s.start.year == 12026
    assert s.start_datetime is None and s.end_datetime is None


# -- defect 2: never a None-start span (BC/AUC prefixed -> clean None) -----
@pytest.mark.parametrize("text", [
    "in the year 1 BC",
    "in the year 753 ab urbe condita",
])
def test_prefixed_bce_returns_none_not_malformed_span(text):
    assert extract_timespan(text, "en", ANCHOR) is None


def test_no_none_start_span_for_target_phrases():
    for text in ["in Saka 1900", "in the year 6260 of the Byzantine era",
                 "in the Holocene year 12026", "the year 12026",
                 "in the year 1 AM", "on the eve of the Ides of March"]:
        r = extract_timespan(text, "en", ANCHOR)
        if r is None:
            continue
        s = r[0]
        assert not (s.start_datetime is None
                    and s.end_datetime is not None), \
            f"{text!r} produced a malformed None-start span"


# -- defect 3: 'the year 1 AM' is not a 1am clock -------------------------
def test_year_one_am_not_clock():
    r = extract_timespan("in the year 1 AM", "en", ANCHOR)
    # the ante-meridiem clock parser must no longer capture "1 am" after
    # "the year"; the tiny-value Anno Mundi era is BCE (out of datetime
    # range), so the clean answer is no match.
    assert r is None


def test_year_5780_am_unchanged():
    # byte-identical: 5780 reads as the plain year, "am" is not a clock.
    s = span("in the year 5780 AM")
    assert s.start.year == 5780


# -- defect 4: eve of the Ides of March -> the day before -----------------
def test_eve_of_ides_of_march():
    s = span("on the eve of the Ides of March")
    assert (s.start.year, s.start.month, s.start.day) == (2017, 3, 14)


def test_eve_of_christmas_unchanged():
    s = span("the eve of Christmas")
    assert (s.start.month, s.start.day) == (12, 24)
