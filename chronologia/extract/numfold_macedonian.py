# -*- coding: utf-8 -*-
"""Spelled-number folding for Macedonian, and the two year adverbs.

Macedonian has no case system, so the declined-ordinal machinery the
case-marking Slavic locales need has nothing to read here: a numeral stands in
one shape wherever it occurs and the noun it counts takes its own count form.
What the language does need is a numeral reader of its own, because the
composition rule is narrow and the connector it composes with is the same word
the clock uses.

и ("and") joins the tens word of a compound numeral to its unit and nothing
else -- дваесет и еден is 21 -- while the very same и is the additive direction
word of the clock.  Allowing it to bridge anything wider would collapse
"дваесет и еден и педесет" (21:50) into a single numeral and lose the minute,
so a bridge is taken only when the value so far is a bare multiple of ten from
twenty to ninety and the word after the connector is a unit below ten.  Every
other adjacency is refused outright, with one exception: a numeral standing
immediately before илјада/илјади multiplies it (две илјади == 2000).

Cardinal one is gender-marked even standing bare -- еден before a masculine
noun, една before a feminine one, едно before a neuter one -- and all three
spell the same value, so all three are read.

лани (last year) and догодина (next year) are single words where every other
unit says its relative marker and its noun apart, so each is rewritten into the
two tokens the ordinary relative-period grammar already reads.  The rewrite is
the same shape :mod:`chronologia.extract.numfold_maltese` uses to split a dual
noun into a count and a plural.

Sources: en.wiktionary.org, ``Module:number_list/data/mk`` (the
machine-readable numeral table: cardinals per number, the compound spelling
"дваесет и еден", the hundred words and "две илјади"); en.wiktionary.org, еден,
whose adjectival declension gives една and едно; en.wiktionary.org, лани
("last year") and догодина ("next year"); Unicode CLDR 47, mk ``dateFields``,
whose year field carries лани and догодина as its relative-type--1 and
relative-type-1.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex

_UNITS: Dict[str, int] = {
    "нула": 0,
    "еден": 1, "една": 1, "едно": 1,
    "два": 2, "две": 2,
    "три": 3, "четири": 4, "пет": 5, "шест": 6, "седум": 7, "осум": 8,
    "девет": 9,
}

_TEENS: Dict[str, int] = {
    "десет": 10, "единаесет": 11, "дванаесет": 12, "тринаесет": 13,
    "четиринаесет": 14, "петнаесет": 15, "шеснаесет": 16, "седумнаесет": 17,
    "осумнаесет": 18, "деветнаесет": 19,
}

_TENS: Dict[str, int] = {
    "дваесет": 20, "триесет": 30, "четириесет": 40, "педесет": 50,
    "шеесет": 60, "седумдесет": 70, "осумдесет": 80, "деведесет": 90,
}

#: the hundred words carry their own multiplier; none is composed here.
_HUNDREDS: Dict[str, int] = {
    "сто": 100, "двесте": 200, "триста": 300, "четиристотини": 400,
    "петстотини": 500, "шестотини": 600, "седумстотини": 700,
    "осумстотини": 800, "деветстотини": 900,
}

_THOUSAND: Dict[str, int] = {"илјада": 1000, "илјади": 1000}

_SIMPLE: Dict[str, int] = {**_UNITS, **_TEENS, **_TENS, **_HUNDREDS}

#: the connector that joins a tens word to its unit, and the clock's direction
#: word.  Which of the two it is, is decided by :func:`read_run`.
_JOINER = "и"

#: single-word year deictics -> the marker + noun pair the grammar reads.
_YEAR_ADVERB: Dict[str, Tuple[str, str]] = {
    "лани": ("минатата", "година"),
    "догодина": ("следната", "година"),
}


def _numeric(tok: Token, value: int, end: Token = None) -> Token:
    return Token(text=str(value), raw=str(value), index=tok.index,
                 is_number=True, value=value, char_start=tok.char_start,
                 char_end=(end or tok).char_end)


def _year_adverb_split(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Rewrite лани/догодина as their relative marker plus the year noun."""
    out: List[Token] = []
    changed = False
    for t in tokens:
        pair = None if t.is_number else _YEAR_ADVERB.get(t.text)
        if pair is None:
            out.append(t)
            continue
        marker, noun = pair
        out.append(Token(text=marker, raw=t.raw, index=t.index,
                         char_start=t.char_start, char_end=t.char_start,
                         cap=t.cap, prev_cap=t.prev_cap))
        out.append(Token(text=noun, raw="", index=t.index,
                         char_start=t.char_start, char_end=t.char_end))
        changed = True
    return reindex(tuple(out)) if changed else tokens


def read_run(words: Tuple[str, ...]) -> Optional[int]:
    """The value of a run of numeral surfaces, or ``None`` if it reads none."""
    total = 0
    current: Optional[int] = None
    i, n = 0, len(words)
    while i < n:
        word = words[i]
        if word == _JOINER:
            if (current is None or current not in _TENS.values()
                    or i + 1 >= n or _UNITS.get(words[i + 1], 0) not in
                    range(1, 10)):
                return None
            current += _UNITS[words[i + 1]]
            i += 2
            continue
        if word in _THOUSAND:
            current = (current or 1) * 1000
            total += current
            current = None
            i += 1
            continue
        value = _SIMPLE.get(word)
        if value is None or current is not None:
            return None
        current = value
        i += 1
    if current is None and total == 0:
        return None
    return total + (current or 0)


_RUN_WORDS = frozenset(_SIMPLE) | frozenset(_THOUSAND) | {_JOINER}


def _run_fold(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Fold each maximal span the numeral reader reads as a single number.

    The span is grown as far as the numeral lexicon reaches and then shortened
    a token at a time until it reads, so a run whose tail belongs to another
    construction ("девет и пол" -- the connector is the clock's, not the
    number's) yields the longest genuine numeral and leaves the rest alone.
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


def fold_mk(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Split the year adverbs, then fold every numeral run they leave."""
    return _run_fold(_year_adverb_split(tokens))
