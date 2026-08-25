# -*- coding: utf-8 -*-
"""Spelled-number folding pre-pass for Albanian, plus its noun government.

The tokenizer only recognises *digit* runs as numbers, and Albanian speech
spells them.  This pass folds a run of spelled number-words into a single
digit :class:`~chronologia.extract.model.Token`, so a ``NUM``/``DAY``/
``HOUR``/``ORD`` slot binds the same whether the writer typed ``25`` or wrote
``njëzet e pesë``.  The module owns its number data outright, transcribed from
the dictionary source cited beside each table; nothing is delegated to an
external number back-end.

Albanian composes a two-digit numeral as ``TENS e UNIT`` -- three words with
the connective ``e`` in the middle ("njëzet e pesë" == 25) -- and writes the
hundreds as single fused words ("dyqind" == 200).  Above 100 the sources give
the round values only, so the fold reads one group and stops: a hundreds or
thousands word joined to a remainder is not attested and is refused rather
than invented.  :func:`read_run` returns ``None`` for anything it cannot
account for, and the fold then leaves the run untouched.

Three lexical facts about the year drive the rest of the module.  ``vjet``,
``sivjet`` and ``mot`` are last year, this year and next year -- three
unrelated words, not a pattern over ``vit``, so :func:`_year_adverb_rewrite`
maps each to the marker/unit pair the ``rel_period`` order reads instead of
deriving any of them from the others.  ``vjet`` is also the plural of ``vit``
("dy vjet më parë" == two years ago), so the adverb reading fires only where
no count precedes it.

And the counted noun's form is not free: it is selected by the word that
governs it.  :func:`governed_form` states that selection -- ablative after
``pas``, indefinite after ``më parë``/``para``, bare indefinite after
``këtë``/``çdo``, definite accusative only inside the fused ``e kaluar`` /
``e ardhshëm`` frame -- and :func:`unit_surface` spells it per unit.
"""
from __future__ import annotations

from typing import Callable, Dict, Optional, Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex

# ---------------------------------------------------------------------------
# Cardinals.  Transcribed from en.wiktionary.org's Albanian number generator
# data (``Module:number list/data/sq``), which is the table every Albanian
# numeral entry renders from, cross-checked headword by headword against the
# individual entries (një, dy, tre/tri, katër ... nëntëdhjetë, qind, mijë,
# zero).  ``tre`` and ``tri`` are the masculine and feminine three; the
# gendered pair is the only value with two cardinal surfaces below 100.
# ---------------------------------------------------------------------------
_UNITS: Dict[str, int] = {
    "zero": 0, "një": 1, "dy": 2, "tre": 3, "tri": 3, "katër": 4, "pesë": 5,
    "gjashtë": 6, "shtatë": 7, "tetë": 8, "nëntë": 9, "dhjetë": 10}

_TEENS: Dict[str, int] = {
    "njëmbëdhjetë": 11, "dymbëdhjetë": 12, "trembëdhjetë": 13,
    "katërmbëdhjetë": 14, "pesëmbëdhjetë": 15, "gjashtëmbëdhjetë": 16,
    "shtatëmbëdhjetë": 17, "tetëmbëdhjetë": 18, "nëntëmbëdhjetë": 19}

_TENS: Dict[str, int] = {
    "njëzet": 20, "tridhjetë": 30, "dyzet": 40, "pesëdhjetë": 50,
    "gjashtëdhjetë": 60, "shtatëdhjetë": 70, "tetëdhjetë": 80,
    "nëntëdhjetë": 90}

#: the round hundreds, each a single fused word, and the thousand.  Only the
#: round values are attested; a hundred or a thousand followed by a remainder
#: has no attested surface and :func:`read_run` refuses it.
_ROUND: Dict[str, int] = {
    "qind": 100, "njëqind": 100, "dyqind": 200, "treqind": 300,
    "katërqind": 400, "pesëqind": 500, "gjashtëqind": 600,
    "shtatëqind": 700, "tetëqind": 800, "nëntëqind": 900,
    "mijë": 1000, "njëmijë": 1000}

#: the connective joining a tens word to its unit ("njëzet e pesë" == 25).
_JOINER = "e"

#: the clock's named fraction words.  A bare "një" in front of one of them is
#: the indefinite article of "një çerek" ("a quarter"), not the number one, so
#: the cardinal fold leaves it standing for the clock order's ``indef`` slot.
_FRACTION_WORDS = frozenset({"çerek", "gjysmë", "gjysëm"})

_CARDINALS: Dict[str, int] = {**_UNITS, **_TEENS, **_TENS, **_ROUND}


# ---------------------------------------------------------------------------
# Ordinals.  Same source table.  From six upward the ordinal is homographic
# with its cardinal ("gjashtë" is both six and sixth), so only the values whose
# ordinal has a surface of its own are listed here -- the rest already fold as
# cardinals, to the same number.  A compound ordinal is written as ONE word,
# the tens and unit fused with the connective ("njëzetepestë" == 25th), unlike
# the compound cardinal's three separate words.
#
# The feminine "e para" is deliberately absent: "para" is also the preposition
# "before/ago" ("para dy ditësh" == two days ago), and no reading of the bare
# word could tell the two apart.  A refusal test pins the omission.
# ---------------------------------------------------------------------------
_ORD_TENS = {20: "njëzet", 30: "tridhjetë", 40: "dyzet", 50: "pesëdhjetë",
             60: "gjashtëdhjetë", 70: "shtatëdhjetë", 80: "tetëdhjetë",
             90: "nëntëdhjetë"}
_ORD_UNITS = {1: "njëtë", 2: "dytë", 3: "tretë", 4: "katërt", 5: "pestë",
              6: "gjashtë", 7: "shtatë", 8: "tetë", 9: "nëntë"}

_ORDINALS: Dict[str, int] = {
    "parë": 1, "dytë": 2, "tretë": 3, "katërt": 4, "pestë": 5,
    "njëzetë": 20, "dyzetë": 40, "qindtë": 100, "njëqindtë": 100,
    "mijtë": 1000, "njëmijtë": 1000}
for _t, _tw in _ORD_TENS.items():
    for _u, _uw in _ORD_UNITS.items():
        _ORDINALS[_tw + _JOINER + _uw] = _t + _u

#: the connective articles introducing an ordinal ("i parë", "e dytë", "të
#: tretë").  An Albanian ordinal is an adjective and never stands without one,
#: so the article is REQUIRED, not optional -- reading a bare "parë" as first
#: would swallow the second half of the "më parë" (ago) marker and turn every
#: "tre ditë më parë" into a clock time.
_ORD_ARTICLES = ("i", "e", "të")


# ---------------------------------------------------------------------------
# The year adverbs.  ``vjet`` (last year), ``sivjet`` (this year) and ``mot``
# (next year) are three unrelated lexical items -- en.wiktionary.org lists each
# as its own adverb, and CLDR 47 ``dateFields.json`` for ``sq`` uses exactly
# these three as the year field's -1/0/+1 relatives.  None is derived from
# ``vit``, so each maps to the marker/unit pair directly.
# ---------------------------------------------------------------------------
_YEAR_ADVERBS: Dict[str, Tuple[str, str]] = {
    "vjet": ("e kaluar", "vit"),
    "sivjet": ("këtë", "vit"),
    "mot": ("e ardhshëm", "vit"),
}


# ---------------------------------------------------------------------------
# Noun government: which form of the counted noun a construction takes.
#
# CLDR 47 ``dateFields.json`` for ``sq`` spells one form per construction and
# they disagree with each other, so a single "the word for day" would be wrong
# three times out of four:
#
#     pas {0} dite / pas {0} ditësh     ablative, singular or -sh plural
#     {0} ditë / {0} ditë më parë       indefinite
#     këtë javë, çdo ditë               bare indefinite
#     javën e kaluar, muajin e ardhshëm definite accusative
#
# The ablative and definite-accusative cells are confirmed against
# en.wiktionary.org's declension tables for ditë, javë, muaj, vit, orë,
# minutë, sekondë and shekull.
# ---------------------------------------------------------------------------
INDEFINITE = "indef"
INDEFINITE_PLURAL = "indef_pl"
ABLATIVE_SINGULAR = "abl_sg"
ABLATIVE_PLURAL = "abl_pl"
DEFINITE_ACCUSATIVE = "def_acc"

#: markers that put their counted noun in the ablative ("in/after X")
ABLATIVE_MARKERS = frozenset({"pas"})
#: markers that leave it indefinite, pluralised by the count ("X ago")
INDEFINITE_MARKERS = frozenset({"më parë", "para"})
#: determiners taking a bare indefinite noun ("this X", "every X")
BARE_MARKERS = frozenset({"këtë", "çdo"})
#: the fused last/next frame, the one construction taking a definite noun
DEFINITE_MARKERS = frozenset({"e kaluar", "e ardhshëm", "e ardhshme"})


def governed_form(marker: str, n: int = 1) -> str:
    """The form the noun takes under ``marker``, counted ``n`` times.

    ``n`` matters only where the marker's construction distinguishes number:
    the ablative and the indefinite both split singular from plural, the bare
    and definite frames take no count at all.
    """
    if marker in ABLATIVE_MARKERS:
        return ABLATIVE_SINGULAR if abs(int(n)) == 1 else ABLATIVE_PLURAL
    if marker in INDEFINITE_MARKERS:
        return INDEFINITE if abs(int(n)) == 1 else INDEFINITE_PLURAL
    if marker in BARE_MARKERS:
        return INDEFINITE
    if marker in DEFINITE_MARKERS:
        return DEFINITE_ACCUSATIVE
    raise KeyError(marker)


#: unit noun surfaces per governed form.  ``vit``/``vjet`` is suppletive: the
#: singular stem is ``vit`` and the plural stem ``vjet``, which is why the
#: indefinite plural and the ablative plural change stem while day/week/month
#: keep theirs.
UNIT_FORMS: Dict[str, Dict[str, str]] = {
    "day": {INDEFINITE: "ditë", INDEFINITE_PLURAL: "ditë",
            ABLATIVE_SINGULAR: "dite", ABLATIVE_PLURAL: "ditësh",
            DEFINITE_ACCUSATIVE: "ditën"},
    "week": {INDEFINITE: "javë", INDEFINITE_PLURAL: "javë",
             ABLATIVE_SINGULAR: "jave", ABLATIVE_PLURAL: "javësh",
             DEFINITE_ACCUSATIVE: "javën"},
    "month": {INDEFINITE: "muaj", INDEFINITE_PLURAL: "muaj",
              ABLATIVE_SINGULAR: "muaji", ABLATIVE_PLURAL: "muajsh",
              DEFINITE_ACCUSATIVE: "muajin"},
    "year": {INDEFINITE: "vit", INDEFINITE_PLURAL: "vjet",
             ABLATIVE_SINGULAR: "viti", ABLATIVE_PLURAL: "vjetësh",
             DEFINITE_ACCUSATIVE: "vitin"},
    "hour": {INDEFINITE: "orë", INDEFINITE_PLURAL: "orë",
             ABLATIVE_SINGULAR: "ore", ABLATIVE_PLURAL: "orësh",
             DEFINITE_ACCUSATIVE: "orën"},
    "minute": {INDEFINITE: "minutë", INDEFINITE_PLURAL: "minuta",
               ABLATIVE_SINGULAR: "minute", ABLATIVE_PLURAL: "minutash",
               DEFINITE_ACCUSATIVE: "minutën"},
    "second": {INDEFINITE: "sekondë", INDEFINITE_PLURAL: "sekonda",
               ABLATIVE_SINGULAR: "sekonde", ABLATIVE_PLURAL: "sekondash",
               DEFINITE_ACCUSATIVE: "sekondën"},
    "century": {INDEFINITE: "shekull", INDEFINITE_PLURAL: "shekuj",
                ABLATIVE_SINGULAR: "shekulli", ABLATIVE_PLURAL: "shekujsh",
                DEFINITE_ACCUSATIVE: "shekullin"},
}


def unit_surface(kind: str, marker: str, n: int = 1) -> str:
    """The surface of unit ``kind`` counted ``n`` times under ``marker``."""
    return UNIT_FORMS[kind][governed_form(marker, n)]


#: the gendered three: ``tri`` counts a feminine noun, ``tre`` a masculine
#: one.  Week, day, hour, minute and second are feminine; month, year and
#: century are masculine (en.wiktionary.org gender marks).
FEMININE_UNITS = frozenset({"day", "week", "hour", "minute", "second"})


def three(kind: str) -> str:
    """The form of "three" that agrees with unit ``kind``."""
    if kind not in UNIT_FORMS:
        raise KeyError(kind)
    return "tri" if kind in FEMININE_UNITS else "tre"


# ---------------------------------------------------------------------------
# The run reader
# ---------------------------------------------------------------------------

def read_run(text: str) -> Optional[int]:
    """Read the value of a run of Albanian number-word surfaces.

    One group only: a round hundred or thousand standing alone, or a tens word
    optionally joined by ``e`` to a unit.  Anything else -- two round words in
    a row, a hundred plus a remainder, a teen continuing a tens -- returns
    ``None``, because no source attests how Albanian writes it and a guessed
    reading would be a silently wrong number.
    """
    words = text.split()
    if not words:
        return None
    if len(words) == 1:
        return _CARDINALS.get(words[0])
    if len(words) == 3 and words[1] == _JOINER:
        tens, unit = _TENS.get(words[0]), _UNITS.get(words[2])
        if tens is not None and unit is not None and 1 <= unit <= 9:
            return tens + unit
    return None


def _numeric(tok: Token, value: int, end: Token = None) -> Token:
    return Token(text=str(value), raw=str(value), index=tok.index,
                 is_number=True, value=value, char_start=tok.char_start,
                 char_end=(end or tok).char_end)


def _is_numberish(tok: Token) -> bool:
    return tok.is_number or tok.text in _CARDINALS


def _run_bounds(tokens: Tuple[Token, ...], i: int) -> int:
    """End of the maximal numeral run starting at ``i`` (exclusive).

    A run is number-words joined by the connective, which is only part of the
    run when a number-word stands on both sides of it.
    """
    n, j = len(tokens), i
    while j < n:
        if _is_numberish(tokens[j]):
            j += 1
        elif (tokens[j].text == _JOINER and j + 1 < n and j > i
              and _is_numberish(tokens[j + 1])):
            j += 1
        else:
            break
    return j


def _refused_indices(tokens: Tuple[Token, ...]) -> frozenset:
    """Token indices inside a numeral run this module must not read at all.

    ``read_run`` stops after one group, which alone would leave an unconsumed
    numeral fragment beside a perfectly well-formed smaller number: "njëqind e
    njëzet" (an attempt at 120) would fold its tail to 20 and stand "njëqind e"
    aside, and "dy mijë e njëzet e gjashtë" (2026) would answer 1000.  A
    partial numeral silently becoming a smaller number is worse than no answer,
    so a run carrying a hundreds or thousands word beside any other number
    refuses WHOLE -- no token in it folds, nothing binds, and the phrase
    returns nothing.

    A round word standing alone is untouched ("njëqind vjet më parë" is a
    hundred years), and a run with no round word in it keeps composing exactly
    as before, which is what leaves the clock's "shtatë e njëzet e pesë"
    (07:25) and the compound "njëzet e pesë" (25) intact.
    """
    refused, i, n = set(), 0, len(tokens)
    while i < n:
        if not _is_numberish(tokens[i]):
            i += 1
            continue
        end = _run_bounds(tokens, i)
        run = tokens[i:end]
        counted = [t for t in run if _is_numberish(t)]
        if len(counted) > 1 and any(t.text in _ROUND for t in counted):
            refused.update(range(i, end))
        i = end
    return frozenset(refused)


def _cardinal_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Fold a spelled cardinal, the ``TENS e UNIT`` compound included."""
    refused = _refused_indices(tokens)
    out, i, n, changed = [], 0, len(tokens), False
    while i < n:
        t = tokens[i]
        if (t.is_number or t.text not in _CARDINALS or i in refused
                or (t.text == "një" and i + 1 < n
                    and tokens[i + 1].text in _FRACTION_WORDS)):
            out.append(t)
            i += 1
            continue
        run = 3 if (t.text in _TENS and i + 2 < n
                    and tokens[i + 1].text == _JOINER
                    and not tokens[i + 2].is_number
                    and tokens[i + 2].text in _UNITS) else 1
        value = read_run(" ".join(tok.text for tok in tokens[i:i + run]))
        if value is None:
            out.append(t)
            i += 1
            continue
        out.append(_numeric(t, value, tokens[i + run - 1]))
        i, changed = i + run, True
    return reindex(out) if changed else tokens


def _ordinal_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Fold a spelled ordinal together with the article introducing it."""
    out, i, n, changed = [], 0, len(tokens), False
    while i < n:
        t = tokens[i]
        if (not t.is_number and t.text in _ORD_ARTICLES and i + 1 < n
                and not tokens[i + 1].is_number
                and tokens[i + 1].text in _ORDINALS):
            out.append(_numeric(t, _ORDINALS[tokens[i + 1].text],
                                tokens[i + 1]))
            i, changed = i + 2, True
            continue
        out.append(t)
        i += 1
    return reindex(out) if changed else tokens


def _year_adverb_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Expand a year adverb into the marker + unit pair the grammar reads.

    ``vjet`` is read as the adverb only when nothing counts it: after a number
    it is the plural of ``vit`` ("dy vjet më parë" == two years ago), which is
    a duration, not last year.
    """
    out, changed = [], False
    for i, t in enumerate(tokens):
        pair = None if t.is_number else _YEAR_ADVERBS.get(t.text)
        if pair is None or (t.text == "vjet" and i and tokens[i - 1].is_number):
            out.append(t)
            continue
        marker, unit = pair
        out.append(Token(text=marker, raw=t.raw, index=t.index,
                         char_start=t.char_start, char_end=t.char_end,
                         cap=t.cap))
        out.append(Token(text=unit, raw=t.raw, index=t.index,
                         char_start=t.char_start, char_end=t.char_end))
        changed = True
    return reindex(out) if changed else tokens


def _compose(*passes: Callable) -> Callable:
    def run(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        for p in passes:
            tokens = p(tokens)
        return tokens
    return run


#: the cardinal fold runs FIRST, for two reasons.  From six upward an ordinal
#: is spelled exactly like its cardinal, so "njëzet e gjashtë" (26) must claim
#: its unit before the ordinal pass could read the tail "e gjashtë" as a bare
#: sixth; and the year-adverb pass decides whether "vjet" is counted by looking
#: for a number to its left, which is only there once the count has folded.
fold_sq = _compose(_cardinal_rewrite, _year_adverb_rewrite, _ordinal_rewrite)
