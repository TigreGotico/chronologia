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

from pathlib import Path

from ovos_number_parser.numbers_ar import extract_number_ar
from ovos_number_parser.numbers_he import extract_number_he
from ovos_spec_tools import read_resource_file

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
# Arabic writes the conjunction و ("and") GLUED onto the word it precedes, with
# no space -- "خمسة وعشرون" (twenty-five) tokenises as [خمسة][وعشرون], not
# [خمسة][و][عشرون].  The bare-"و" run connector above therefore never fires on
# real Arabic text, so a spelled compound 21-99 (and hundred+tens, "مئة وخمسة
# وعشرون") stalled after its first word and the rest was stranded -- a flat
# None for the whole utterance.  ovos_number_parser reads the glued run
# correctly (extract_number_ar("خمسة وعشرون") == 25, "مئة وخمسة وعشرون" == 125),
# so admit every و-glued cardinal surface to the run set as well.
_AR_NUM_WAW = frozenset("و" + w for w in _AR_NUM)
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
_fold_ar_base = with_ordinals(
    _make_fold(extract_number_ar, _AR_NUM | _AR_NUM_WAW), "ar",
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


# -- feminine ordinal CLOCK hour fold ----------------------------------------
# Arabic tells clock hours with the FEMININE ordinal -- الثامنة ("the eighth
# [hour]") is eight o'clock, not the cardinal ثمانية.  These forms carry the
# definite article and are never in the curated cardinal set, so the base fold
# left them stranded and a spelled clock time ("الساعة الثامنة صباحا",
# "الثامنة مساء") did not parse at all.  In an unambiguous CLOCK context --
# immediately after the o'clock word الساعة, or immediately before an am/pm
# daypart particle -- fold the feminine ordinal hour الواحدة..الثانية عشرة
# (1..12) to a CLOCK "H:00" token.  The meridiem-optional clock orders then
# resolve it, and the shared daypart->meridiem shift turns it into the 24-hour
# reading (الثامنة مساء -> 20:00).  Gated on the clock context so every
# non-clock use -- the #268/#279 date ordinals الأول/الثاني, spelled cardinals,
# quarters -- stays byte-identical.
_AR_CLOCK_AT = frozenset({"الساعة", "الساعه"})
_AR_CLOCK_MERIDIEM = frozenset({
    "صباحا", "صباحاً", "الصباح", "فجرا", "فجراً",
    "مساء", "مساءً", "المساء", "ظهرا", "ظهراً",
    "عصرا", "عصراً", "ليلا", "ليلاً",
})
_AR_FEM_HOUR = {
    "الواحدة": 1, "الثانية": 2, "الثالثة": 3, "الرابعة": 4, "الخامسة": 5,
    "السادسة": 6, "السابعة": 7, "الثامنة": 8, "التاسعة": 9, "العاشرة": 10,
}
# the two-word teen hours -- [feminine unit ordinal][عشرة]: الحادية عشرة (11),
# الثانية عشرة (12).  المصرية reckoning never spells past twelve o'clock.
_AR_FEM_HOUR_TEEN = {"الحادية": 11, "الثانية": 12}


def _ar_clock_token(hour, first, last):
    text = "%d:00" % hour
    return Token(text=text, raw=text, index=first.index,
                 char_start=first.char_start, char_end=last.char_end)


def _ar_clock_hour_fold(tokens):
    """Fold a feminine ordinal hour (1..12) to a CLOCK ``H:00`` token when it
    stands in an unambiguous clock context (after الساعة, or before a daypart
    meridiem particle)."""
    out, i, n, changed = [], 0, len(tokens), False
    while i < n:
        t = tokens[i]
        prev_at = i > 0 and tokens[i - 1].text in _AR_CLOCK_AT
        # two-word teen hour: الحادية عشرة (11) / الثانية عشرة (12)
        if (not t.is_number and t.text in _AR_FEM_HOUR_TEEN and i + 1 < n
                and tokens[i + 1].text == "عشرة"):
            after = tokens[i + 2] if i + 2 < n else None
            if prev_at or (after is not None
                           and after.text in _AR_CLOCK_MERIDIEM):
                out.append(_ar_clock_token(_AR_FEM_HOUR_TEEN[t.text],
                                           t, tokens[i + 1]))
                i, changed = i + 2, True
                continue
        # single-word hour الواحدة..العاشرة
        if not t.is_number and t.text in _AR_FEM_HOUR:
            after = tokens[i + 1] if i + 1 < n else None
            if prev_at or (after is not None
                           and after.text in _AR_CLOCK_MERIDIEM):
                out.append(_ar_clock_token(_AR_FEM_HOUR[t.text], t, t))
                i, changed = i + 1, True
                continue
        out.append(t)
        i += 1
    return reindex(tuple(out)) if changed else tokens


import re as _re

_CLOCK_TEXT = _re.compile(r"\d{1,2}:\d{2}(?::\d{2})?$")
# The clock-fraction surfaces (matching clock_fraction_{30,15}.voc), bare of the
# article and of the "و" (and) proclitic.  Arabic writes that connective GLUED
# onto the fraction it precedes, so "الساعة الثالثة والنصف" tokenises as
# [CLOCK][والنصف] -- one fused token that is neither a CLOCKDIR nor a FRACTION,
# which stranded the fraction and returned the bare hour.  The subtractive
# "إلا" (to) is written with a space and needs no split.
_AR_CLOCK_FRACTION = frozenset({"النصف", "نصف", "الربع", "ربع"})


def _ar_clock_fraction_split(tokens):
    """Split a "و"-glued clock fraction ("والنصف" -> "و" + "النصف") when it
    directly follows a folded CLOCK ``H:MM`` token, so the past-direction
    connective surfaces as its own CLOCKDIR token and the fraction as FRACTION.
    Gated on the preceding CLOCK so nothing but a spoken clock fraction fires,
    keeping every و-glued cardinal ("وعشرون") untouched."""
    out, changed = [], False
    for t in tokens:
        if (not t.is_number and len(t.text) > 1 and t.text[0] == "و"
                and t.text[1:] in _AR_CLOCK_FRACTION and out
                and _CLOCK_TEXT.match(out[-1].text)):
            waw = Token(text="و", raw="و", index=t.index,
                        char_start=t.char_start, char_end=t.char_start + 1)
            frac = Token(text=t.text[1:], raw=t.text[1:], index=t.index,
                         char_start=t.char_start + 1, char_end=t.char_end)
            out.append(waw)
            out.append(frac)
            changed = True
        else:
            out.append(t)
    return reindex(tuple(out)) if changed else tokens


#: locale-directory roots this module's hooks read vocabulary from, same
#: layout ``loader.LOCALE_DIR`` resolves (``chronologia/locale``).
_DEFAULT_LOCALE_DIR = str(Path(__file__).parent.parent / "locale")

#: vocab-filename globs that name a single closed-class TEMPORAL slot whose
#: bare word may legitimately follow a fused waw as a range endpoint --
#: months (Gregorian and Islamic-civil), weekdays and dayparts.  The
#: ABBREVIATED weekday file (``weekday_abbr_6.voc``: "أحد"/"احد", bare
#: Sunday with no article) is deliberately excluded: it is spelled
#: identically to the bare stem inside the numeral "واحد" (one), so folding
#: it in would mis-split "واحد وعشرين يوما" (21 days) into "و" + "احد" and
#: silently drop a day.  ``weekday_[0-9].voc`` (the article-bearing full
#: form, "الأحد") carries no such collision.  Multiword entries within these
#: files (``"ربيع الأول"``, ``"يوم الإثنين"``) are filtered out below:
#: splitting only the leading proclitic off a MULTIWORD surface would leave a
#: dangling remainder the multiword-merge pass was never asked to re-glue, so
#: those surfaces are deliberately left unclosed by this hook (tracked
#: separately).
_AR_WORD_ROLE_GLOBS = ("month_*.voc", "weekday_[0-9].voc", "daypart_*.voc")


def _ar_temporal_words(locale_dir=_DEFAULT_LOCALE_DIR):
    lang_dir = Path(locale_dir) / "ar"
    words = set()
    for pattern in _AR_WORD_ROLE_GLOBS:
        for path in sorted(lang_dir.glob(pattern)):
            for surface in read_resource_file(path):
                if " " not in surface:
                    words.add(surface)
    return frozenset(words)


# Single-word month/weekday/daypart surfaces, used to recognise a "و"-glued
# temporal word as a range endpoint -- see split_ar_range_word.
_AR_TEMPORAL_WORDS = _ar_temporal_words()


def split_ar_range_word(tokens):
    """Split a "و"-glued temporal word off its proclitic ("بين يناير ومارس" ->
    [بين][يناير][و][مارس]).  Arabic writes the "and" conjunction fused onto
    the word it precedes with no space, so the second endpoint of a range
    ("بين X وY", "من X وY") is otherwise invisible to the range grammar and
    the span silently truncates to the first endpoint alone.  Gated on the
    remainder being a recognised single-word month/weekday/daypart surface
    (see ``_AR_TEMPORAL_WORDS``), so words that merely happen to start with و
    ("وسط" mid, "واحد" one, "والنصف" and-the-half, ...) are left untouched.
    Wired as ``pre_hook`` -- range/connector detection reads the raw pretoken
    stream, before the ``hook`` number fold ever runs."""
    out, changed = [], False
    for t in tokens:
        if (not t.is_number and len(t.raw) > 1 and len(t.text) == len(t.raw)
                and t.raw[0] == "و" and t.text[1:] in _AR_TEMPORAL_WORDS):
            waw = Token(text="و", raw=t.raw[0], index=t.index,
                        char_start=t.char_start, char_end=t.char_start + 1)
            rest = Token(text=t.text[1:], raw=t.raw[1:], index=t.index,
                         char_start=t.char_start + 1, char_end=t.char_end)
            out.append(waw)
            out.append(rest)
            changed = True
        else:
            out.append(t)
    return reindex(tuple(out)) if changed else tokens


#: vocab-filename globs that name a single closed-class TEMPORAL slot whose
#: bare word may legitimately follow a fused vav as a range endpoint --
#: Gregorian and Hebrew-calendar months, and dayparts.  ``weekday_[0-9].voc``
#: is EXCLUDED, unlike the Arabic version of this guard: every Hebrew weekday
#: full name Mon..Fri is multiword ("יום שני") and so is already filtered out
#: by the single-word check below. ``weekday_abbr_*.voc`` (the bare
#: abbreviated forms, e.g. "שני" Monday, "שלישי" Tuesday, ...) is EXCLUDED
#: outright rather than relying on the single-word filter, and for two
#: DIFFERENT reasons per entry, not one shared one: "שני" is specifically the
#: SAME string as the construct form of the cardinal "two" (שניים), a
#: homograph documented on ``_HE_NUM``/``fold_he`` above -- folding it in
#: would let "יום ושני שעות" (a day and two hours) mis-split into "ו" +
#: "שני" and risk a duration count being read as a Monday range endpoint,
#: the same class of defect the Arabic guard's abbreviated-Sunday exclusion
#: documents ("أحد" inside "واحد"). The other bare abbreviated weekdays
#: (שלישי/רביעי/חמישי/שישי/ראשון) carry a broader, ordinary ORDINAL
#: homograph instead -- Hebrew names weekdays by ordinal, so e.g. "שלישי" is
#: simultaneously "third" and "Tuesday" with no dedicated cardinal collision;
#: excluding the whole file keeps that one guard simple rather than needing
#: a second, narrower rationale per entry. ``weekday_abbr_5.voc`` never
#: reaches either check regardless: its only surfaces ("יום ש"/"ביום ש")
#: are multiword, so the single-word filter below would have dropped it
#: anyway. ``weekday_5.voc`` ("שבת", bare Saturday) has no such collision
#: and is covered through the single-word filter same as any other role.
#: Multiword entries (weekday full names, "אדר ב"/"אדר שני"/"אדר בית" for
#: the Hebrew leap month) are filtered out below: splitting only the
#: leading vav off a MULTIWORD surface would leave a dangling remainder the
#: multiword-merge pass was never asked to re-glue, so those surfaces are
#: deliberately left unclosed by this hook (tracked separately).
_HE_WORD_ROLE_GLOBS = ("month_*.voc", "weekday_5.voc", "daypart_*.voc")

#: ``month_hebrew_5.voc`` ("אב", the Hebrew month Av) is excluded outright,
#: from BOTH the range-endpoint split and the bare-mention remerge below --
#: not merely narrowed the way the abbreviated weekdays are. "אב" is not a
#: rare technical homograph: it is also the ordinary, extremely common noun
#: "father" ("אמא ואב", "mother and father"), and admitting it let a fused
#: bare mention resolve as a confident ``basis='exact'`` month span for text
#: that is not talking about a date at all (found on adversarial review --
#: "אם ואב"/"אבא ואב" mis-resolved to Av). Gregorian months and the other
#: Hebrew-calendar months carry no such everyday-word collision. The
#: trade-off, stated not hidden: a range whose second endpoint is a FUSED
#: "ואב" ("בין ניסן ואב") still truncates, the original defect, left open for
#: this one month rather than risk the false positive; the spaced form
#: ("בין ניסן ו אב") is unaffected and already works.
_HE_VAV_HOMOGRAPH_EXCLUDE = frozenset({"אב"})


def _he_temporal_words(locale_dir=_DEFAULT_LOCALE_DIR):
    lang_dir = Path(locale_dir) / "he"
    words = set()
    for pattern in _HE_WORD_ROLE_GLOBS:
        for path in sorted(lang_dir.glob(pattern)):
            for surface in read_resource_file(path):
                if " " not in surface:
                    words.add(surface)
    return frozenset(words) - _HE_VAV_HOMOGRAPH_EXCLUDE


# Single-word month/weekday/daypart surfaces, used to recognise a
# vav-glued temporal word as a range endpoint -- see split_he_range_word.
_HE_TEMPORAL_WORDS = _he_temporal_words()


def split_he_range_word(tokens):
    """Split a vav-glued temporal word off its proclitic ("בין ינואר ומרץ" ->
    [בין][ינואר][ו][מרץ]).  Hebrew writes the "and" conjunction fused onto the
    word it precedes with no space, so the second endpoint of a range
    ("בין X וY") is otherwise invisible to the range grammar and the span
    silently truncates to the first endpoint alone.  Gated on the remainder
    being a recognised single-word month/weekday/daypart surface (see
    ``_HE_TEMPORAL_WORDS``), so words that merely happen to start with ו
    ("ורוד" pink, "ותיק" veteran, ...) are left untouched.  Wired as
    ``pre_hook`` -- range/connector detection reads the raw pretoken stream,
    before the ``hook`` number fold (``fold_he``, which already strips a
    vav proclitic off a wider curated word set, ``_he_vav_strip``) ever
    runs."""
    out, changed = [], False
    for t in tokens:
        if (not t.is_number and len(t.text) > 1 and t.text[0] == "ו"
                and t.text[1:] in _HE_TEMPORAL_WORDS):
            vav = Token(text="ו", raw=t.raw[0], index=t.index,
                        char_start=t.char_start, char_end=t.char_start + 1)
            rest = Token(text=t.text[1:], raw=t.raw[1:], index=t.index,
                         char_start=t.char_start + 1, char_end=t.char_end)
            out.append(vav)
            out.append(rest)
            changed = True
        else:
            out.append(t)
    return reindex(tuple(out)) if changed else tokens


def fold_ar(tokens):
    """Fold the feminine ordinal clock hour first (in clock context only), split
    a "و"-glued trailing clock fraction off it, then the ordinal teen (11..19),
    the cardinal/ordinal fold, then license الأول/الثاني positionally
    (Rule A, #268)."""
    return _ar_month_ordinal_license(
        _fold_ar_base(_ar_teen_fold(
            _ar_clock_fraction_split(_ar_clock_hour_fold(tokens)))))


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


# -- gematria year numerals ---------------------------------------------------
# Hebrew calendar years are traditionally written with letters (gematria):
# תשפ״ה = 785 (small count) means the year 5785.  The numeral is always set
# off typographically -- a gershayim ״ before the final letter, or a geresh ׳
# for the thousands / a lone letter -- and that mark is what makes the fold
# safe: an UNMARKED run of letters is ordinary Hebrew (a word, a weekday name
# like יום ראשון) and is left untouched, so weekday / ordinal handling cannot
# regress.  A marked numeral folds to its integer year (via the shared
# ``hebrew_numerals`` converter) so it flows through the SAME Hebrew-calendar
# year path the numeric form (5785) already uses.
from chronologia.hebrew_numerals import (gematria_value, hebrew_year_value,
                                          is_gematria_numeral)

# The gematria fold is scoped to a YEAR context: it fires only on a marked
# numeral that directly follows a Hebrew-calendar month name (bare or with the
# ב- "in" prefix) or a year word (שנת / בשנת ...), which is exactly where a
# Hebrew-calendar year stands.  This is what keeps the equally gershayim-marked
# ABBREVIATIONS -- the weekend סופ״ש, the era marker לפנה״ס -- from being read
# as numbers: they never follow a Hebrew month, so they are left untouched.
_HE_CAL_MONTH = frozenset({
    "אב", "אדר", "אייר", "אלול", "חשון", "טבת", "כסלו", "ניסן", "סיון",
    "שבט", "תמוז", "תשרי",
    # ב- ("in") prefixed forms
    "באב", "באדר", "באייר", "באלול", "בחשון", "בטבת", "בכסלו", "בניסן",
    "בסיון", "בשבט", "בתמוז", "בתשרי",
})
_HE_YEAR_WORD = frozenset({"שנת", "בשנת", "שנה", "השנה"})
_HE_YEAR_CONTEXT = _HE_CAL_MONTH | _HE_YEAR_WORD


def _he_gematria_rewrite(tokens):
    out, changed = [], False
    n = len(tokens)
    for i, t in enumerate(tokens):
        prev = tokens[i - 1] if i > 0 else None
        nxt = tokens[i + 1] if i + 1 < n else None
        v = None
        if (not t.is_number and is_gematria_numeral(t.text)):
            if prev is not None and prev.text in _HE_YEAR_CONTEXT:
                # a marked numeral AFTER a month/year word is the YEAR: the
                # implied +5000 "small count" applies (תשפ״ה -> 5785).
                try:
                    v = hebrew_year_value(t.text)
                except ValueError:
                    v = None
            elif nxt is not None and nxt.text in _HE_CAL_MONTH:
                # a marked numeral BEFORE a Hebrew month is the DAY-OF-MONTH
                # (day-month order: "כ״ה בכסלו" = 25 Kislev): the RAW gematria
                # value with NO implied thousands.  Fold ANY positive value and
                # let calendar_date validate the day, exactly as the numeric
                # spelling does -- an out-of-range day ("ל״ה" = 35) then resolves
                # to None just like numeric "35 בכסלו", instead of leaving the
                # numeral unfolded and letting the bare month resolve to a
                # confident whole-month span (a numeric-vs-gematria parity break).
                try:
                    dv = gematria_value(t.text)
                except ValueError:
                    dv = None
                if dv is not None and dv >= 1:
                    v = dv
        if v is not None:
            out.append(Token(text=str(v), raw=str(v), index=t.index,
                             is_number=True, value=v,
                             char_start=t.char_start, char_end=t.char_end))
            changed = True
            continue
        out.append(t)
    return reindex(tuple(out)) if changed else tokens


_fold_he_cardinal = fold_he


# -- vav-conjunction (ו) proclitic strip --------------------------------------
# Hebrew glues the one-letter conjunction ו ("and") directly onto the word it
# precedes, no space -- "ומחר" (and-tomorrow), "ופסח" (and-Passover). The
# bet-preposition ("in") already gets this treatment for months, but as
# CURATED DUPLICATE literal surfaces -- ``month_1.voc`` lists both "ינואר" and
# "בינואר" outright. That approach cannot reach the holiday surfaces, which
# are harvested from ``well_known.tab`` and tokenised at load time, or the
# multi-word ones ("חג הפסח"), so it is done here instead as a token-level
# strip: a token whose text starts with ו folds to its bare remainder when
# that remainder is one of a curated closed set of Hebrew date/holiday stems.
# Gating on a curated set (rather than "any known vocab surface", which this
# hook cannot see -- it runs on tokens only) is exactly what keeps a real
# ו-initial root word ("ותיק", "ורוד"...) untouched: the strip only ever fires
# on a word already attested here as the Hebrew name of a day, month or
# holiday.
_HE_VAV_STEMS = frozenset({
    # named days (named_day_*.voc)
    "מחר", "היום", "אתמול", "אמש", "מחרתיים", "מחרתים",
    # Gregorian months (month_*.voc, bare form)
    "ינואר", "פברואר", "מרץ", "מרס", "אפריל", "מאי", "יוני", "יולי",
    "אוגוסט", "ספטמבר", "אוקטובר", "נובמבר", "דצמבר",
    # holiday surfaces (well_known.tab, he) -- single-word or the first word
    # of a multi-word surface ("חג" of "חג הפסח"), left for the multiword
    # merge pass to glue back together once split off from "וחג"
    "פסח", "חנוכה", "חג",
    # marker_before (marker_before.voc) -- "ולפני יום" (and-before-a-day) is
    # ordinary coordinated speech ("...and a day ago, ...")
    "לפני",
    # marker_future (marker_future.voc) -- "ובעוד יומיים" (and-in-two-days)
    # is the forward-direction sibling of "לפני"; without the bare stem
    # restored the vav strip drops the whole mention instead of the
    # future-offset marker
    "בעוד",
    # bet-prefixed weekday noun (weekday_*.voc curated duplicate "ביום שני")
    # -- "וביום ראשון הבא" (and-on-next-Sunday) needs the bare "ביום" restored
    # so the multiword merge pass can still glue it to the weekday that follows
    "ביום",
})


def _he_vav_strip(tokens):
    out, changed = [], False
    for t in tokens:
        if (not t.is_number and len(t.text) > 1 and t.text[0] == "ו"
                and t.text[1:] in _HE_VAV_STEMS):
            out.append(Token(text=t.text[1:], raw=t.raw[1:], index=t.index,
                             char_start=t.char_start + 1 if t.char_start is not None else None,
                             char_end=t.char_end, cap=t.cap, prev_cap=t.prev_cap))
            changed = True
        else:
            out.append(t)
    return reindex(tuple(out)) if changed else tokens


# ``split_he_range_word`` (pre_hook) already split a fused vav + month/
# weekday/daypart word into two adjacent tokens ["ו"][word] BEFORE this hook
# ever sees the stream -- range detection needs that split visible on the raw
# pretoken stream.  Every OTHER grammar (bare-mention date resolution
# included) reads this hook's OUTPUT instead (``fold_tokens``, applied to
# ``pretokens()``'s result -- see ``pipeline.fold_tokens``/``pretokens``), so
# without undoing the split here first, a standalone fused mention
# ("ומרץ" alone, no range) would surface a stray unconsumed "ו" token in the
# remainder instead of resolving clean.  This re-merges the pair back into
# one bare-word token whenever the two tokens are ADJACENT with no gap
# (``char_end == char_start``, i.e. actually fused in the source text): a
# genuinely SPACED "ו word" ("ינואר ו מרץ") keeps its own "ו" token
# untouched, since that vav is an ordinary free connector word, not a
# proclitic to undo.
#
# NOTE this does not merely RESTORE the pre-pre_hook behaviour -- it
# BROADENS it.  ``_he_vav_strip`` above only ever curated Gregorian months
# into ``_HE_VAV_STEMS``, so on the prior release a fused bare mention of a
# weekday ("ושבת"), a daypart ("ובבוקר") or a Hebrew-calendar month
# ("וניסן", "וסיון") returned no match at all.  Gating the remerge on
# ``_HE_VAV_STEMS | _HE_TEMPORAL_WORDS`` (the same set the range-endpoint
# split itself uses, see ``_HE_TEMPORAL_WORDS`` above) makes those three
# additional classes resolve too, since they are now reachable via the
# split either way and leaving them unmerged would only add noise (a stray
# "ו" in the remainder) without preventing the match.  Pinned with tests
# (test_nl_ranges.py) rather than left as an undocumented side effect.
def _he_vav_remerge(tokens):
    out, i, n, changed = [], 0, len(tokens), False
    while i < n:
        t = tokens[i]
        if (i + 1 < n and t.text == "ו" and t.char_end is not None
                and tokens[i + 1].char_start == t.char_end
                and tokens[i + 1].text in (_HE_VAV_STEMS | _HE_TEMPORAL_WORDS)):
            nxt = tokens[i + 1]
            out.append(Token(text=nxt.text, raw=(t.raw or "") + (nxt.raw or ""),
                             index=t.index, char_start=t.char_start,
                             char_end=nxt.char_end, cap=nxt.cap,
                             prev_cap=nxt.prev_cap))
            i += 2
            changed = True
            continue
        out.append(t)
        i += 1
    return reindex(tuple(out)) if changed else tokens


# -- dual-noun unit split -----------------------------------------------
# Hebrew inflects a unit noun for the DUAL number when the count is exactly
# two -- יומיים ("two days") is one word, not "שני ימים" spelled together --
# so unlike every other count, "two" here is never a separate token for the
# offset grammar's ``NUM UNIT`` pre-amble to read ("לפני יומיים" stalled to
# ``None`` while its analytic sibling "לפני שני ימים" already worked).  Each
# dual surface is split here into a synthetic ``2`` NUM token followed by the
# ordinary PLURAL unit word it is dual for -- the same plural surface "לפני 2
# ימים" already binds -- so the split needs no grammar or resolver change,
# only reuse of the existing NUM+UNIT reading. The synthetic NUM carries a
# zero-width extent (mirrors the agglutinative "at"-marker split) so it never
# reaches the remainder text; the plural token keeps the dual word's raw/char
# extent so an unconsumed dual still reconstructs verbatim.
_HE_DUAL_UNIT_PLURAL = {
    "יומיים": "ימים", "יומים": "ימים",      # unit_dual_day.voc -> unit_day.voc
    "שעתיים": "שעות",                        # unit_dual_hour.voc -> unit_hour.voc
    "שבועיים": "שבועות",                     # unit_dual_week.voc -> unit_week.voc
    "דקתיים": "דקות",                        # unit_dual_minute.voc -> unit_minute.voc
    "חודשיים": "חודשים",                     # month (no dedicated .voc; unit_month.voc plural)
    "שנתיים": "שנים",                        # year (no dedicated .voc; unit_year.voc plural)
}


def _he_dual_split(tokens):
    out, changed = [], False
    for t in tokens:
        plural = None if t.is_number else _HE_DUAL_UNIT_PLURAL.get(t.text)
        if plural is None:
            out.append(t)
            continue
        out.append(Token(text="2", raw="", index=t.index, is_number=True,
                         value=2, char_start=t.char_start,
                         char_end=t.char_start))
        out.append(Token(text=plural, raw=t.raw, index=t.index,
                         char_start=t.char_start, char_end=t.char_end,
                         cap=t.cap, prev_cap=t.prev_cap))
        changed = True
    return reindex(tuple(out)) if changed else tokens


def fold_he(tokens):  # noqa: F811  -- wrap the cardinal fold with the fem ordinal
    """Fold the gematria year numeral (תשפ״ה → 5785), the ordinal teen
    (11..19) and the feminine ordinal (מחצית's "first/second") before the
    cardinal fold, then run the cardinal fold: none overlap (each is its own
    run), and the weekday-masculine ordinals stay untouched. The vav remerge
    runs first, undoing ``split_he_range_word``'s pre_hook split for any pair
    that was not consumed as a range connector, so a bare fused month/
    weekday/daypart mention resolves clean instead of leaving a stray "ו" in
    the remainder -- this both restores the pre-pre_hook Gregorian-month
    behaviour AND broadens it to weekday/daypart/Hebrew-month mentions that
    previously had no match at all (see the comment on ``_he_vav_remerge``);
    the vav strip runs next so a still-fused vav-prefixed date word (any
    ``_HE_VAV_STEMS`` role the pre_hook does not cover) folds/matches exactly
    like its bare form; the dual split runs on its result so a vav-prefixed
    dual ("ולפני יומיים") reaches it as a bare dual noun token."""
    return _fold_he_cardinal(_he_ordinal_rewrite(
        _he_teen_fold(_he_gematria_rewrite(
            _he_dual_split(_he_vav_strip(_he_vav_remerge(tokens)))))))
