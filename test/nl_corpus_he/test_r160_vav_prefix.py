# -*- coding: utf-8 -*-
"""R160: the vav-conjunction proclitic ו ("and") glued onto a date/holiday
word ("ומחר" and-tomorrow) must resolve exactly like the bare word.

Hebrew glues ו directly onto the following word, no space -- unlike the
bet-preposition ב ("in"), which the existing locale data already handles for
months as a curated literal DUPLICATE surface ("ינואר" and "בינואר" both
listed in month_1.voc). That approach cannot reach the holiday surfaces
(harvested from ``well_known.tab`` at load time) or a multi-word holiday
("חג הפסח"), so the fix is a token-level strip in the ``he`` fold hook
(``numfold_semitic._he_vav_strip``): a ו-initial token folds to its bare
remainder only when that remainder is one of a curated closed set of
Hebrew date/holiday stems, so a real ו-initial root word is never touched.

Before the fix: every ``ו``-prefixed surface below either dropped the whole
mention (named days) or silently kept parsing as a bare year, stranding the
prefixed word in the remainder (``ופסח 2026`` -> whole-year 2026, ``פסח``
lost) instead of resolving the holiday/month it actually names.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, span, start, nomatch


# --------------------------------------------------------------------------
# Named days -- total drop before the fix.
# --------------------------------------------------------------------------
@pytest.mark.parametrize("text,ymd", [
    ("ומחר", (2017, 6, 28)),
    ("והיום", (2017, 6, 27)),
    ("ואתמול", (2017, 6, 26)),
    ("ומחרתיים", (2017, 6, 29)),
    ("ומחרתים", (2017, 6, 29)),
])
def test_vav_named_day(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


# --------------------------------------------------------------------------
# Holidays -- silently wrong (whole-year span, holiday word stranded) before
# the fix.
# --------------------------------------------------------------------------
def test_vav_holiday_bare():
    assert start("וחנוכה") == AstroDate(2017, 12, 13)


def test_vav_holiday_multiword():
    """"וחג הפסח" -- the ו glues onto the FIRST word of the two-word surface
    "חג הפסח"; the strip must leave "חג" "הפסח" for the multiword-merge pass
    to glue back together, not eat the surface."""
    assert start("וחג הפסח") == AstroDate(2018, 3, 31)


def test_vav_holiday_explicit_year():
    r = span("ופסח 2026")
    assert r.start == AstroDate(2026, 4, 2)
    assert r.width == timedelta(days=1)


# --------------------------------------------------------------------------
# Months -- silently wrong (whole-year span) before the fix.
# --------------------------------------------------------------------------
def test_vav_month_year():
    r = span("וינואר 2020")
    assert r.start == AstroDate(2020, 1, 1)
    assert r.end == AstroDate(2020, 2, 1)


@pytest.mark.parametrize("text,month", [
    ("ופברואר", 2), ("ומרץ", 3), ("ומרס", 3), ("ואפריל", 4), ("ומאי", 5),
    ("ויוני", 6), ("ויולי", 7), ("ואוגוסט", 8), ("וספטמבר", 9),
    ("ואוקטובר", 10), ("ונובמבר", 11), ("ודצמבר", 12),
])
def test_vav_month_bare(text, month):
    assert span(text).start == AstroDate(2017, month, 1)


# --------------------------------------------------------------------------
# Controls: nothing the fix touches must regress.
# --------------------------------------------------------------------------
def test_control_bare_named_days_unaffected():
    assert start("מחר") == AstroDate(2017, 6, 28)
    assert start("היום") == AstroDate(2017, 6, 27)
    assert start("אתמול") == AstroDate(2017, 6, 26)


def test_control_bare_holiday_and_month_unaffected():
    assert start("פסח 2026") == AstroDate(2026, 4, 2)
    assert start("ינואר 2020") == AstroDate(2020, 1, 1)


def test_control_bet_prefixed_month_unaffected():
    """The already-working ב- ("in") month prefix must keep working exactly
    as before -- the vav strip is scoped to ו only."""
    assert span("בינואר").start == AstroDate(2017, 1, 1)


def test_control_bet_vav_combo_unaffected():
    """"וב-15 בינואר 2020" (and-on-the-15th-of-January-2020) already worked
    pre-fix (evidence a Hebrew ב- prefix mechanism existed); must still."""
    assert start("וב-15 בינואר 2020") == AstroDate(2020, 1, 15)


def test_control_gematria_year_unaffected():
    """A gematria numeral has no leading ו and is unrelated to the vav
    strip -- pinned as a neighbouring-mechanism control (full battery in
    test_nl_gematria_year.py)."""
    assert start("15 אדר תשפ״ה") == AstroDate(2025, 3, 15)


def test_control_real_vav_initial_word_not_stripped():
    """A genuine word that happens to start with ו but whose remainder is
    NOT a curated date/holiday stem must be left alone entirely."""
    nomatch("ורוד")  # "pink" -- not a date word, remainder not a stem


# --------------------------------------------------------------------------
# Multi-mention: the vav-prefixed mention must no longer silently vanish.
# --------------------------------------------------------------------------
def test_vav_multimention_three_present():
    from chronologia.extract import extract_timespans
    ms = extract_timespans(
        'אתמול הייתי בעבודה, היום אני בבית, ומחר אטוס לחו״ל.', "he", ANCHOR)
    assert len(ms) == 3
    assert [m.span.start for m in ms] == [
        AstroDate(2017, 6, 26), AstroDate(2017, 6, 27), AstroDate(2017, 6, 28)]
