# -*- coding: utf-8 -*-
"""Arabic and Hebrew date words over the numtag number layer.

Fixed multi-word surfaces ("بعد غد", "יום ראשון") are merged to one token by
``pipeline.merge_multiword``, so the ``*.voc`` files list them with their
space.

numtag reads the spelled numbers, the "و"-glued compounds and the ordinal
teens.  The shared rules of :mod:`chronologia.extract.numlayer` claim
clock fractions, scale words and counts of things.  This module claims the
ordinals and cardinals that are also weekday or month names ("الاثنين",
"تشرين الأول", "יום שני") and adds the clock, dual-noun and gematria passes
around that fold.

Each pass is a ``tuple[Token] -> tuple[Token]`` transform that keeps
``Token.index`` contiguous; they are wired as the language ``hook`` and
``pre_hook``.
"""
from __future__ import annotations

import re as _re
from pathlib import Path

from ovos_spec_tools import read_resource_file

from chronologia.extract.model import Token
from chronologia.extract.numlayer import (DateWords, count_words, fold,
                                          locale_words)
from chronologia.extract.numfold_engine import reindex
from chronologia.hebrew_numerals import (gematria_value, hebrew_year_value,
                                          is_gematria_numeral)

_LOCALE_DIR = Path(__file__).parent.parent / "locale"


_AR_WORDS = DateWords(
    lang="ar",
    fractions=locale_words("ar", "clock_fraction_"),
    counts=count_words("ar"))


# الأول (first) and الثاني (second) are the ordinal everywhere except directly
# after a Levantine solar month prefix (تشرين الأول = October, كانون الثاني =
# January, جمادى الأولى, ربيع الأول), where they form the month name.  They are
# claimed as words there and fold to the ordinal elsewhere, so "النصف الأول"
# (first half) reads while تشرين الأول stays October.  Confirmed by a native
# speaker (TigreGotico/chronologia #268).
_AR_MONTH_ORD_PREFIX = frozenset({"تشرين", "كانون", "جمادى", "ربيع"})
_AR_MONTH_ORDINAL = frozenset({"الأول", "الاول", "الأولى", "الاولى", "الثاني",
                               "الثانية"})
#: "أمس الأول" (the day before yesterday) takes the ordinal after the day
#: word.  Folding it to 1 would break the phrase before the multiword pass
#: merges it and the day word alone would answer YESTERDAY.
_AR_DAY_ORD_PREFIX = frozenset({"أمس", "امس", "الأمس"})

#: "أول أمس" and "أول من أمس" (the day before yesterday) put the ordinal
#: before the day word.
_AR_DAY_ORD_FIRST = frozenset({"أول", "اول"})
#: Month names numtag also reads as a number ("صفر" is a month and zero).
_AR_MONTHS = locale_words("ar", "month_")
#: Weekday names numtag also reads as a number ("الاثنين" is Monday and two).
_AR_WEEKDAYS = locale_words("ar", "weekday_")


def _ar_date_names(tokens):
    """Claim the number words that are part of a weekday, a month or a day
    name: "الاثنين", "تشرين الأول", "أمس الأول", "أول أمس"."""
    claimed = set()
    for i, t in enumerate(tokens):
        if t.mention is None or t.mention.text != t.raw:
            continue
        prev = tokens[i - 1].text if i else None
        after = [u.text for u in tokens[i + 1:i + 3]]
        if (t.text in _AR_WEEKDAYS or t.text in _AR_MONTHS
                or (t.text in _AR_MONTH_ORDINAL
                    and (prev in _AR_MONTH_ORD_PREFIX
                         or prev in _AR_DAY_ORD_PREFIX))
                or (t.text in _AR_DAY_ORD_FIRST and after
                    and (after[0] in _AR_DAY_ORD_PREFIX
                         or after[0] == "من" and after[1:2]
                         and after[1] in _AR_DAY_ORD_PREFIX))):
            claimed.add(i)
    return claimed, set(), {}


# -- feminine ordinal CLOCK hour fold ----------------------------------------
# Arabic tells clock hours with the feminine ordinal: الثامنة is eight o'clock.
# In an unambiguous clock context (right after الساعة, or right before an am/pm
# daypart particle) the ordinal hour الواحدة..الثانية عشرة folds to a CLOCK
# "H:00" token.  Every other use of these words stays untouched.
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
# Two-word teen hours: الحادية عشرة (11), الثانية عشرة (12).
_AR_FEM_HOUR_TEEN = {"الحادية": 11, "الثانية": 12}


def _ar_clock_token(hour, first, last):
    text = "%d:00" % hour
    return Token(text=text, raw=text, index=first.index,
                 char_start=first.char_start, char_end=last.char_end)


def _ar_clock_hour_fold(tokens):
    """Fold a feminine ordinal hour (1..12) to a CLOCK ``H:00`` token in a
    clock context."""
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


_CLOCK_TEXT = _re.compile(r"\d{1,2}:\d{2}(?::\d{2})?$")
# Clock-fraction surfaces (``clock_fraction_{30,15}.voc``) without the article
# or the "و" proclitic.  "الساعة الثالثة والنصف" tokenises as [CLOCK][والنصف], a
# fused token that is neither CLOCKDIR nor FRACTION.
_AR_CLOCK_FRACTION = frozenset({"النصف", "نصف", "الربع", "ربع"})


def _ar_clock_fraction_split(tokens):
    """Split a "و"-glued clock fraction ("والنصف" -> "و" + "النصف") that follows
    a folded CLOCK token, leaving every other و-glued word ("وعشرون") alone."""
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


def _temporal_words(lang, globs):
    """The single-word surfaces of the vocabulary files matching ``globs``."""
    words = set()
    for pattern in globs:
        for path in sorted((_LOCALE_DIR / lang).glob(pattern)):
            words.update(w for w in read_resource_file(path) if " " not in w)
    return frozenset(words)


#: Vocabulary files whose bare words may follow a fused waw as a range
#: endpoint: months (Gregorian and Islamic-civil), weekdays and dayparts.
#: ``weekday_abbr_6.voc`` is left out: its bare Sunday "أحد" is spelled like
#: the stem inside "واحد" (one), so "واحد وعشرين يوما" would lose a day.
#: Multiword surfaces are skipped because splitting the proclitic off one
#: would leave a remainder the multiword merge never re-glues.
_AR_WORD_ROLE_GLOBS = ("month_*.voc", "weekday_[0-9].voc", "daypart_*.voc")


_AR_TEMPORAL_WORDS = _temporal_words("ar", _AR_WORD_ROLE_GLOBS)


def split_ar_range_word(tokens):
    """Split a "و"-glued temporal word off its proclitic ("بين يناير ومارس" ->
    [بين][يناير][و][مارس]), so the second endpoint of a range is visible to the
    range grammar.  Only a remainder in ``_AR_TEMPORAL_WORDS`` splits; words
    that merely start with و ("وسط", "واحد") stay whole.  Wired as
    ``pre_hook``, which runs before the ``hook`` number fold."""
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


#: Vocabulary files whose bare words may follow a fused vav as a range
#: endpoint: months and dayparts.  The weekday files are left out: "שני"
#: (Monday) is also the construct form of "two", so "יום ושני שעות" (a day and
#: two hours) would split into a Monday range endpoint, and the other bare
#: weekdays are ordinals.  Multiword surfaces are skipped as in the Arabic
#: guard.
_HE_WORD_ROLE_GLOBS = ("month_*.voc", "weekday_5.voc", "daypart_*.voc")

#: "אב" (the month Av) is also the everyday noun "father": admitting it read
#: "אם ואב" (mother and father) as a confident month span.  A fused "ואב" range
#: endpoint ("בין ניסן ואב") therefore stays truncated; the spaced form works.
_HE_VAV_HOMOGRAPH_EXCLUDE = frozenset({"אב"})


_HE_TEMPORAL_WORDS = (_temporal_words("he", _HE_WORD_ROLE_GLOBS)
                      - _HE_VAV_HOMOGRAPH_EXCLUDE)


def split_he_range_word(tokens):
    """Split a vav-glued temporal word off its proclitic ("בין ינואר ומרץ" ->
    [בין][ינואר][ו][מרץ]), so the second endpoint of a range is visible to the
    range grammar.  Only a remainder in ``_HE_TEMPORAL_WORDS`` splits; words
    that merely start with ו ("ורוד", "ותיק") stay whole.  Wired as
    ``pre_hook``, which runs before the ``hook`` number fold."""
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


# -- dual-noun unit split ----------------------------------------------------
# A dual unit noun (ساعتان / ساعتين, "two hours") hides its count, so the
# offset grammar's ``NUM UNIT`` reading never sees it.  Each dual surface is
# split into a zero-width synthetic ``2`` NUM token and the plural unit it is
# dual for, which the grammar already binds ("بعد 2 ساعات").  The plural token
# keeps the dual word's raw and char extent, so an unconsumed dual still
# reconstructs verbatim.  Both the nominative -ān and the oblique -ayn are
# read (W. Wright, *A Grammar of the Arabic Language*, 3rd ed., vol. I, §299).
# Keys are the surfaces of ``locale/ar/unit_dual_*.voc``.
_AR_DUAL_UNIT_PLURAL = {
    "ساعتان": "ساعات", "ساعتين": "ساعات",      # unit_dual_hour.voc
    "يومان": "أيام", "يومين": "أيام",          # unit_dual_day.voc
    "أسبوعان": "أسابيع", "أسبوعين": "أسابيع",  # unit_dual_week.voc
    "اسبوعان": "أسابيع", "اسبوعين": "أسابيع",  # ... alif-hamza-less spelling
    "دقيقتان": "دقائق", "دقيقتين": "دقائق",    # unit_dual_minute.voc
    "ثانيتان": "ثوان", "ثانيتين": "ثوان",      # unit_dual_second.voc
}


def _dual_split(tokens, plural_of):
    """Replace each dual unit noun with ``2`` and its plural, per ``plural_of``."""
    out, changed = [], False
    for t in tokens:
        plural = None if t.is_number else plural_of.get(t.text)
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


# -- additive fraction on a counted unit ---------------------------------------
# "N and a half/quarter <unit>" is written with the fraction fused to the
# conjunction after the unit: "ساعة ونصف" (an hour and a half), "ساعتين ونصف".
# The offset grammar reads a NUM before its UNIT, so the fraction is folded into
# one number: a bare singular unit counts one, a preceding numeral keeps its
# value.  The synthetic NUM spans from the unit to the fraction.
_AR_ADDITIVE_FRACTION = {"ونصف": 0.5, "وربع": 0.25}


_AR_UNIT_SURFACES = frozenset(
    w for path in sorted((_LOCALE_DIR / "ar").glob("unit_*.voc"))
    for w in read_resource_file(path))


def _ar_additive_fraction(tokens):
    out, changed = [], False
    i = 0
    while i < len(tokens):
        t = tokens[i]
        nxt = tokens[i + 1] if i + 1 < len(tokens) else None
        if (nxt is not None and not t.is_number and not nxt.is_number
                and nxt.text in _AR_ADDITIVE_FRACTION
                and t.text in _AR_UNIT_SURFACES):
            frac = _AR_ADDITIVE_FRACTION[nxt.text]
            if out and out[-1].is_number and out[-1].value is not None:
                num = out.pop()
                value = num.value + frac
                start = num.char_start
            else:
                value = 1 + frac
                start = t.char_start
            out.append(Token(text=str(value), raw="", index=t.index,
                             is_number=True, value=value,
                             char_start=start, char_end=nxt.char_end))
            out.append(t)
            changed = True
            i += 2
            continue
        out.append(t)
        i += 1
    return reindex(tuple(out)) if changed else tokens


def fold_ar(tokens):
    """Fold the feminine ordinal clock hour, split a "و"-glued clock fraction
    off it, fold the numbers with the weekday and month names claimed, then
    split dual unit nouns and fold additive fractions on the folded stream."""
    tokens = _ar_clock_fraction_split(_ar_clock_hour_fold(tokens))
    tokens = fold(tokens, _AR_WORDS, extra=_ar_date_names)
    return _ar_additive_fraction(_dual_split(tokens, _AR_DUAL_UNIT_PLURAL))


# -- Hebrew ------------------------------------------------------------------
_HE_WORDS = DateWords(
    lang="he",
    fractions=locale_words("he", "clock_fraction_"),
    counts=count_words("he"))
# The ordinals שני..שישי (2..6) are the weekday names Monday..Friday and ראשון
# (1) is Sunday.  Folding any of them to a digit would break bare-weekday,
# recurrence and offset parsing, so they stay words; the spelled ordinal
# quarter ("רבעון שלישי") therefore stays a documented xfail.
_HE_WEEKDAY_ORDINALS = frozenset(
    w for w in locale_words("he", "weekday_abbr_") if " " not in w)
#: Decade names ("שנות השמונים"): one word for the multiword pass, whose second
#: word is not the count 80.
_HE_DECADES = locale_words("he", "decade_word_")

# שני is both the construct form of the cardinal "two" and the ordinal "second",
# and Hebrew names weekdays by ordinal (יום שני is Monday).  Reading it as 2 once
# turned "כל יום שני" (every Monday) into FREQ=DAILY.
_HE_SHENI = "שני"
# The day noun a weekday name is built on, bare and with the ב- "on" prefix.
_HE_DAY_NOUN = frozenset({"יום", "ביום"})


def _he_counts_a_noun(tokens, i):
    """Whether ``שני`` at index ``i`` can be the cardinal "two".

    A construct-state cardinal binds the noun it counts ("שני ימים"), so it
    needs a following word, and it cannot follow its own day noun ("יום שני").
    """
    if i and tokens[i - 1].text in _HE_DAY_NOUN:
        return False
    return i + 1 < len(tokens) and not tokens[i + 1].is_number


#: The feminine hour numerals 1..10.  Hebrew tells time in the feminine and
#: writes the preposition ב־ ("at") fused on: "בשבע בבוקר" is one token to a
#: whitespace tokenizer.  The masculine forms are absent: "בשני" is Monday.
_HE_BET_HOURS = {
    "אחת": 1, "שתיים": 2, "שלוש": 3, "ארבע": 4, "חמש": 5,
    "שש": 6, "שבע": 7, "שמונה": 8, "תשע": 9, "עשר": 10,
}


#: What must follow a fused numeral for it to be a clock.  "בשבע רצון" (gladly)
#: and "בשבע עיניים" are idioms on the same spelling, so only a time word closes
#: the split.
_HE_CLOCK_TAIL = frozenset({
    "בבוקר", "בערב", "בלילה", "ורבע", "וחצי",
    # The afternoon meridiem has two words; its first token follows the numeral.
    "אחר", "אחה",
})


def _he_split_bet_hour(tokens):
    """Split the fused "at" preposition off a feminine hour numeral that a time
    word closes, giving ["ב"][numeral] for the ``at HOUR`` grammar."""
    out, changed = [], False
    for i, t in enumerate(tokens):
        nxt = tokens[i + 1] if i + 1 < len(tokens) else None
        if (nxt is not None and nxt.text in _HE_CLOCK_TAIL
                and not t.is_number and len(t.text) > 1 and t.text[0] == "ב"
                and t.text[1:] in _HE_BET_HOURS):
            out.append(Token(text="ב", raw=t.raw[0], index=t.index,
                             char_start=t.char_start,
                             char_end=t.char_start + 1 if t.char_start is not None else None))
            hour = _HE_BET_HOURS[t.text[1:]]
            out.append(Token(text=str(hour), raw=t.raw[1:], index=t.index,
                             is_number=True, value=hour,
                             char_start=t.char_start + 1 if t.char_start is not None else None,
                             char_end=t.char_end))
            changed = True
        else:
            out.append(t)
    return reindex(tuple(out)) if changed else tokens


def _he_date_names(tokens):
    """Claim the number words that name a weekday, a decade, or a fused "at"
    hour that no time word closes ("בשבע רצון").  ``שני`` stays a word where it
    cannot count a noun (:func:`_he_counts_a_noun`).
    """
    claimed = set()
    for i, t in enumerate(tokens):
        if t.mention is None or t.is_number or t.mention.text != t.raw:
            continue
        if i and f"{tokens[i - 1].text} {t.text}" in _HE_DECADES:
            claimed.add(i)
        elif t.text == _HE_SHENI:
            if not _he_counts_a_noun(tokens, i):
                claimed.add(i)
        elif t.text in _HE_WEEKDAY_ORDINALS:
            claimed.add(i)
        elif t.text[0] == "ב" and t.text[1:] in _HE_BET_HOURS:
            claimed.add(i)
    return claimed, set(), {}


def _fold_he_cardinal(tokens):
    """The Hebrew number fold, with the fused "at" hour split off first."""
    return fold(_he_split_bet_hour(tokens), _HE_WORDS, extra=_he_date_names)


# -- feminine ordinals 1/2 that agree with the "half" noun מחצית ---------------
# Weekdays use the masculine ordinal (ראשון, שני), which the cardinal fold
# withholds.  מחצית is feminine, so "the first/second half" takes ראשונה /
# שנייה, which are no weekday name and fold to the digit the half_period NUM
# slot binds.  Only 1 and 2 occur (Even-Shoshan; Academy of the Hebrew
# Language).
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
# Hebrew years are written with letters: תשפ״ה is 785, the year 5785.  Only a
# numeral marked by a geresh or gershayim folds, so ordinary words and weekday
# names are untouched.  The fold also needs a year context (a Hebrew month or
# a year word before it) or a Hebrew month after it, which keeps the equally
# marked abbreviations סופ״ש (weekend) and לפנה״ס (BCE) from reading as numbers.
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


# -- vav-conjunction (ו) proclitic strip --------------------------------------
# Hebrew glues "and" onto the next word ("ומחר", "ופסח").  A token starting with
# ו folds to its remainder when that is in a closed set of date, month and
# holiday stems; ו-initial roots ("ותיק", "ורוד") stay untouched.
_HE_VAV_STEMS = frozenset({
    # named days (named_day_*.voc)
    "מחר", "היום", "אתמול", "אמש", "מחרתיים", "מחרתים",
    # Gregorian months (month_*.voc, bare form)
    "ינואר", "פברואר", "מרץ", "מרס", "אפריל", "מאי", "יוני", "יולי",
    "אוגוסט", "ספטמבר", "אוקטובר", "נובמבר", "דצמבר",
    # holiday surfaces (well_known.tab), including the first word of a
    # multiword surface ("חג" of "חג הפסח") for the multiword merge pass
    "פסח", "חנוכה", "חג",
    # marker_before.voc: "ולפני יום" is ordinary coordinated speech
    "לפני",
    # marker_future.voc: "ובעוד יומיים", the forward sibling of "לפני"
    "בעוד",
    # "וביום ראשון הבא" needs "ביום" restored for the multiword merge pass
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


# ``split_he_range_word`` (pre_hook) splits a fused vav + temporal word before
# this hook runs, because range detection reads the raw stream.  Every other
# grammar reads this hook's output, so a standalone fused mention ("ומרץ")
# would leave a stray "ו" in the remainder.  This re-merges the pair into the
# bare word when the two tokens are adjacent in the source text.  A spaced
# "ינואר ו מרץ" keeps its "ו": there it is a free connector.  The re-merge also
# lets a fused bare weekday, daypart or Hebrew-month mention resolve.
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


# -- dual-noun unit split -----------------------------------------------------
# Hebrew dual unit nouns (יומיים, "two days") are split like the Arabic ones,
# see ``_dual_split``.
_HE_DUAL_UNIT_PLURAL = {
    "יומיים": "ימים", "יומים": "ימים",      # unit_dual_day.voc -> unit_day.voc
    "שעתיים": "שעות",                        # unit_dual_hour.voc -> unit_hour.voc
    "שבועיים": "שבועות",                     # unit_dual_week.voc -> unit_week.voc
    "דקתיים": "דקות",                        # unit_dual_minute.voc -> unit_minute.voc
    "חודשיים": "חודשים",                     # month (no dedicated .voc; unit_month.voc plural)
    "שנתיים": "שנים",                        # year (no dedicated .voc; unit_year.voc plural)
}


def fold_he(tokens):
    """Fold Hebrew date words, in this order: undo the pre_hook vav split where
    no range consumed it, strip a vav proclitic from curated stems, split dual
    unit nouns, fold gematria years, rewrite feminine ordinals (מחצית's "first"
    and "second"), then run the number fold."""
    tokens = _he_vav_strip(_he_vav_remerge(tokens))
    tokens = _dual_split(tokens, _HE_DUAL_UNIT_PLURAL)
    return _fold_he_cardinal(_he_ordinal_rewrite(_he_gematria_rewrite(tokens)))
