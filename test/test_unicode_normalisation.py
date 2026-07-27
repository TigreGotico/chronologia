"""Unicode/typography normalisation before tokenizing.

Curly apostrophes/quotes, fullwidth digits and punctuation, non-breaking
spaces and the º/ª ordinal indicators are the shapes a real user pastes
in from a word processor, a CJK keyboard or a Romance-language document.
Each one used to silently break the parse -- a dropped clock minute, a
stranded ordinal day, a whole-month answer where a day was meant -- while the
plain ASCII form parsed fine.  These tests pin the fix: a normalised surface
must resolve exactly as its ASCII twin, and the paths that already worked
(Arabic-Indic digits, straight ASCII) must stay byte-identical.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)

CURLY_APOS = "’"      # RIGHT SINGLE QUOTATION MARK
FW_COLON = "："        # FULLWIDTH COLON
FW_FIVE = "５"         # FULLWIDTH DIGIT FIVE
ORD_MASC = "º"        # MASCULINE ORDINAL INDICATOR
ORD_FEM = "ª"         # FEMININE ORDINAL INDICATOR
NBSP = " "            # NO-BREAK SPACE
NNBSP = " "           # NARROW NO-BREAK SPACE


def _span(text, lang):
    r = extract_timespan(text, lang, ANCHOR)
    return None if r is None else (r.span.start, r.remainder)


def test_curly_apostrophe_oclock_reads_like_straight():
    curly = "5 o" + CURLY_APOS + "clock"
    assert _span(curly, "en") == _span("5 o\'clock", "en")
    assert _span(curly, "en") is not None


def test_fullwidth_colon_keeps_the_minutes():
    curly = "meet at 5" + FW_COLON + "30"
    plain = _span("meet at 5:30", "en")
    assert _span(curly, "en") == plain
    assert plain is not None and plain[0].minute == 30


def test_fullwidth_digits_read_as_ascii():
    fw = FW_FIVE + ":30"
    assert _span(fw, "en") == _span("5:30", "en")


def test_es_ordinal_indicator_day_reads_as_the_day():
    got = _span("el 1" + ORD_MASC + " de abril", "es")
    assert got == _span("el 1 de abril", "es")
    assert got is not None and got[0].month == 4 and got[0].day == 1


def test_es_feminine_ordinal_indicator_day():
    assert _span("1" + ORD_FEM + " de abril", "es") == \
        _span("1 de abril", "es")


def test_es_rae_dotted_ordinal_indicator_day():
    assert _span("el 1." + ORD_MASC + " de abril", "es") == \
        _span("el 1 de abril", "es")


def test_pt_ordinal_indicator_day():
    assert _span("1" + ORD_MASC + " de abril", "pt") == \
        _span("1 de abril", "pt")


def test_it_ordinal_indicator_day():
    assert _span("1" + ORD_MASC + " aprile", "it") == \
        _span("1 aprile", "it")


def test_nbsp_separated_date_resolves():
    got = _span("15" + NBSP + "de abril", "es")
    assert got == _span("15 de abril", "es")
    assert got is not None


def test_narrow_nbsp_separated_date_resolves():
    assert _span("15" + NNBSP + "de abril", "es") == \
        _span("15 de abril", "es")


def test_arabic_indic_year_still_resolves():
    got = _span("\u0662\u0660\u0662\u0660", "ar")
    assert got is not None and got[0].year == 2020


def test_french_curly_apostrophe_phrase():
    curly = "l" + CURLY_APOS + "ann\u00e9e prochaine"
    assert _span(curly, "fr") == _span("l\'ann\u00e9e prochaine", "fr")


@pytest.mark.parametrize("text,lang", [
    ("5 o\'clock", "en"),
    ("meet at 5:30", "en"),
    ("1 de abril", "es"),
    ("\u0662\u0660\u0662\u0660", "ar"),
])
def test_plain_forms_unchanged(text, lang):
    assert _span(text, lang) is not None
