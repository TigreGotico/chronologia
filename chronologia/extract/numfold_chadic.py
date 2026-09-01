# -*- coding: utf-8 -*-
"""Spelled-number folding for Hausa.

Hausa builds a number out of components read largest first, joined by *da*.
A scale word LEADS its multiplier -- *ɗari tara* is nine hundred, *dubu biyu*
two thousand -- and the teens are *goma sha* plus a unit, *goma* being ten and
*sha* the linker that carries the addition.  After a larger component the
*goma* is normally dropped and *sha* stands alone, so 2015 is written *dubu
biyu da sha biyar*.

Both readings are attested with their own arithmetic beside them.  Hausa
Wikipedia habitually glosses a spelled number with the digits it means, which
makes the encyclopedia its own worked-example oracle: *goma sha biyar (15)*,
*ashirin da shida (26)*, *dubu ɗaya da ɗari tara da goma sha huɗu (1914)*,
*dubu ɗaya da ɗari takwas da ashirin da biyu (1822)*, *dubu biyu da sha biyar
(2015)*.  Those five fix the composition rule completely: descending
magnitude, *da* between components, the scale word before its multiplier.

*da* is also the ordinary word for "and", so it bridges only where a numeral
genuinely continues -- the component it introduces must rank strictly below
the one before it.  "tsakanin Litinin da Jumaʼa" is left alone, because
neither side is a smaller component of one number.

The tens have two registers.  The inherited series multiplies ten
(*gomiya biyu* = twenty) and the Arabic loans (*ashirin*, *talatin*,
*arbaʼin* ...) do not inflect at all; both are read, because a writer picks
one and either is correct Hausa for the same value.

Sources: en.wiktionary.org, ``Module:number_list/data/ha`` for the base
numerals, the two tens registers, ɗari and dubu, each value cross-checked
against its own lemma entry; ha.wikipedia.org for the composition rule and
every worked example above.  The module's tone- and length-marked citation
forms (*bìyar̃*, *gōmà*, *àshìr̃in*) are folded to the plain spelling ordinary
written Hausa uses, which is the spelling the lemma titles themselves carry.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex

_UNITS: Dict[str, int] = {
    "sifiri": 0, "ɗaya": 1, "daya": 1, "biyu": 2, "uku": 3,
    "huɗu": 4, "hudu": 4, "fuɗu": 4, "fudu": 4,
    "biyar": 5, "shida": 6, "bakwai": 7, "takwas": 8, "tara": 9,
}

#: ten, and the two registers of the tens above it.  The Arabic loans are
#: invariant; the inherited series is gomiya (a multiple of ten) plus a unit,
#: which the reader below assembles from its two words.
_TEN = "goma"
_GOMIYA = "gomiya"
_TENS: Dict[str, int] = {
    "ashirin": 20, "talatin": 30, "arba'in": 40, "hamsin": 50,
    "sittin": 60, "saba'in": 70, "tamanin": 80,
    "casa'in": 90, "cassa'in": 90, "tis'in": 90,
}

#: the teen linker: goma sha biyar = 15, and sha biyar alone after a larger
#: component.
_SHA = "sha"

#: scale word -> its factor.  The word leads its multiplier.
_SCALES: Dict[str, int] = {"ɗari": 100, "dari": 100, "dubu": 1000, "alif": 1000}

#: the connector, which is also the ordinary "and".
_JOINER = "da"

_RUN_WORDS = (frozenset(_UNITS) | frozenset(_TENS) | frozenset(_SCALES)
              | {_TEN, _GOMIYA, _SHA, _JOINER})

_RANK_UNIT, _RANK_TEEN, _RANK_TENS, _RANK_HUNDRED, _RANK_THOUSAND = range(5)


def read_run(words: Tuple[str, ...]) -> Optional[int]:
    """The value of a run of numeral surfaces, or ``None`` if it reads none."""
    total = 0
    last_rank: Optional[int] = None
    i, n = 0, len(words)
    seen = False
    while i < n:
        word = words[i]
        if word == _JOINER:
            if not seen or i + 1 >= n:
                return None
            i += 1
            continue
        factor = _SCALES.get(word)
        if factor is not None:
            rank = _RANK_HUNDRED if factor == 100 else _RANK_THOUSAND
            mult = 1
            if i + 1 < n and words[i + 1] in _UNITS:
                mult = _UNITS[words[i + 1]]
                i += 1
            value = factor * mult
        elif word == _GOMIYA:
            # the inherited tens: gomiya biyu = twenty
            if i + 1 >= n or words[i + 1] not in _UNITS:
                return None
            rank, value = _RANK_TENS, 10 * _UNITS[words[i + 1]]
            i += 1
        elif word == _TEN:
            # goma sha X is a teen; a bare goma is ten
            if i + 1 < n and words[i + 1] == _SHA:
                if i + 2 >= n or words[i + 2] not in _UNITS:
                    return None
                rank, value = _RANK_TEEN, 10 + _UNITS[words[i + 2]]
                i += 2
            else:
                rank, value = _RANK_TEEN, 10
        elif word == _SHA:
            # sha carries the teen with the goma dropped, both after a larger
            # component ("dubu biyu da sha biyar" = 2015) and on its own
            # ("ranar sha ɗaya", the eleventh day).  It is never a number
            # without the unit that follows it.
            if i + 1 >= n or words[i + 1] not in _UNITS:
                return None
            rank, value = _RANK_TEEN, 10 + _UNITS[words[i + 1]]
            i += 1
        elif word in _TENS:
            rank, value = _RANK_TENS, _TENS[word]
        elif word in _UNITS:
            rank, value = _RANK_UNIT, _UNITS[word]
        else:
            return None
        if last_rank is not None and rank >= last_rank:
            return None
        total += value
        last_rank = rank
        seen = True
        i += 1
    return total if seen else None


def _numeric(tok: Token, value: int, end: Token) -> Token:
    return Token(text=str(value), raw=str(value), index=tok.index,
                 is_number=True, value=value, char_start=tok.char_start,
                 char_end=end.char_end)


def _run_fold(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Fold each maximal span the numeral reader reads as a single number.

    The span is grown as far as the numeral lexicon reaches and then shortened
    a token at a time until it reads, so a run whose tail belongs to another
    construction yields the longest genuine numeral and leaves the rest alone.
    """
    out: List[Token] = []
    i, n, changed = 0, len(tokens), False
    while i < n:
        t = tokens[i]
        if t.is_number or t.text not in _RUN_WORDS or t.text == _JOINER:
            out.append(t)
            i += 1
            continue
        end = i + 1
        while (end < n and not tokens[end].is_number
               and tokens[end].text in _RUN_WORDS):
            end += 1
        value = None
        while end > i:
            value = read_run(tuple(tok.text for tok in tokens[i:end]))
            if value is not None:
                break
            end -= 1
        if end == i:
            out.append(t)
            i += 1
            continue
        out.append(_numeric(t, value, tokens[end - 1]))
        i, changed = end, True
    return reindex(out) if changed else tokens


def fold_ha(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Fold every Hausa numeral run."""
    return _run_fold(tokens)
