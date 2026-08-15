# -*- coding: utf-8 -*-
"""Recurrence in Italian: ``extract_recurrence(text, "it")`` -> RRULE.

R173: Italian shipped no recurrence vocab at all (``marker_every.voc``,
``marker_freq_daily/weekly/monthly/yearly.voc`` were absent from
``locale/it/``) -- the recurrence grammar itself lives in the base engine and
is entirely vocab-driven, so every recurring-phrase probe silently returned
``None``.  The fix adds only the five missing vocab files, mirroring the
``es``/``fr``/``pt`` siblings' surfaces and file structure -- no grammar
code changed.
"""
import pytest

from chronologia.extract import extract_recurrence, extract_timespan

LANG = "it"

_CASES = [
    ("ogni lunedì", "FREQ=WEEKLY;BYDAY=MO", ""),
    ("ogni giorno", "FREQ=DAILY", ""),
    ("ogni 2 settimane", "FREQ=WEEKLY;INTERVAL=2", ""),
    ("settimanalmente il lunedì", "FREQ=WEEKLY;BYDAY=MO", ""),
    ("quotidianamente", "FREQ=DAILY", ""),
    ("giornalmente", "FREQ=DAILY", ""),
    ("settimanalmente", "FREQ=WEEKLY", ""),
    ("mensilmente", "FREQ=MONTHLY", ""),
    ("annualmente", "FREQ=YEARLY", ""),
    # "tutti i"/"tutte le" -- the plural-determiner reading of "every" --
    # works through the SAME general article-combining mechanism the "fr"
    # sibling's "tous les"/"toutes les" uses (``marker_article.voc`` already
    # carries "i"/"gli"/"le" for "it"); mirrored here, not invented.
    ("tutti i lunedì", "FREQ=WEEKLY;BYDAY=MO", ""),
    ("tutte le settimane", "FREQ=WEEKLY", ""),
    # "in <month>" parallels the es sibling's "en junio" via the SAME
    # ``marker_in`` connector ("in" was already wired for "it" -- unlike
    # "el"/"the" for a day-of-month, see the skip below).
    ("annualmente in giugno", "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=1", ""),
    ("ogni mese il 15", "FREQ=MONTHLY;BYMONTHDAY=15", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ["lunedì", "il lunedì"])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None


def test_ognissanti_holiday_not_corrupted_by_every_marker():
    # "ogni" (the new "every" marker) is a strict prefix of "ognissanti"
    # ("All Saints") -- tokenization is whole-word, so the new vocab entry
    # must not bleed into the holiday match. Guards R173's own risk.
    got = extract_timespan("ognissanti 2026", LANG)
    assert got is not None
    span, remainder = got
    assert (span.start.year, span.start.month, span.start.day) == (2026, 11, 1)
    assert remainder == ""


def test_ognissanti_alone_still_a_holiday_date_not_a_recurrence():
    assert extract_recurrence("ognissanti", LANG) is None
    got = extract_timespan("ognissanti", LANG, anchor=__import__("datetime").datetime(2026, 8, 14, 10, 0))
    assert got is not None
    span, remainder = got
    assert (span.start.month, span.start.day) == (11, 1)


# Known gap, reported rather than hacked around: "it" has no marker_on.voc
# (the "el"/"the"-on-a-day-of-month connector "es"/"pt" carry); "il" is
# already claimed as a plain article (marker_article.voc) and is NOT safe
# to overload as a general "on" connector without touching grammar/matcher
# code, which is out of scope here. So the "adverb + il + day-number" shape
# claims FREQ but cannot fold the day -- unlike "ogni mese il 15" above,
# which resolves the day through a different (already-working) finder path.
def test_known_gap_mensilmente_il_n_does_not_fold_day():
    got = extract_recurrence("mensilmente il 15", LANG)
    assert got is not None
    assert got[0].to_string() == "FREQ=MONTHLY"
    assert got[1] == "il 15"
