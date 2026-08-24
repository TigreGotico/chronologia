# -*- coding: utf-8 -*-
"""Spelled-number folding pre-pass for Eastern Armenian.

The tokenizer only recognises *digit* runs as numbers; Armenian speech spells
them, so a maximal run of spelled number-words is folded into a single digit
:class:`~chronologia.extract.model.Token` and a ``NUM``/``DAY``/``HOUR``/``ORD``
slot then binds the same whether the writer typed ``3`` or the word.

Armenian counts in **tens, not twenties**.  There is no vigesimal grouping and
no coordinator anywhere in the system: 21..99 is written as ONE word, the tens
word immediately followed by the unit word, with a tens word ending in ``ը``
rewritten to ``ն`` before it joins -- ``տասը`` + ``ինը`` is ``տասնինը`` (19),
``քսան`` + ``մեկ`` is ``քսանմեկ`` (21).  Because the compound is a single
token, :data:`CARDINALS` is a flat surface map for the whole 0..99 range and
multi-token composition is needed only above it, where ``հարյուր`` (hundred)
and ``հազար`` (thousand) multiply the group standing before them and are
written as separate words (``երկու հարյուր`` == 200).

Ordinals suffix the whole cardinal: ``-երորդ``, or ``-ներորդ`` replacing a
final ``ը`` (``ինը`` -> ``իններորդ``, ``տասը`` -> ``տասներորդ``).  First to
fourth are suppletive.  This is the EASTERN Armenian series; Western Armenian
suffixes ``-երթ`` instead and is a different locale (``hyw``), not shipped here.

The forward temporal offset is not a separate marker word but the **ablative
case suffix on the unit noun** -- "in three days" is ``երեք օրից``, the
ablative of ``օր``.  :func:`_split_ablative_unit` splits that fused surface
back into the bare unit noun plus a ``ից`` marker token, so the ordinary
``NUM UNIT MARKER`` order reads it exactly as it reads the backward
``երեք օր առաջ``; ``marker_future.voc`` carries ``ից`` alongside the two
free-standing forward postpositions ``անց`` and ``հետո``.  The stem changes in
that paradigm are real (``ամիս`` -> ``ամսից``, ``տարի`` -> ``տարուց``), so the
map is curated per noun rather than derived by stripping a suffix.

Sources.  Cardinals 0..100, the hundreds, ``հազար``/``միլիոն`` and the
compounding rule for 11..99: en.wiktionary.org, ``Module:number_list/data/hy``
(the numeral table the Armenian entries themselves are generated from),
corroborated per word by the individual en.wiktionary.org entries for the
units, the teens and every tens word.  Ordinal suffixation and the suppletive
first..fourth: the same module, corroborated by the en.wiktionary.org entries
առաջին, երկրորդ, տասներորդ, քսաներորդ.  The ablative unit surfaces: Unicode
CLDR 47 ``cldr-dates-full/main/hy/dateFields.json``
(``relativeTime-type-future``), with decade/century/millennium from the
en.wiktionary.org declension table on each headword.  Nothing is delegated to
an external number back-end.
"""
from __future__ import annotations

from typing import Callable, Dict, Optional, Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex

#: 0..10, the atoms every larger numeral is built from.
UNITS: Dict[int, str] = {
    0: "զրո", 1: "մեկ", 2: "երկու", 3: "երեք", 4: "չորս", 5: "հինգ",
    6: "վեց", 7: "յոթ", 8: "ութ", 9: "ինը", 10: "տասը",
}

#: the tens.  ``տասը`` (10) heads the series for compounding purposes -- the
#: teens are formed by exactly the same rule as the twenties.
TENS: Dict[int, str] = {
    10: "տասը", 20: "քսան", 30: "երեսուն", 40: "քառասուն", 50: "հիսուն",
    60: "վաթսուն", 70: "յոթանասուն", 80: "ութսուն", 90: "իննսուն",
}

#: ``հարյուր`` multiplies the group before it and stays a separate word.
HUNDRED = "հարյուր"
#: the scale words, each multiplying the group before it and closing it.
SCALES: Dict[str, int] = {"հազար": 1000, "միլիոն": 1000000}


def _join(tens_word: str, unit_word: str) -> str:
    """The single-word compound of a tens and a unit ("քսան"+"մեկ")."""
    stem = tens_word[:-1] + "ն" if tens_word.endswith("ը") else tens_word
    return stem + unit_word


def _cardinal_words() -> Dict[str, int]:
    words = {word: value for value, word in UNITS.items()}
    for ten, ten_word in TENS.items():
        words[ten_word] = ten
        for unit in range(1, 10):
            words[_join(ten_word, UNITS[unit])] = ten + unit
    words[HUNDRED] = 100
    words.update(SCALES)
    return words


#: cardinal surface -> value, 0..99 plus the multiplier words.
CARDINALS: Dict[str, int] = _cardinal_words()


def _ordinal(cardinal: str) -> str:
    """The ordinal of a cardinal below 100: ``-ներորդ`` for a ``ը``-final
    surface, ``-երորդ`` otherwise."""
    if cardinal.endswith("ը"):
        return cardinal[:-1] + "ներորդ"
    return cardinal + "երորդ"


#: the ordinals no rule derives.
_SUPPLETIVE_ORDINALS: Dict[int, str] = {
    1: "առաջին", 2: "երկրորդ", 3: "երրորդ", 4: "չորրորդ",
}


def _ordinal_words() -> Dict[str, int]:
    words = {word: value for value, word in _SUPPLETIVE_ORDINALS.items()}
    for word, value in CARDINALS.items():
        if value in _SUPPLETIVE_ORDINALS or value > 100:
            continue
        words.setdefault(_ordinal(word), value)
    words[_ordinal(HUNDRED)] = 100
    return words


#: ordinal surface -> value, 1st..100th.
ORDINALS: Dict[str, int] = _ordinal_words()

#: The definite article is the suffix ``-ը`` after a consonant, ``-ն`` before a
#: following vowel; the spoken clock puts it on the hour numeral ("ժամը վեցն ու
#: կեսն է", "Ժամը յոթը քառորդ անց է").  Only consonant-final cardinals take it
#: -- a ``ը``-final cardinal ("ինը", "տասը") already ends in the article's own
#: vowel and its definite form is not attested here, so none is invented.
for _word, _value in list(CARDINALS.items()):
    if not _word.endswith("ը"):
        CARDINALS.setdefault(_word + "ը", _value)
        CARDINALS.setdefault(_word + "ն", _value)

#: ablative unit surface -> the bare nominative noun the fold restores.  The
#: ablative IS the forward-offset marker, so the split leaves a ``ից`` token
#: behind for ``marker_future.voc`` to bind.
_ABLATIVE_UNITS: Dict[str, str] = {
    "վայրկյանից": "վայրկյան",
    "րոպեից": "րոպե",
    "ժամից": "ժամ",
    "օրից": "օր",
    "շաբաթից": "շաբաթ",
    "ամսից": "ամիս",
    "տարուց": "տարի",
    "տասնամյակից": "տասնամյակ",
    "դարից": "դար",
    "հազարամյակից": "հազարամյակ",
}
#: the marker surface the split emits, the ablative's citation form.  Written
#: once here so it cannot drift from ``marker_future.voc``.
ABLATIVE_MARKER = "ից"


def _common_prefix(surface: str, noun: str) -> str:
    """The shared stem of an ablative surface and its nominative, which is
    where the original token's character extent is cut."""
    k = 0
    while k < len(surface) and k < len(noun) and surface[k] == noun[k]:
        k += 1
    return surface[:k]


def _split_ablative_unit(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Split an ablative-marked unit noun into ``UNIT`` + forward marker.

    Fires only on a whole token that is exactly one of the ten curated
    ablative surfaces, so an unrelated word merely ending in ``ից`` passes
    through untouched.  The two synthesised tokens split the original's
    character extent at the stem/suffix boundary.
    """
    out, changed = [], False
    for tok in tokens:
        noun = None if tok.is_number else _ABLATIVE_UNITS.get(tok.text)
        if noun is None:
            out.append(tok)
            continue
        cut = len(_common_prefix(tok.text, noun))
        start, end = tok.char_start, tok.char_end
        mid = (start + cut) if start is not None else None
        out.append(Token(text=noun, raw=tok.raw[:cut], index=tok.index,
                         is_number=False, char_start=start, char_end=mid,
                         cap=tok.cap))
        out.append(Token(text=ABLATIVE_MARKER, raw=tok.raw[cut:],
                         index=tok.index, is_number=False,
                         char_start=mid, char_end=end))
        changed = True
    return reindex(out) if changed else tokens


def read_run(text: str) -> Optional[int]:
    """Read the value of a joined run of Armenian cardinal surfaces.

    Additive over the 0..99 words; ``հարյուր`` multiplies the group
    accumulated so far and a scale word multiplies it and closes it into the
    running total.  Returns ``None`` when a word is not a cardinal, so the
    fold leaves the run alone rather than committing a partial reading.
    """
    total = 0
    group = 0
    seen = False
    for word in text.split():
        if word.isdigit():
            group += int(word)
            seen = True
            continue
        if word in SCALES:
            group = (group or 1) * SCALES[word]
            total += group
            group = 0
            seen = True
            continue
        if word == HUNDRED:
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


#: the magnitude class of a cardinal surface, which is what licenses one word
#: to continue the run another opened.  A composed numeral descends through the
#: classes: a SCALE or HUNDRED word may follow a lower one as its multiplier
#: ("երկու հարյուր"), and a lower class may follow a higher one as an additive
#: remainder ("երկու հազար քսանչորս").  Two words of the same class never
#: compose, which keeps two adjacent numerals from collapsing into one.
_BELOW_HUNDRED, _HUNDRED_CLASS, _SCALE_CLASS = 1, 2, 3


def _magnitude(word: str) -> int:
    if word in SCALES:
        return _SCALE_CLASS
    if word == HUNDRED:
        return _HUNDRED_CLASS
    return _BELOW_HUNDRED


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
        if t.is_number or t.text not in CARDINALS:
            out.append(t)
            i += 1
            continue
        j, previous = i + 1, t.text
        while j < n:
            if (tokens[j].is_number or tokens[j].text not in CARDINALS
                    or not _composes(previous, tokens[j].text)):
                break
            previous, j = tokens[j].text, j + 1
        value = read_run(" ".join(tok.text for tok in tokens[i:j]))
        if value is None:
            out.append(t)
            i += 1
            continue
        out.append(_numeric(t, value, tokens[j - 1]))
        i, changed = j, True
    return reindex(out) if changed else tokens


def _ordinal_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Fold a spelled ordinal, which is always a single word."""
    out, changed = [], False
    for t in tokens:
        if not t.is_number and t.text in ORDINALS:
            out.append(_numeric(t, ORDINALS[t.text]))
            changed = True
            continue
        out.append(t)
    return reindex(out) if changed else tokens


def _compose(*passes: Callable) -> Callable:
    def run(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        for p in passes:
            tokens = p(tokens)
        return tokens
    return run


fold_hy = _compose(_split_ablative_unit, _ordinal_rewrite, _cardinal_rewrite)
