"""Greek date words over the numtag number layer.

numtag reads the Greek numbers in every gender ("τρεις", "διακόσιες") and the
spoken forms ("εφτά", "οχτώ").  The shared rules of
:mod:`chronologia.extract.numlayer_germanic` claim the clock fractions, the
deep-time scale words and the counts of things.  This module joins the
ordinal ending a writer glues onto a digit day, and claims the weekday names
that are also ordinals.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex, with_marked_h_clock
from chronologia.extract.numlayer_germanic import (DateWords, count_words, fold,
                                                   locale_words)

# The written day-of-month is a digit and an ordinal ending:
# "5η Μαρτίου" (the 5th of March), "της 5ης Μαρτίου" (of the 5th of March).
# A Greek τακτικό αριθμητικό (ordinal) inflects for gender/case; when spelled
# with a digit the ending rides on the numeral ("5η", "5ος", "5ου").  The
# day-of-month agrees with the feminine ημέρα, so "Nη"/"Nης" are the everyday
# forms, but the masculine/neuter/plural endings are the same closed class and
# are folded too so any digit-ordinal binds its numeral.  Source: Νεοελληνική
# Γραμματική (Τριανταφυλλίδης), τακτικά αριθμητικά; Πύλη για την Ελληνική Γλώσσα
# (greek-language.gr) ordinal-ending paradigm.
#
# The tokenizer shears the ending off the digit ("5η" -> "5", "η"), so a number
# immediately followed by a bare ordinal-ending fragment folds back to the
# number and the DAY/NUM slot binds.  The merge is gated on ADJACENCY (no space
# between the two source tokens): "η"/"ο"/"οι" are also the feminine/neuter
# definite articles, and "5 η ώρα" ("5 o'clock", article present) must keep its
# separate article token -- only the glued "5η" is an ordinal.
_EL_ORD_SUFFIX = frozenset({
    "η", "ης", "ην",              # feminine (day agrees with ημέρα): nom/gen/acc
    "ος", "ου", "ο", "ον",       # masculine / neuter
    "οι", "ων", "ους", "ες",     # plural forms
})


def _merge_digit_ordinal(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    merged = []
    i = 0
    n = len(tokens)
    while i < n:
        t = tokens[i]
        nxt = tokens[i + 1] if i + 1 < n else None
        if (t.is_number and nxt is not None and not nxt.is_number
                and nxt.text in _EL_ORD_SUFFIX
                and t.char_end is not None and nxt.char_start is not None
                and nxt.char_start == t.char_end):
            merged.append(replace(t, raw=t.raw + nxt.raw,
                                  char_end=nxt.char_end
                                  if nxt.char_end is not None else t.char_end))
            i += 2
            continue
        merged.append(t)
        i += 1
    return reindex(tuple(merged))


_WORDS = DateWords(
    lang="el",
    fractions=locale_words("el", "clock_fraction_"),
    counts=count_words("el"))
#: The weekday names.  Greek names Tuesday, Wednesday and Thursday with the
#: feminine ordinal: "Τρίτη" is Tuesday and the third.
_WEEKDAYS = locale_words("el", "weekday_")
#: The words before which a weekday name is the ordinal: "την τρίτη Δευτέρα
#: του Μαΐου" (the third Monday of May), "η τρίτη εβδομάδα" (the third week).
_ORDINAL_BEFORE = (_WEEKDAYS | locale_words("el", "month_", "unit_")
                   | locale_words("el", "marker_quarter_word",
                                  "marker_month_word", "marker_year_word"))


def _weekdays(tokens: Tuple[Token, ...]):
    """Claim a weekday name that numtag reads as an ordinal, unless a
    weekday, a month, a unit or a period word follows it."""
    claimed = set()
    for i, t in enumerate(tokens):
        if (t.mention is not None and t.text in _WEEKDAYS
                and t.mention.text.lower() == t.text):
            nxt = tokens[i + 1].text if i + 1 < len(tokens) else None
            if nxt not in _ORDINAL_BEFORE:
                claimed.add(i)
    return claimed, set(), {}


def _fold_el(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    return fold(_merge_digit_ordinal(tokens), _WORDS, extra=_weekdays)


# Greek writes "21h30" only behind a clock marker ("στις 21h30"); a bare
# "21h30" in Greek text is a duration or a citation to a French source.  The
# marker set is el's own marker_at and marker_oclock surfaces.
fold_el = with_marked_h_clock(_fold_el, {"στις", "στη", "στην", "ώρα"})
