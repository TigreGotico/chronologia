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

from chronologia.extract.numfold_engine import NumberGrammar, make_fold


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
fold_he = _make_fold(extract_number_he, _HE_NUM)
