"""Spelled-number folding for Greek.

Same job as the English/Slavic folds: collapse a maximal run of spelled
number-words into one digit :class:`~chronologia.extract.model.Token` so a
``NUM``/``HOUR``/``DAY`` slot binds the same whether the writer typed ``5``
or spelled it.  The pronouncer emits only the neuter forms, so the fold takes
the feminine clock-hour numerals that agree with *ώρα* ("τρεις"/"τέσσερις")
and the gendered hundreds as an explicit ``{surface: value}`` map: run
membership is gated on the surface and the value is read from the map when
the number model rejects the form.

``fold_el`` is wired as the language ``hook`` in ``locale/el/lang.json`` and
is a pure ``tuple[Token] -> tuple[Token]``.  Estonian, Finnish, Hungarian and
Basque read their numbers through numtag (:mod:`numlayer_agglutinative`).
"""
from __future__ import annotations

from dataclasses import replace
from importlib import import_module
from typing import Callable, Dict, Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import (NumberGrammar, make_fold,
                                                reindex, with_marked_h_clock)


def _make_fold(lang: str, extra_values: Dict[str, float] | None = None
               ) -> Callable[[Tuple[Token, ...]], Tuple[Token, ...]]:
    """A cardinal fold whose word set is derived from the model's own
    pronunciation, augmented by an ``extra`` map of oblique/hour surfaces the
    pronouncer does not emit (also the single-token fallback value source).
    The model import is deferred to first call.
    """
    extra = {k.lower(): v for k, v in (extra_values or {}).items()}
    holder: dict = {}

    def _load():
        mod = import_module("ovos_number_parser.numbers_" + lang)
        pron = getattr(mod, "pronounce_number_" + lang)
        extract = getattr(mod, "extract_number_" + lang)
        words = set()
        # Pronounce through 999, not just 100: the single-token hundred words
        # 200..900 ("διακόσια") only appear when a number >= 200 is
        # pronounced, so a run set built from 0..100 alone silently dropped
        # every spelled hundred.  The 100..999 sweep adds only
        # those hundred words (tens/units are already covered by 0..99), so the
        # set stays a closed class of genuine number-words.
        for n in range(0, 1000):
            try:
                for w in str(pron(n)).lower().replace("-", " ").split():
                    words.add(w)
            except Exception:
                pass
        words |= set(extra)

        def value_of(text):
            try:
                return extract(text)
            except Exception:
                return False
        return make_fold(NumberGrammar(
            is_number=lambda tok: tok.is_number or tok.text in words,
            extract=value_of,
            single_fallback=extra.get))

    def fold(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        f = holder.get("fold")
        if f is None:
            f = holder["fold"] = _load()
        return f(tokens)

    return fold


# -- Greek: feminine clock-hour numerals agree with the elided ώρα ----------
# extract_number_el already reads most; the run-membership gate needs the
# feminine surfaces the *pronounce* side (neuter) does not emit.
_EL_FEM_HOURS = {
    "μία": 1, "τρεις": 3, "τέσσερις": 4,
    "δεκατρείς": 13, "δεκατέσσερις": 14,
}
# Greek hundreds inflect for gender; ``pronounce_number_el`` emits only the
# NEUTER form (διακόσια), so the FEMININE hundreds that agree with feminine unit
# nouns ("διακόσιες μέρες" -- 200 days, μέρα being feminine) and the MASCULINE
# hundreds ("διακόσιοι μήνες") never entered the model-derived run set and folded
# to None.  ``extract_number_el`` reads every gender correctly, so the surfaces
# only need to be present in the run set; the neuter forms already arrive via
# the 0..999 pronunciation sweep.
_EL_HUNDREDS = {
    "διακόσιες": 200, "τριακόσιες": 300, "τετρακόσιες": 400,
    "πεντακόσιες": 500, "εξακόσιες": 600, "εφτακόσιες": 700,
    "επτακόσιες": 700, "οχτακόσιες": 800, "οκτακόσιες": 800,
    "εννιακόσιες": 900,
    "διακόσιοι": 200, "τριακόσιοι": 300, "τετρακόσιοι": 400,
    "πεντακόσιοι": 500, "εξακόσιοι": 600, "επτακόσιοι": 700,
    "οκτακόσιοι": 800, "εννιακόσιοι": 900,
}
# The everyday spellings of seven, eight and nine (Wiktionary: εφτά and οχτώ
# "alternative spelling of" επτά / οκτώ, εννιά "nine") beside the formal
# ones the pronouncer emits, so the spoken clock "στις οχτώ" (at eight) binds.
_EL_SPOKEN_UNITS = {"εφτά": 7, "οχτώ": 8, "εννιά": 9}
_el_numfold = _make_fold("el", {**_EL_FEM_HOURS, **_EL_HUNDREDS,
                                **_EL_SPOKEN_UNITS})

# -- Greek: the written day-of-month is a digit + ordinal ending -------------
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


def fold_el(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
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
    return _el_numfold(reindex(tuple(merged)))


# Greek writes "21h30" only behind a clock marker ("στις 21h30"); a bare
# "21h30" in Greek text is a duration or a citation to a French source.  The
# marker set is el's own marker_at and marker_oclock surfaces.
fold_el = with_marked_h_clock(fold_el, {"στις", "στη", "στην", "ώρα"})
