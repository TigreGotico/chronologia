# -*- coding: utf-8 -*-
"""Semitic (Arabic / Hebrew) spelled-number fold hooks.

Two RTL languages whose calendars already worked but whose relative /
weekday / clock surfaces did not.  Fixed multi-word slot surfaces (Arabic
"بعد غد" day-after-tomorrow, Hebrew "יום ראשון" Sunday, "نهاية الأسبوع" /
"סוף שבוע" weekend, "منتصف الليل" midnight) are folded back to a single token
by the shared ``pipeline.merge_multiword`` pass, so the ``*.voc`` files list
those surfaces *with their space* and no glue is needed here.

This hook owns only **spelled cardinals** ("قبل خمسة أيام",
"לפני חמישה ימים"): a maximal run of a curated closed set of number-words is
folded to one digit ``NUM`` token via ``ovos_number_parser``'s
``extract_number_<lang>``.  The set is curated (not the parser's full
vocabulary) so unit-duals and weekday homographs -- which the number
back-end would also read as numbers -- stay their own token.

A pure ``tuple[Token] -> tuple[Token]`` transform, re-indexed so
``Token.index`` stays contiguous, wired as the language ``hook``.
"""
from __future__ import annotations

from ovos_number_parser.numbers_ar import extract_number_ar
from ovos_number_parser.numbers_he import extract_number_he

from chronologia.extract.numfold_engine import NumberGrammar, make_fold, reindex


def _make_fold(extract_fn, numwords):
    """A curated-set cardinal fold with the Arabic/Hebrew "و" (and) as the
    internal run connector ("خمسة وعشرون")."""
    numset = frozenset(numwords)
    return make_fold(NumberGrammar(
        is_number=lambda tok: tok.is_number or tok.text in numset,
        extract=extract_fn,
        joiner=lambda tok: tok.text == "و"))


# -- Arabic ------------------------------------------------------------------
# curated cardinal surfaces (no article).  "اثنين/اثنان" are withheld -- they
# double as the bare weekday name for Monday; two is spelled as the dual noun
# (يومين) in real offsets, so nothing is lost.
_AR_NUM = frozenset({
    "واحد", "وحدة", "أحد", "إحدى", "احد",
    "ثلاثة", "ثلاث", "ثلاثه", "أربعة", "أربع", "اربعة", "اربع",
    "خمسة", "خمس", "خمسه", "ستة", "ست", "سته",
    "سبعة", "سبع", "سبعه", "ثمانية", "ثماني", "ثمانيه",
    "تسعة", "تسع", "تسعه", "عشرة", "عشر", "عشره",
    "عشرون", "عشرين", "ثلاثون", "ثلاثين", "أربعون", "أربعين",
    "خمسون", "خمسين", "ستون", "ستين", "سبعون", "سبعين",
    "ثمانون", "ثمانين", "تسعون", "تسعين",
    "مئة", "مائة", "مئتان", "مئتين",
})
from chronologia.extract.numfold_ordinals import with_ordinals

# Arabic ordinals carry the definite article ال ("الثالث" the-third), which is
# exactly the surface the quarter phrase "الربع الثالث" attests; the model's
# ``pronounce_ordinal_ar`` emits that article-prefixed form.  الأول (first) and
# الثاني (second) are withheld: they are the ordinal component of the Levantine
# month names (تشرين الأول = October, كانون الثاني = January), so folding them
# would erase the month.  Consequently a *spelled* Arabic Q1/Q2 does not fold
# (Q3/Q4 and the digit/Latin-Q forms do) -- a documented, narrow limitation.
fold_ar = with_ordinals(_make_fold(extract_number_ar, _AR_NUM), "ar",
                        exclude=("الأول", "الثاني"))


# -- Hebrew ------------------------------------------------------------------
# curated cardinal surfaces (masc + fem, no prefix).  Dual unit nouns
# (שבועיים/יומיים ...) are withheld -- they carry their own unit meaning.
_HE_NUM = frozenset({
    "אחד", "אחת", "שתי", "שני", "שניים", "שתיים",
    "שלוש", "שלושה", "ארבע", "ארבעה", "חמש", "חמישה",
    "שש", "שישה", "שבע", "שבעה", "שמונה", "תשע", "תשעה",
    "עשר", "עשרה", "עשרים", "שלושים", "ארבעים", "חמישים",
    "שישים", "שבעים", "שמונים", "תשעים", "מאה", "מאתיים",
})
# Hebrew ordinals are NOT folded: the ordinal surfaces שני / שלישי / רביעי /
# חמישי / שישי (2..6) are exactly the weekday names (Monday..Friday, from
# יום שני ...), and ראשון (1) is Sunday.  Folding any of them to a digit would
# destroy bare-weekday, recurrence and offset parsing.  Hebrew's spelled
# ordinal quarter ("רבעון שלישי") therefore stays a documented xfail -- the
# collision is total, so it cannot fold at the token level.
_fold_he_run = _make_fold(extract_number_he, _HE_NUM)

# The one cardinal that is also a weekday name.  שני is the construct form of
# שניים "two" *and* the ordinal "second", and Hebrew names its weekdays by
# ordinal -- יום שני is literally "second day", Monday (Hebrew Wikipedia,
# "שבוע": the day names follow their ordinal number as in Genesis 1, only the
# seventh keeping the name שבת).  Reading it as the digit 2 is what silently
# turned "כל יום שני" (every Monday) into a confident FREQ=DAILY.
_HE_SHENI = "שני"
# The day noun the weekday name is built on, in the surfaces the weekday
# vocabulary lists (bare and with the ב- "on" prefix).
_HE_DAY_NOUN = frozenset({"יום", "ביום"})


def _he_counts_a_noun(tokens, i):
    """Whether ``שני`` at index ``i`` can be the cardinal "two" here.

    A cardinal in the **construct state** binds the noun it counts and cannot
    stand without it: "שני ימים" is two days, but nothing counts two in
    "כל שני" -- there the word is the ordinal, i.e. Monday.  So the cardinal
    reading needs a following word, and it must not be the ordinal's own day
    noun ("יום שני"), where the weekday reading is the only one available.
    """
    if i and tokens[i - 1].text in _HE_DAY_NOUN:
        return False
    return i + 1 < len(tokens) and not tokens[i + 1].is_number


def fold_he(tokens):
    """The Hebrew cardinal fold, holding ``שני`` back where it names Monday.

    The shared run scanner decides membership one token at a time, which is
    all every other language needs; the שני homograph is settled by the words
    around it instead.  The stream is therefore split at each weekday שני and
    the scanner run over the remaining segments, so a real count ("לפני שני
    ימים", two days ago) still folds while the weekday survives to be glued
    onto its day noun by the multiword pass.
    """
    out = []
    segment = []
    for i, tok in enumerate(tokens):
        if tok.text == _HE_SHENI and not _he_counts_a_noun(tokens, i):
            out.extend(_fold_he_run(tuple(segment)))
            out.append(tok)
            segment = []
        else:
            segment.append(tok)
    out.extend(_fold_he_run(tuple(segment)))
    return reindex(tuple(out))
