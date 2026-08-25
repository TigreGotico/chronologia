# -*- coding: utf-8 -*-
"""Spelled-number folding for Swahili, where a numeral agrees with its noun.

Swahili cardinals split in two.  Six of them are inherited Bantu stems that
take a concord prefix from the class of the noun they count -- *-wili*,
*-tatu*, *-nne*, *-tano*, *-nane* and *-moja* -- and the other four are loans
from Arabic
that never inflect at all: *sita*, *saba*, *tisa*, *kumi*.  So five days is
"siku tano" but five years is "miaka mitano": the same value, a different word,
chosen by the noun standing in front of it.

The two concords this locale needs are the two its units fall into.  Class 9/10
(sekunde, dakika, saa, siku, wiki) absorbs the nasal prefix to nothing, so the
stem surfaces bare -- mbili, tatu, nne, tano, nane.  Class 3/4 (mwaka/miaka,
mwezi/miezi) prefixes *mi-* in the plural, giving miwili, mitatu, minne,
mitano, minane.  Both sets are read, because a writer picks the one their own
noun demands and both are correct Swahili for the same number.

The count is not folded into the noun and the noun is not folded into the
count.  This is the mirror image of the agglutinative locales: an N-class noun
never changes shape at all, so the entire number lives in the numeral, and a
class 3/4 noun changes only between one and more-than-one, so it never carries
a value either.  The fold therefore reads numerals only, and the unit surface
reaches the grammar untouched.

Composition runs largest first, opposite to the Germanic and Slavic direction:
the scale word LEADS its multiplier -- "elfu mbili" is two thousand, "mia tatu"
three hundred -- and the components descend in magnitude, optionally linked by
*na*.  "elfu mbili mia tatu ishirini na tano" is 2325.  *na* is also the
ordinary word for "and", so it bridges only where a numeral genuinely
continues: the component it introduces must be strictly smaller than the one
before it.  "Jumatatu na Ijumaa" and "kati ya saa mbili na dakika tano" are
left alone, because neither side of the connector is a smaller component of one
number.

Sources: en.wiktionary.org, ``Module:number_list/data/sw`` (the
machine-readable numeral table: the base stems 1-10, the tens
ishirini..tisini, mia and elfu, and the "ishirini na tano" composition);
en.wiktionary.org, Appendix:Swahili_numbers, whose rule is that every stem
except -moja declines in the plural only; en.wiktionary.org,
Appendix:Swahili_noun_classes for the
class 3/4 *mi-* and class 9/10 zero concords; Unicode CLDR 47, sw
``dateFields``, whose "miaka {0} iliyopita" beside "siku {0} zilizopita" shows
the same split from the calendar side.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex

#: The Arabic loans.  These never take a concord prefix, in any class.
_INVARIANT: Dict[str, int] = {
    "sita": 6, "saba": 7, "tisa": 9, "kenda": 9,
}

#: The agreeing stems as class 9/10 surfaces them -- bare, the N- prefix being
#: absorbed.  moja is the one stem that does not decline for plural at all.
_CLASS_9: Dict[str, int] = {
    "moja": 1, "mbili": 2, "tatu": 3, "nne": 4, "tano": 5, "nane": 8,
}

#: The same stems under the class 3/4 plural concord *mi-*.
_CLASS_3: Dict[str, int] = {
    "miwili": 2, "mitatu": 3, "minne": 4, "mitano": 5, "minane": 8,
}

#: Units below ten, every class-surface of them.
_UNITS: Dict[str, int] = {**_CLASS_9, **_CLASS_3, **_INVARIANT}

_TENS: Dict[str, int] = {
    "kumi": 10, "ishirini": 20, "thelathini": 30, "arobaini": 40,
    "hamsini": 50, "sitini": 60, "sabini": 70, "themanini": 80, "tisini": 90,
}

#: scale word -> its factor.  The word LEADS its multiplier.
_SCALES: Dict[str, int] = {"mia": 100, "elfu": 1000}

#: the connector, which is also the ordinary "and".
_JOINER = "na"

_RUN_WORDS = (frozenset(_UNITS) | frozenset(_TENS) | frozenset(_SCALES)
              | {_JOINER})

#: magnitude rank of a component, so a run reads only while it descends.
_RANK_UNIT, _RANK_TENS = 0, 1


def _rank_of_scale(factor: int) -> int:
    return 2 if factor == 100 else 3


def read_run(words: Tuple[str, ...]) -> Optional[int]:
    """The value of a run of numeral surfaces, or ``None`` if it reads none.

    Components are read largest first and must strictly descend, so a genuine
    numeral ("mia tatu ishirini na tano") reads and a repetition that cannot be
    one number ("tatu tano") does not.
    """
    total = 0
    last_rank: Optional[int] = None
    i, n = 0, len(words)
    seen = False
    while i < n:
        word = words[i]
        if word == _JOINER:
            # a connector is only ever internal, and only between components
            if not seen or i + 1 >= n:
                return None
            i += 1
            continue
        factor = _SCALES.get(word)
        if factor is not None:
            rank = _rank_of_scale(factor)
            mult = 1
            if i + 1 < n and words[i + 1] in _UNITS:
                mult = _UNITS[words[i + 1]]
                i += 1
            value = factor * mult
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
    construction ("saa mbili na dakika tano" -- the connector is the range's,
    not the number's) yields the longest genuine numeral and leaves the rest
    alone.
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


def fold_sw(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Fold every Swahili numeral run, in whichever class concord it wears."""
    return _run_fold(tokens)
