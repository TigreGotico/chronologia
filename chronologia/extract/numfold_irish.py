# -*- coding: utf-8 -*-
"""Spelled-number folding pre-pass for Irish.

The tokenizer only recognises *digit* runs as numbers; Irish speech spells
them, so a maximal run of spelled number-words is folded into a single digit
:class:`~chronologia.extract.model.Token` and a ``NUM``/``DAY``/``HOUR``/``ORD``
slot then binds the same whether the writer typed ``3`` or the word.

Irish keeps three numeral word-sets and the choice between them is
grammatical, not stylistic.  The **conjunctive** set counts a noun directly
and mutates it -- ``dhá`` (2) lenites, ``trí``..``sé`` (3-6) leave a
consonant bare and prefix ``h`` to a vowel, ``seacht``..``deich`` (7-10)
eclipse -- and it is the set every duration and date phrase uses.  The
**disjunctive** set is the abstract counting series, each word carried by the
particle ``a`` (``a haon``, ``a trí``, ``a hocht``), and it is what a clock
hour takes.  The **personal** set counts human beings and has no temporal
use, so it is absent here.

Both temporal sets are read, because both reach a temporal slot: this module
is the numeral half of that split.  The mutation the conjunctive numerals
impose falls on the *noun*, and every mutated noun surface is enumerated in
the locale's own ``unit_*.voc`` -- there is no mutation machinery in the
engine, and none is needed.

Sources.  The cardinal, ordinal, personal and attributive series 1-30 plus
the tens, hundred and thousand: en.wiktionary.org, "Appendix:Irish numerals"
(the rendered table, fetched through the MediaWiki ``action=parse`` API),
cross-checked word by word against each numeral's own en.wiktionary.org
lemma entry.  Nothing is delegated to an external number back-end.
"""
from __future__ import annotations

from typing import Callable, Dict, Optional, Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex

#: The conjunctive ("counting with a noun") series, the one a duration or a
#: date uses.  The mutation each imposes on the noun after it is stated
#: beside it and realised in the locale's unit vocabulary, not here.
CONJUNCTIVE: Dict[int, str] = {
    1: "aon",       # no mutation
    2: "dhá",       # lenition:      dhá bhliain
    3: "trí",       # bare / h-:     trí bliana, trí huaire
    4: "ceithre",
    5: "cúig",
    6: "sé",
    7: "seacht",    # eclipsis:      seacht mbliana, seacht n-uaire
    8: "ocht",
    9: "naoi",
    10: "deich",
}

#: The disjunctive series, which a clock hour takes behind the particle "a".
#: One and eight carry the h-prothesis that particle imposes, so both the
#: bare and the prefixed surface are read.
DISJUNCTIVE: Dict[int, Tuple[str, ...]] = {
    0: ("náid", "neamhní"),
    1: ("aon", "haon"),
    2: ("dó",),
    3: ("trí",),
    4: ("ceathair",),
    5: ("cúig",),
    6: ("sé",),
    7: ("seacht",),
    8: ("ocht", "hocht"),
    9: ("naoi",),
    10: ("deich",),
}

#: The teen suffix.  Eleven to nineteen are "<unit> déag", the lenited
#: "dhéag" appearing after "dó".
_DEAG = ("déag", "dhéag")

#: The tens.  The vigesimal alternatives the same table lists ("dhá
#: fhichead", "trí scór", "leathchéad") are two-word idioms and are not read.
TENS: Dict[int, Tuple[str, ...]] = {
    20: ("fiche",), 30: ("tríocha",), 40: ("daichead", "ceathracha"),
    50: ("caoga",), 60: ("seasca",), 70: ("seachtó",), 80: ("ochtó",),
    90: ("nócha",),
}

#: "céad" (hundred).  Its lenited surface "chéad" is deliberately NOT read:
#: that spelling is the ordinal "first" after the article, and the one source
#: that states a mutation rule for "céad" as a numeral is contradicted by the
#: attested unmutated "céad bliain", so the two uses are kept apart by
#: reading only the bare surface as the number.
_HUNDRED = ("céad",)
_SCALE: Dict[str, int] = {"míle": 1000, "milliún": 1000000,
                          "billiún": 1000000000}
#: the coordinators a compound numeral may carry ("fiche a haon",
#: "aonú is fiche").
_JOINERS = frozenset({"a", "is", "agus"})


# ---------------------------------------------------------------------------
# Ordinals.  Every ordinal but "dara" (2nd) is the cardinal stem plus "-ú".
# The teens append "déag" and the twenties are "<ordinal> is fiche", both
# straight off the numerals appendix.
#
# Two values are deliberately absent.  "céad" is at once "hundred" and
# "first", so claiming it as an ordinal would read "céad bliain" (a hundred
# years) as a first-of-something.  "ceathrú" is at once "fourth" and the
# quarter of an hour the clock speaks ("ceathrú tar éis a trí"), so claiming
# it as an ordinal would rewrite the quarter out of every clock reading.
# Fourteenth ("ceathrú déag") goes with the fourth.
# ---------------------------------------------------------------------------
_ORDINAL_UNITS: Dict[str, int] = {
    "aonú": 1, "dara": 2, "dóú": 2, "tríú": 3, "cúigiú": 5, "séú": 6,
    "seachtú": 7, "ochtú": 8, "naoú": 9, "deichiú": 10,
}
_ORDINAL_TENS: Dict[str, int] = {"fichiú": 20, "tríochadú": 30}


# ---------------------------------------------------------------------------
# The run reader
# ---------------------------------------------------------------------------
CARDINALS: Dict[str, int] = {}
for _v, _w in CONJUNCTIVE.items():
    CARDINALS[_w] = _v
for _v, _ws in DISJUNCTIVE.items():
    for _w in _ws:
        CARDINALS.setdefault(_w, _v)
for _v, _ws in TENS.items():
    for _w in _ws:
        CARDINALS[_w] = _v
for _w in _HUNDRED:
    CARDINALS[_w] = 100
CARDINALS.update(_SCALE)

#: the magnitude class of a cardinal surface, which is what licenses one
#: number-word to continue the run another opened.  A composed Irish numeral
#: descends through the classes ("fiche a haon"), and a HUNDRED or SCALE word
#: may follow a lower one as its multiplier ("trí míle").  Two words of the
#: same class never compose, which keeps "deich nóiméad tar éis a hocht" from
#: collapsing once the unit noun between the counts is out of the way.
_UNIT_CLASS, _TEEN_CLASS, _TEN_CLASS, _HUNDRED_CLASS, _SCALE_CLASS = 1, 2, 3, 4, 5

_TENS_SURFACES = frozenset(w for ws in TENS.values() for w in ws)


def _magnitude(word: str) -> int:
    if word in _SCALE:
        return _SCALE_CLASS
    if word in _HUNDRED:
        return _HUNDRED_CLASS
    if word in _TENS_SURFACES:
        return _TEN_CLASS
    if word in _DEAG:
        return _TEEN_CLASS
    return _UNIT_CLASS


def _composes(previous: str, following: str) -> bool:
    prev, nxt = _magnitude(previous), _magnitude(following)
    if following in _DEAG:
        return prev == _UNIT_CLASS
    if nxt > prev:
        return nxt in (_HUNDRED_CLASS, _SCALE_CLASS)
    return nxt < prev


def read_run(text: str) -> Optional[int]:
    """Read the value of a joined run of Irish number-word surfaces.

    Additive over units and tens; "déag" adds the ten of a teen, "céad"
    multiplies the group accumulated so far and a scale word multiplies it and
    closes it into the running total.  A coordinator contributes nothing.
    Returns ``None`` when a word is not a number-word, so the fold leaves the
    run alone rather than committing a partial reading.
    """
    total = 0
    group = 0
    seen = False
    for word in text.split():
        if word in _JOINERS:
            continue
        if word.isdigit():
            group += int(word)
            seen = True
            continue
        if word in _DEAG:
            group += 10
            seen = True
            continue
        if word in _SCALE:
            group = (group or 1) * _SCALE[word]
            total += group
            group = 0
            seen = True
            continue
        if word in _HUNDRED:
            group = (group or 1) * 100
            seen = True
            continue
        value = CARDINALS.get(word)
        if value is None:
            return None
        group += value
        seen = True
    return total + group if seen else None


def _numeric(tok: Token, value: int, end: Token = None) -> Token:
    return Token(text=str(value), raw=str(value), index=tok.index,
                 is_number=True, value=value, char_start=tok.char_start,
                 char_end=(end or tok).char_end)


def _cardinal_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Fold a well-formed run of spelled cardinals into one digit token."""
    out, i, n, changed = [], 0, len(tokens), False
    while i < n:
        t = tokens[i]
        if t.is_number or t.text not in CARDINALS:
            out.append(t)
            i += 1
            continue
        j, previous = i + 1, t.text
        while j < n:
            # a coordinator only continues the run when a composing
            # number-word follows it
            k = j + 1 if tokens[j].text in _JOINERS else j
            if (k >= n or tokens[k].is_number
                    or (tokens[k].text not in CARDINALS
                        and tokens[k].text not in _DEAG)
                    or not _composes(previous, tokens[k].text)):
                break
            previous, j = tokens[k].text, k + 1
        value = read_run(" ".join(tok.text for tok in tokens[i:j]))
        if value is None:
            out.append(t)
            i += 1
            continue
        out.append(_numeric(t, value, tokens[j - 1]))
        i, changed = j, True
    return reindex(out) if changed else tokens


def _ordinal_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Fold a spelled ordinal, its teen and its twenties compound included."""
    out, i, n, changed = [], 0, len(tokens), False
    while i < n:
        t = tokens[i]
        unit = None if t.is_number else _ORDINAL_UNITS.get(t.text)
        if unit is not None:
            if i + 1 < n and tokens[i + 1].text in _DEAG:
                out.append(_numeric(t, unit + 10, tokens[i + 1]))
                i, changed = i + 2, True
                continue
            if (i + 2 < n and tokens[i + 1].text in _JOINERS
                    and _ORDINAL_TENS.get(tokens[i + 2].text) == 20):
                out.append(_numeric(t, unit + 20, tokens[i + 2]))
                i, changed = i + 3, True
                continue
            out.append(_numeric(t, unit))
            i, changed = i + 1, True
            continue
        if not t.is_number and t.text in _ORDINAL_TENS:
            out.append(_numeric(t, _ORDINAL_TENS[t.text]))
            i, changed = i + 1, True
            continue
        out.append(t)
        i += 1
    return reindex(out) if changed else tokens


def _compose(*passes: Callable) -> Callable:
    def run(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        for p in passes:
            tokens = p(tokens)
        return tokens
    return run


fold_ga = _compose(_ordinal_rewrite, _cardinal_rewrite)
