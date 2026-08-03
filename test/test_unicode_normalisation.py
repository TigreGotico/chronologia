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


def test_turkish_dotted_capital_i_preserves_offsets():
    # Turkish capital İ (U+0130) lower-cases to i + COMBINING DOT ABOVE (two
    # codepoints), which broke the tokenizer's length-preserving invariant and
    # shifted every remainder char after it. Folding İ->i keeps offsets aligned.
    from chronologia.extract.tokenizer import normalise_unicode
    text = "İzmir 5 Haziran 2020 günü"
    assert len(normalise_unicode(text)) == len(text)
    r = extract_timespan(text, "tr", datetime(2017, 6, 27, 13, 4))
    assert r is not None
    assert (r.span.start.year, r.span.start.month, r.span.start.day) \
        == (2020, 6, 5)
    # the remainder is sliced correctly from the original text (the 'g' survives)
    assert r.remainder == "İzmir günü"


# --------------------------------------------------------------------------
# Locale-aware number grouping / decimal separator (r50b).
#
# The SAME two characters ',' and '.' mean OPPOSITE things per locale: in
# English (and he/ms) '.' is the decimal point and ',' groups thousands, so
# "12,000" == 12000 and "1,234.5" == 1234.5; in Continental-European locales
# (de/es/it/fr/pt/...) it is the reverse, so "1.500" == 1500 and "1.234,5" ==
# 1234.5.  The number tokenizer used to be language-neutral and split the
# grouped surface, binding a confident-but-wrong fragment (an English
# "12,000 days" resolved to 0, a German "1,5 Stunden" to 5h).  These pin the
# per-locale reading and that dotted dates / ordinals are not confused for it.
from datetime import timedelta

from chronologia import extract_duration


def _dur(text, lang):
    r = extract_duration(text, lang)
    return r.duration if r is not None else None


@pytest.mark.parametrize("text,expected", [
    ("in 12,000 days", timedelta(days=12000)),   # comma = thousands
    ("1,500 days", timedelta(days=1500)),
    ("1,234.5 days", timedelta(days=1234, hours=12)),
    ("1.5 hours", timedelta(hours=1, minutes=30)),  # dot = decimal
    ("2.5 hours", timedelta(hours=2, minutes=30)),
])
def test_en_dot_decimal_comma_thousands(text, expected):
    assert _dur(text, "en-us") == expected


@pytest.mark.parametrize("text,expected", [
    ("1,5 Stunden", timedelta(hours=1, minutes=30)),   # comma = decimal
    ("2,5 Stunden", timedelta(hours=2, minutes=30)),
    ("1.500 Stunden", timedelta(hours=1500)),          # dot = thousands
    ("1.234,5 Stunden", timedelta(hours=1234, minutes=30)),
])
def test_de_comma_decimal_dot_thousands(text, expected):
    assert _dur(text, "de") == expected


@pytest.mark.parametrize("text,expected", [
    ("1,5 horas", timedelta(hours=1, minutes=30)),   # comma = decimal
    ("1.500 dias", timedelta(days=1500)),            # dot = thousands
    ("mil dias", timedelta(days=1000)),              # spelled word, unaffected
])
def test_es_comma_decimal_dot_thousands(text, expected):
    assert _dur(text, "es") == expected


def test_de_dotted_date_not_confused_with_thousands():
    # "15.06.2020" is a German civil date, NOT a thousands-grouped number,
    # while "1.500" in the same locale IS 1500 -- the dotted-date literal and
    # the number rule must stay mutually exclusive.
    got = _span("15.06.2020", "de")
    assert got is not None and (got[0].year, got[0].month, got[0].day) == (2020, 6, 15)


def test_de_trailing_dot_ordinal_still_reads():
    # "5. Juni 2020" -- the trailing-dot ordinal must not be read as an
    # incomplete decimal.
    got = _span("5. Juni 2020", "de")
    assert got is not None and (got[0].month, got[0].day) == (6, 5)
