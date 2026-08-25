# -*- coding: utf-8 -*-
"""Spelled-number folding for Maltese -- construct state, the dual, and ``-il``.

Maltese counts with a Semitic numeral system wearing Latin orthography, and
three of its features have to be read here rather than left to a generic
cardinal table.

**Construct state.**  Two through ten have a free-standing form used when the
number stands alone ("tnejn", "tlieta", "għaxra") and a distinct ATTRIBUTIVE
form used immediately before the noun being counted ("żewġ ijiem", "tliet
snin", "għaxar minuti").  The attributive form itself splits in two: a short
form before an ordinary noun and a long form, ending in ``-t``, before a noun
whose onset is a consonant cluster ("żewġt itfal", "tlitt elef").  Both are
listed; which one a writer picked is the noun's business, not the number's,
and both spell the same value.

**The ``-il`` linker.**  From eleven upward the counted noun reverts to the
SINGULAR and is linked by ``-il`` written onto the numeral ("ħdax-il jum",
"tnax-il elf").  The tokenizer shears the hyphen, so the linker arrives as its
own ``il`` token; inside a numeral run it is transparent ("tnax-il elf" ==
12000) and everywhere else the grammar's optional ``il`` connector absorbs it.

**The dual.**  Five time nouns mark "exactly two" with an ``-ejn`` suffix that
is neither singular nor plural -- jumejn, ġimagħtejn, sagħtejn, xahrejn,
sentejn -- and a matcher that knows only singular and plural does not see a
count in them at all.  Each is split into a synthetic ``2`` plus the ordinary
plural the unit vocabulary already ships, the same rewrite
:mod:`chronologia.extract.numfold_semitic` performs for Hebrew's יומיים.
Minute, second and century take NO dual: they are Romance loans (minuta,
sekonda, seklu, cf. Italian minuto/secondo/secolo) that never acquired Semitic
dual morphology, so no dual is invented for them.  The same ``-ejn`` suffix
recurs inside the number system itself -- mitejn (200) is the dual of mija,
elfejn (2000) the dual of elf -- and those two are read straight off the
cardinal table.

Composition is deliberately narrow.  ``u`` ("and") joins a unit to a TENS word
and nothing else ("ħamsa u għoxrin" == 25), because the very same ``u`` is the
additive direction word of the clock: were it allowed to join two unit
numerals, "is-sitta u għaxra" (06:10) would collapse into a single sixteen and
the minute would vanish.  A hundred or thousand word multiplies the
attributive numeral in front of it ("tliet mija" == 300, "għaxart elef" ==
10000, "mitt elf" == 100000).

Three cardinals are homographs of a weekday name once the definite article is
prefixed: it-Tnejn (Monday) against tnejn (2), it-Tlieta (Tuesday) against
tlieta (3), l-Erbgħa (Wednesday) against erbgħa (4).  A numeral standing
directly after its own article in one of those three pairs is left unfolded so
the weekday vocabulary can claim it; the cost is that two, three and four
o'clock cannot be spelled with the article, which is refused rather than
guessed at.

The attributive five through ten (ħames, sitt, seba', tmien, disa', għaxar)
are also, letter for letter, the ordinals fifth through tenth.  That homograph
costs nothing here: both slots the surface can fill -- a count and a rank --
want the same integer, and the surrounding construction decides which it read,
exactly as the Filipino ``ika-`` fold already relies on.

Sources: en.wiktionary.org, ``Module:number_list/data/mt`` (the machine-readable
numeral table, whose ``attr_cardinal`` entries carry the short and long
attributive forms per number and state the ``-il`` suffix for 11-19);
en.wiktionary.org, "Appendix:Maltese numerals"; en.wiktionary.org, per-lemma
entries for jum, ġimgħa, siegħa, xahar and sena, whose ``mt-noun`` templates
carry the ``d=`` dual parameter, and for minuta, sekonda and seklu, which carry
none; Unicode CLDR 47, ``mt`` ``dateFields.json``, whose "two" plural category
spells every relative-time pattern with the dual noun.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex

#: free-standing cardinals -- the form a number takes with no noun after it.
_ABSOLUTE: Dict[str, int] = {
    "żero": 0,
    "wieħed": 1, "waħda": 1,
    "tnejn": 2, "tlieta": 3, "erbgħa": 4, "ħamsa": 5, "sitta": 6,
    "sebgħa": 7, "tmienja": 8, "disgħa": 9, "għaxra": 10,
    "ħdax": 11, "tnax": 12, "tlettax": 13, "erbatax": 14, "ħmistax": 15,
    "sittax": 16, "sbatax": 17, "tmintax": 18, "dsatax": 19,
    "mitejn": 200, "elfejn": 2000,
}

#: attributive (construct-state) cardinals, short form then long ``-t`` form.
#: ġiex/ġiext are the colloquial rival of żewġ/żewġt for two, listed by the
#: same source.  The apostrophe of erba', seba' and disa' is dropped by the
#: tokenizer, so the keys carry the bare letters.
_ATTRIBUTIVE: Dict[str, int] = {
    "żewġ": 2, "żewġt": 2, "ġiex": 2, "ġiext": 2,
    "tliet": 3, "tlitt": 3,
    "erba": 4, "erbat": 4,
    "ħames": 5, "ħamest": 5,
    "sitt": 6,
    "seba": 7, "sebat": 7,
    "tmien": 8, "tmint": 8,
    "disa": 9, "disat": 9,
    "għaxar": 10, "għaxart": 10,
}

#: ordinals one through four.  Fifth through tenth are spelled exactly like
#: the attributive cardinals above and are read by that table.
_ORDINAL: Dict[str, int] = {"ewwel": 1, "tieni": 2, "tielet": 3, "raba": 4}

_TENS: Dict[str, int] = {
    "għoxrin": 20, "tletin": 30, "erbgħin": 40, "ħamsin": 50, "sittin": 60,
    "sebgħin": 70, "tmenin": 80, "disgħin": 90,
}

#: hundred and thousand words.  mija is the free-standing hundred, mitt its
#: attributive form; elf the singular thousand, elef the plural counted from
#: three upward ("tlitt elef").
_SCALE: Dict[str, int] = {
    "mija": 100, "mitt": 100,
    "elf": 1000, "elef": 1000,
    "miljun": 10 ** 6, "biljun": 10 ** 9,
}

_SIMPLE: Dict[str, int] = {**_ABSOLUTE, **_ATTRIBUTIVE, **_ORDINAL, **_TENS}

#: the "and" that joins a unit numeral to a tens word, and nothing else.
_JOINER = "u"

#: the linker written onto a numeral from eleven upward.
_LINKER = "il"

#: article + numeral pairs that spell a weekday, left unfolded so the weekday
#: vocabulary claims them.  Only the sun-letter-assimilated article that
#: actually precedes each of the three words is listed.
_WEEKDAY_HOMOGRAPH = {("it", "tnejn"), ("it", "tlieta"), ("l", "erbgħa")}

#: dual time nouns -> the ordinary plural they are read as two of.
_DUAL_PLURAL: Dict[str, str] = {
    "jumejn": "jiem",
    "ġimagħtejn": "ġimgħat",
    "sagħtejn": "sigħat",
    "xahrejn": "xhur",
    "sentejn": "snin",
}


def _numeric(tok: Token, value: int, end: Token = None) -> Token:
    return Token(text=str(value), raw=str(value), index=tok.index,
                 is_number=True, value=value, char_start=tok.char_start,
                 char_end=(end or tok).char_end)


def _dual_split(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Rewrite a dual time noun as a synthetic ``2`` plus its plural."""
    out: List[Token] = []
    changed = False
    for t in tokens:
        plural = None if t.is_number else _DUAL_PLURAL.get(t.text)
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


def read_run(words: Tuple[str, ...]) -> Optional[int]:
    """The value of a run of numeral surfaces, or ``None`` if it reads none.

    Additive across a ``u``-joined tens word, multiplicative on a hundred or
    thousand word, and transparent to the ``-il`` linker before a scale word.
    """
    total = 0
    current: Optional[int] = None
    i, n = 0, len(words)
    while i < n:
        word = words[i]
        if word == _JOINER:
            if (current is None or i + 1 >= n or words[i + 1] not in _TENS):
                return None
            current += _TENS[words[i + 1]]
            i += 2
            continue
        if word == _LINKER:
            if (current is None or not 11 <= current <= 19
                    or i + 1 >= n or words[i + 1] not in _SCALE):
                return None
            i += 1
            continue
        if word in _SCALE:
            scale = _SCALE[word]
            current = scale if current is None else current * scale
            if scale >= 1000:
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


#: every surface a numeral run may contain, joiner and linker included.
_RUN_WORDS = frozenset(_SIMPLE) | frozenset(_SCALE) | {_JOINER, _LINKER}

#: the surfaces a run may OPEN on -- a numeral, or a bare scale word standing
#: for one of itself ("mitt sena" == a hundred years, "elf sena" == a thousand).
_RUN_HEADS = frozenset(_SIMPLE) | frozenset(_SCALE)


def _run_fold(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Fold each maximal token span the numeral reader can read as one number.

    The span is grown as far as the numeral lexicon reaches and then shortened
    one token at a time until it reads, so a run that ends on a word the
    grammar wants back ("sitta u nofs" -- the joiner belongs to the clock, not
    to the number) yields the longest genuine number and leaves the rest.
    """
    out: List[Token] = []
    i, n, changed = 0, len(tokens), False
    while i < n:
        t = tokens[i]
        if t.is_number or t.text not in _RUN_HEADS:
            out.append(t)
            i += 1
            continue
        if i and (tokens[i - 1].text, t.text) in _WEEKDAY_HOMOGRAPH:
            out.append(t)
            i += 1
            continue
        end = i + 1
        while (end < n and not tokens[end].is_number
               and tokens[end].text in _RUN_WORDS):
            end += 1
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


def fold_mt(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Split the duals, then fold every numeral run they leave behind."""
    return _run_fold(_dual_split(tokens))
