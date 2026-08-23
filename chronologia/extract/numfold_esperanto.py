# -*- coding: utf-8 -*-
"""Spelled-number folding for Esperanto -- the single fully regular case.

Esperanto's numeral system has no irregulars and no case/gender agreement at
all: the closed set of cardinal words is 0..10, the nine fused
multiples-of-ten (``dudek`` = du+dek = 20, ..., ``naŭdek`` = 90), ``cent``
(hundred) and ``mil`` (thousand); every other value is spelled by writing the
magnitude-descending words left to right as SEPARATE tokens ("dek du" = 12,
"dudek du" = 22, "dek du mil" = 12000).  Ordinals are the regular adjectival
suffix ``-a`` on the cardinal stem ("tri" -> "tria"), and a compound ordinal
inflects only its LAST element ("dudek tri" -> "dudek tria" = 23rd), the
tens staying the bare cardinal -- mirroring the Baltic day-of-month shape in
:mod:`chronologia.extract.numfold_baltic`, minus any declension table.
Source: en.wikipedia.org, "Esperanto grammar" (cardinal numerals, the
compounding rule, the ``-a`` ordinal suffix).

The day-of-month compound is shipped SPACE-SEPARATED ("dudek tria"), not
hyphenated ("dudek-tria") or solid ("dudektria"): the exact orthographic
convention for the joined spelling is not attested in the sources this
locale was built from, but Esperanto's general compounding rule always
keeps the two words independently readable, so the unhyphenated
two-token spelling is the safe subset that needs no unverified citation.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Callable, Dict, Optional, Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex

#: the written digit-ordinal suffix ("15-a" = 15th, "15-an" = accusative
#: 15th): the tokenizer shears the hyphen, leaving the bare digit and a
#: dangling "a"/"an" fragment that no other vocabulary claims.  Merged back
#: onto the digit -- not folded to a distinct value, since a numeric slot
#: (DAY/ORD) reads a plain digit either way -- so the token stream is
#: "15 de marto", not "15 a de marto" stranding the fragment and letting an
#: unrelated construction (the clock's bare "article HOUR") claim the digit
#: instead.  Esperanto's ordinal suffix is the regular adjectival "-a"
#: (en.wikipedia.org "Esperanto grammar"); "-an" is the same suffix under
#: the accusative -n a fully-specified date takes on its ordinal
#: (mirrored from the spelled form, "la unuan de januaro" -- see
#: locale/eo/lang.json comments).
_DIGIT_ORD_SUFFIX = frozenset({"a", "an"})

_CARDINALS: Dict[str, int] = {
    "nul": 0, "unu": 1, "du": 2, "tri": 3, "kvar": 4, "kvin": 5, "ses": 6,
    "sep": 7, "ok": 8, "naŭ": 9, "dek": 10,
    "dudek": 20, "tridek": 30, "kvardek": 40, "kvindek": 50, "sesdek": 60,
    "sepdek": 70, "okdek": 80, "naŭdek": 90,
}
_TENS: Dict[str, int] = {k: v for k, v in _CARDINALS.items() if v >= 20}
_HUNDRED = "cent"
_SCALE = "mil"

#: every cardinal plus "-a" is the regular ordinal ("tri" -> "tria", "dek" ->
#: "deka", "dudek" -> "dudeka"); "cent"/"mil" ordinalise the same way
#: ("centa", "mila").  No entry collides -- no cardinal surface ends in "a".
_ORDINALS: Dict[str, int] = {w + "a": v for w, v in _CARDINALS.items()}
_ORDINALS[_HUNDRED + "a"] = 100
_ORDINALS[_SCALE + "a"] = 1000

#: the tens (or "dek" itself, for 11..19: "dek tria" = 13th) element of a
#: compound day-of-month ordinal, which stays the bare cardinal while only
#: the trailing unit inflects ("dudek tria" = 23rd).
_DAY_TENS = {**_TENS, "dek": 10}


def read_run(text: str) -> Optional[int]:
    """The value of a joined run of Esperanto cardinal-word surfaces.

    Additive over the closed word set: "cent" multiplies the group
    accumulated so far, "mil" multiplies it and closes it into the running
    total ("dek du mil dudek kvin" == 12025).  Returns ``None`` when a word
    is not a number-word, so the fold leaves an unrelated run untouched.
    """
    total = 0
    group = 0
    seen = False
    for word in text.split():
        if word.isdigit():
            group += int(word)
            seen = True
            continue
        if word == _SCALE:
            group = (group or 1) * 1000
            total += group
            group = 0
            seen = True
            continue
        if word == _HUNDRED:
            group = (group or 1) * 100
            seen = True
            continue
        value = _CARDINALS.get(word)
        if value is None:
            return None
        group += value
        seen = True
    return total + group if seen else None


def _numeric(tok: Token, value: int, end: Token = None) -> Token:
    return Token(text=str(value), raw=str(value), index=tok.index,
                 is_number=True, value=value, char_start=tok.char_start,
                 char_end=(end or tok).char_end)


#: magnitude class of a cardinal surface -- what licenses one number-word to
#: extend the run another opened.  A composed numeral descends through the
#: classes ("dudek kvin" 25, "cent dudek kvin" 125) and a HUNDRED or SCALE
#: word may follow a lower class as its multiplier ("kvin cent" 500, "du
#: mil" 2000); two words of the SAME class never compose.
_UNIT_CLASS, _TEN_CLASS, _HUNDRED_CLASS, _SCALE_CLASS = 1, 2, 3, 4


def _magnitude(word: str) -> int:
    if word == _SCALE:
        return _SCALE_CLASS
    if word == _HUNDRED:
        return _HUNDRED_CLASS
    if word in _TENS or word == "dek":
        return _TEN_CLASS
    return _UNIT_CLASS


def _composes(previous: str, following: str) -> bool:
    prev, nxt = _magnitude(previous), _magnitude(following)
    if nxt > prev:
        return nxt in (_HUNDRED_CLASS, _SCALE_CLASS)
    return nxt < prev


def _cardinal_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Fold a well-formed run of spelled cardinals into one digit token."""
    out, i, n, changed = [], 0, len(tokens), False
    while i < n:
        t = tokens[i]
        if t.is_number or t.text not in _CARDINALS and t.text not in (
                _HUNDRED, _SCALE):
            out.append(t)
            i += 1
            continue
        j = i + 1
        while (j < n and not tokens[j].is_number
               and (tokens[j].text in _CARDINALS
                    or tokens[j].text in (_HUNDRED, _SCALE))
               and _composes(tokens[j - 1].text, tokens[j].text)):
            j += 1
        value = read_run(" ".join(tok.text for tok in tokens[i:j]))
        if value is None:
            out.append(t)
            i += 1
            continue
        out.append(_numeric(t, value, tokens[j - 1]))
        i, changed = j, True
    return reindex(out) if changed else tokens


def _day_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Fold the spelled day-of-month ordinal, tens compound included."""
    out, i, n, changed = [], 0, len(tokens), False
    while i < n:
        t = tokens[i]
        if (not t.is_number and t.text in _DAY_TENS and i + 1 < n
                and not tokens[i + 1].is_number):
            unit = _ORDINALS.get(tokens[i + 1].text, 0)
            if 1 <= unit <= 9:
                out.append(_numeric(t, _DAY_TENS[t.text] + unit,
                                    tokens[i + 1]))
                i, changed = i + 2, True
                continue
        if not t.is_number and t.text in _ORDINALS:
            out.append(_numeric(t, _ORDINALS[t.text]))
            i, changed = i + 1, True
            continue
        out.append(t)
        i += 1
    return reindex(out) if changed else tokens


def _digit_ordinal_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Glue a digit to its hyphenated "-a"/"-an" ordinal suffix fragment.

    Gated on ADJACENCY (a one-character gap -- the hyphen the tokenizer
    sheared -- between the digit and the fragment): "a"/"an" are otherwise
    ordinary short tokens (never real Esperanto words) that must not be
    swallowed when they are not glued to a digit at all.
    """
    out, i, n, changed = [], 0, len(tokens), False
    while i < n:
        t = tokens[i]
        nxt = tokens[i + 1] if i + 1 < n else None
        if (t.is_number and nxt is not None and not nxt.is_number
                and nxt.text in _DIGIT_ORD_SUFFIX
                and t.char_end is not None and nxt.char_start is not None
                and nxt.char_start - t.char_end == 1):
            out.append(replace(t, raw=t.raw + "-" + nxt.raw,
                               char_end=nxt.char_end))
            i, changed = i + 2, True
            continue
        out.append(t)
        i += 1
    return reindex(tuple(out)) if changed else tokens


def _compose(*passes: Callable) -> Callable:
    def run(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        for p in passes:
            tokens = p(tokens)
        return tokens
    return run


#: the digit-ordinal glue runs first so "15-a" is one token before the
#: day/cardinal passes (which only ever see already-digit tokens as opaque)
#: and before anything else could read the bare "15" as an hour. The
#: day/ordinal pass then leads the SPELLED forms so a compound ordinal
#: claims its tens before the plain cardinal fold could take that tens for
#: a bare number.
fold_eo = _compose(_digit_ordinal_rewrite, _day_rewrite, _cardinal_rewrite)
