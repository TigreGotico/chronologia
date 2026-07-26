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

from chronologia.extract.model import Token
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


# -- ordinal TEEN fold (11..19), a two-word run -------------------------------
# The Semitic ordinal teens are written as two words -- an inflected unit
# ordinal followed by the teen word عشر / עשר ("الخامس عشر" the-fifteenth,
# "החמישה עשר").  The unit word carries the definite article, so it is NOT in
# the curated *cardinal* set (خمسة/חמישה are; الخامس/החמישה are not), and the
# single-token ordinal pre-pass (``with_ordinals``) cannot see a two-word run.
# The result was that the leading ordinal folded to its UNIT value (الخامس -> 5)
# while the teen word عشر folded to 10 on its own, and the date bound the unit
# (April 5 / April 10) -- a silent wrong answer.
#
# ovos-number-parser already reads the *joined* two-word run correctly
# (``extract_number_<lang>("الخامس عشر", ordinals=True) == 15``), so this
# pre-pass -- run BEFORE ``with_ordinals`` and the cardinal fold -- detects the
# [unit-ordinal][teen-word] pair and folds it to that value.  Gated on an
# explicit first-word set so nothing but a genuine ordinal teen can fire, and
# the month-name ordinals الأول/الثاني are untouched (they are the teen fold's
# concern only when عشر follows, which the Levantine month names never do).
_AR_TEEN_SECOND = frozenset({"عشر", "عشرة"})
_AR_TEEN_FIRST = frozenset({
    # masculine, with the definite article (the attested date surface)
    "الحادي", "الثاني", "الثالث", "الرابع", "الخامس", "السادس", "السابع",
    "الثامن", "التاسع",
    # feminine, with the definite article ("الخامسة عشرة")
    "الحادية", "الثانية", "الثالثة", "الرابعة", "الخامسة", "السادسة",
    "السابعة", "الثامنة", "التاسعة",
    # article-less variants
    "حادي", "ثاني", "ثالث", "رابع", "خامس", "سادس", "سابع", "ثامن", "تاسع",
})
_HE_TEEN_SECOND = frozenset({"עשר", "עשרה"})
_HE_TEEN_FIRST = frozenset({
    # definite (ה-prefixed) unit words -- the stranded surface
    "האחד", "השניים", "השנים", "השלושה", "הארבעה", "החמישה", "השישה",
    "השבעה", "השמונה", "התשעה",
    # feminine definite ("החמש עשרה")
    "האחת", "השלוש", "הארבע", "החמש", "השש", "השבע", "השמונה", "התשע",
})


def _teen_fold(extract_fn, first_words, second_words):
    """Fold a [unit-ordinal][teen-word] pair to its 11..19 value."""
    def rewrite(tokens):
        out, i, n, changed = [], 0, len(tokens), False
        while i < n:
            t = tokens[i]
            if (not t.is_number and t.text in first_words and i + 1 < n
                    and tokens[i + 1].text in second_words):
                try:
                    v = extract_fn(t.text + " " + tokens[i + 1].text,
                                   ordinals=True)
                except Exception:
                    v = False
                if v is not False and v is not None and 11 <= v <= 19:
                    out.append(Token(text=str(int(v)), raw=str(int(v)),
                                     index=t.index, is_number=True,
                                     value=int(v), char_start=t.char_start,
                                     char_end=tokens[i + 1].char_end))
                    i, changed = i + 2, True
                    continue
            out.append(t)
            i += 1
        return reindex(tuple(out)) if changed else tokens
    return rewrite


_ar_teen_fold = _teen_fold(extract_number_ar, _AR_TEEN_FIRST, _AR_TEEN_SECOND)
_he_teen_fold = _teen_fold(extract_number_he, _HE_TEEN_FIRST, _HE_TEEN_SECOND)


# Arabic ordinals carry the definite article ال ("الثالث" the-third), which is
# exactly the surface the quarter phrase "الربع الثالث" attests; the model's
# ``pronounce_ordinal_ar`` emits that article-prefixed form.  الأول (first) and
# الثاني (second) are withheld: they are the ordinal component of the Levantine
# month names (تشرين الأول = October, كانون الثاني = January), so folding them
# would erase the month.  Consequently a *spelled* Arabic Q1/Q2 does not fold
# (Q3/Q4 and the digit/Latin-Q forms do) -- a documented, narrow limitation.
_fold_ar_base = with_ordinals(_make_fold(extract_number_ar, _AR_NUM), "ar",
                              exclude=("الأول", "الثاني"))

# Rule A, confirmed by native speaker athmanemokraoui (TigreGotico/chronologia
# #268): الأول (first) / الثاني (second) ARE the ordinal in every position
# EXCEPT immediately after a Levantine solar month-name prefix
# (تشرين الأول = October, كانون الثاني = January, جمادى الأولى, ربيع الأول),
# where they form the month name.  They are withheld from the base fold above
# (which is global and cannot see the preceding word) and licensed back to the
# ordinal here in every non-month position, so "النصف الأول من 2020" (first
# half) and "الربع الأول" (first quarter) read while تشرين الأول stays October.
_AR_MONTH_ORD_PREFIX = frozenset({"تشرين", "كانون", "جمادى", "ربيع"})
_AR_MONTH_ORDINAL = {"الأول": 1, "الأولى": 1, "الثاني": 2, "الثانية": 2}


def _ar_month_ordinal_license(tokens):
    out = list(tokens)
    for i, t in enumerate(out):
        if t.is_number or t.text not in _AR_MONTH_ORDINAL:
            continue
        prev = out[i - 1] if i > 0 else None
        if prev is not None and prev.text in _AR_MONTH_ORD_PREFIX:
            continue  # part of a month name -- leave the surface untouched
        v = _AR_MONTH_ORDINAL[t.text]
        out[i] = Token(text=str(v), raw=str(v), index=t.index, is_number=True,
                       value=v, char_start=t.char_start, char_end=t.char_end)
    return tuple(out)


def fold_ar(tokens):
    """Fold the ordinal teen (11..19) first, then the cardinal/ordinal fold,
    then license الأول/الثاني positionally (Rule A, #268)."""
    return _ar_month_ordinal_license(_fold_ar_base(_ar_teen_fold(tokens)))


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


# -- feminine ordinals 1/2 that agree with the "half" noun מחצית ---------------
# Hebrew names its weekdays by the MASCULINE ordinal (יום ראשון = Sunday, יום
# שני = Monday), which is exactly why the cardinal fold withholds those forms.
# The half noun מחצית is FEMININE, so "the first/second half" takes the FEMININE
# ordinal -- ראשונה / שנייה -- which is NOT a weekday name and collides with
# nothing, so it folds safely to the digit the half_period ``NUM`` slot binds.
# Both spellings of "second" (שנייה full plene / שניה) and the definite ה- form
# the attested surface uses ("המחצית הראשונה") are listed.  Only 1 and 2: a half
# admits no ordinal past the second.  Even-Shoshan, מילון אבן-שושן, and the
# Academy of the Hebrew Language: ראשונה / שנייה — שם מספר סודר, נקבה.
_HE_ORD_FEM = {
    "ראשונה": 1, "הראשונה": 1,
    "שנייה": 2, "השנייה": 2, "שניה": 2, "השניה": 2,
}


def _he_ordinal_rewrite(tokens):
    out, changed = [], False
    for t in tokens:
        if not t.is_number and t.text in _HE_ORD_FEM:
            v = _HE_ORD_FEM[t.text]
            out.append(Token(text=str(v), raw=str(v), index=t.index,
                             is_number=True, value=v,
                             char_start=t.char_start, char_end=t.char_end))
            changed = True
        else:
            out.append(t)
    return reindex(tuple(out)) if changed else tokens


_fold_he_cardinal = fold_he


def fold_he(tokens):  # noqa: F811  -- wrap the cardinal fold with the fem ordinal
    """Fold the ordinal teen (11..19) and the feminine ordinal (מחצית's
    "first/second") before the cardinal fold, then run the cardinal fold: none
    overlap (each is its own run), and the weekday-masculine ordinals stay
    untouched."""
    return _fold_he_cardinal(_he_ordinal_rewrite(_he_teen_fold(tokens)))
