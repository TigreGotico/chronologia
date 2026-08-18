# -*- coding: utf-8 -*-
"""Spelled-number folding pre-pass for Indo-Aryan (Hindi).

The tokenizer reads *digit* runs as numbers -- Devanagari ०-९ as readily as
ASCII, since both are Unicode decimal digits -- but Hindi speech spells its
numerals, and 1..99 are SUPPLETIVE: there is no productive tens+unit rule to
compose them from.  बयालीस (42) is not derivable from चार and दो, and no
regular affix relates छियालीस (46) to सैंतालीस (47).  A rule-driven number
back-end therefore cannot serve this language at all, and none is consulted:
the tables below are the language's own closed class, transcribed word by word
from the dictionary source cited beside each of them, and the value of a run is
read by :func:`read_run` here.

Three passes compose into :data:`fold_hi`, in this order:

* the **Devanagari digit** pass, which rewrites a numeral written in the native
  digits to its ASCII spelling so a slot bound by a digit pattern (the ``CLOCK``
  literal, the ISO and slash dates) reads ``१५:३०`` exactly as it reads
  ``15:30``;
* the **ordinal** pass, for the ordinal an ``ORD`` slot reads
  ("इक्कीसवीं सदी" -- the twenty-first century);
* the **cardinal** pass, which joins a well-formed composed numeral into one
  token ("दो हज़ार चौबीस" == 2024).

Hindi nouns counted by a numeral take the OBLIQUE case, which for the -आ stems
is a plain -ए ("दो घंटे", "तीन हफ़्ते"); that is a fact of the noun and lives in
the ``unit_*.voc`` surfaces, not here.
"""
from __future__ import annotations

from typing import Callable, Dict, Optional, Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex

# ---------------------------------------------------------------------------
# Devanagari digits.  ०-९ (U+0966..U+096F) are ordinary decimal digits and are
# used interchangeably with the ASCII ones in Hindi writing; CLDR 47 ships the
# locale with the ASCII default, so the native spelling is folded to it.
# Source: Unicode 16.0, Devanagari block chart (U+0900), DIGIT ZERO..NINE.
# ---------------------------------------------------------------------------
_DEV_DIGITS = str.maketrans({chr(0x0966 + d): str(d) for d in range(10)})


# ---------------------------------------------------------------------------
# Cardinals 0..100, one entry per attested surface.  Every value is read from
# the ``{{number box|hi|N}}`` header of the word's own en.wiktionary.org entry,
# harvested over Category:Hindi cardinal numbers
# (https://en.wiktionary.org/wiki/Category:Hindi_cardinal_numbers); alternative
# spellings are the ``{{alt sp}}`` / ``{{alter}}`` variants those entries name.
# The nukta is written where the entry writes it (सिफ़र) and the nukta-less
# spelling is shipped alongside wherever Wiktionary attests one.
#
# Deliberately absent: इक (a bound prefix, whose number box is Dogra, not
# Hindi), यक (a Persian borrowing), and the literary/poetic hundreds शत and सद
# -- none of them is the everyday counting word, and test_hi_omitted_surfaces
# pins that they do not fold.
# ---------------------------------------------------------------------------
_CARDINALS: Dict[str, int] = {}


def _card(value: int, *surfaces: str) -> None:
    for s in surfaces:
        _CARDINALS[s] = value


_card(0, "शून्य", "सिफ़र")
_card(1, "एक")
_card(2, "दो")
_card(3, "तीन")
_card(4, "चार")
_card(5, "पाँच", "पांच")
_card(6, "छः", "छह", "छै")
_card(7, "सात")
_card(8, "आठ")
_card(9, "नौ")
_card(10, "दस")
_card(11, "ग्यारह")
_card(12, "बारह")
_card(13, "तेरह")
_card(14, "चौदह")
_card(15, "पंदरह", "पंद्रह", "पन्द्रह")
_card(16, "सोलह")
_card(17, "सत्तरह", "सत्रह")
_card(18, "अठारह")
_card(19, "उन्नीस")
_card(20, "बीस")
_card(21, "इक्कीस")
_card(22, "बाईस")
_card(23, "तेईस")
_card(24, "चौबीस")
_card(25, "पच्चीस")
_card(26, "छब्बीस")
_card(27, "सत्ताईस")
_card(28, "अट्ठाईस")
_card(29, "उनतीस")
_card(30, "तीस")
_card(31, "इकतीस", "इकत्तीस")
_card(32, "बत्तीस")
_card(33, "तेंतीस", "तेतीस", "तैंतीस")
_card(34, "चौंतीस")
_card(35, "पैंतीस")
_card(36, "छत्तीस")
_card(37, "सैंतीस")
_card(38, "अड़तीस")
_card(39, "उनतालीस")
_card(40, "चालीस")
_card(41, "इकतालीस")
_card(42, "बयालीस")
_card(43, "तैंतालीस")
_card(44, "चवालीस")
_card(45, "पैंतालीस")
_card(46, "छियालीस")
_card(47, "सैंतालीस")
_card(48, "अड़तालीस")
_card(49, "उनचास")
_card(50, "पचास")
_card(51, "इकावन", "इक्यावन")
_card(52, "बावन")
_card(53, "तिरपन")
_card(54, "चव्वन", "चौवन")
_card(55, "पचपन")
_card(56, "छप्पन")
_card(57, "सत्तावन")
_card(58, "अट्ठावन")
_card(59, "उनसठ")
_card(60, "साठ")
_card(61, "इकसठ")
_card(62, "बासठ")
_card(63, "तिरसठ")
_card(64, "चौंसठ")
_card(65, "पैंसठ")
_card(66, "छियासठ")
_card(67, "सड़सठ", "सरसठ")
_card(68, "अड़सठ")
_card(69, "उनहत्तर")
_card(70, "सत्तर")
_card(71, "इकहत्तर")
_card(72, "बहत्तर")
_card(73, "तिहत्तर")
_card(74, "चौहत्तर")
_card(75, "पचहत्तर", "पछत्तर")
_card(76, "छिहत्तर")
_card(77, "सतहत्तर")
_card(78, "अठहत्तर")
_card(79, "उनासी", "उन्यासी")
_card(80, "अस्सी")
_card(81, "इकासी", "इक्यासी")
_card(82, "बयासी", "बिरासी")
_card(83, "तिरासी")
_card(84, "चौरासी")
_card(85, "पचासी")
_card(86, "छियासी")
_card(87, "सत्तासी")
_card(88, "अट्ठासी")
_card(89, "नवासी")
_card(90, "नब्बे", "नव्वे")
_card(91, "इकानवे", "इक्यानवे")
_card(92, "बानवे")
_card(93, "तिरानवे")
_card(94, "चौरानवे")
_card(95, "पंचानवे")
_card(96, "छियानवे")
_card(97, "सत्तानवे")
_card(98, "अट्ठानवे")
_card(99, "निनानवे", "निन्यानवे")
_card(100, "सौ")


#: the hundred, which MULTIPLIES the group before it ("उन्नीस सौ" == 1900).
_HUNDRED = {"सौ"}
#: the thousand, which multiplies its group and closes it into the running
#: total ("दो हज़ार चौबीस" == 2024).  हज़ार is the everyday word (a
#: Persian borrowing); हजार is its nukta-less spelling.  The Sanskritic
#: सहस्र family is attested but literary, and is left out with शत/सद.
_SCALE = {"हज़ार": 1000, "हजार": 1000}
_CARDINALS.update(_SCALE)


# ---------------------------------------------------------------------------
# Ordinals.  The first four are suppletive words in their own right
# (पहला, दूसरा, तीसरा, चौथा); from five up the ordinal is the cardinal plus
# the suffix -वाँ.  Both series inflect for GENDER and case on the ā/ā̃-stem
# adjective paradigm, whose three distinct forms are the direct masculine
# singular (-आ / -वाँ), the oblique-or-plural masculine (-ए / -वें) and the
# feminine (-ई / -वीं) -- "इक्कीसवीं सदी" is the twenty-first century, feminine
# because सदी is.  All three are shipped, because a date or a scoped ordinal
# may surface in any of them.
#
# Headwords: en.wiktionary.org, Category:Hindi ordinal numbers
# (https://en.wiktionary.org/wiki/Category:Hindi_ordinal_numbers), each entry
# carrying its own ``{{number box|hi|N}}``.  The other two columns are that
# entry's own ``{{hi-adecl}}`` declension table -- verified against
# https://en.wiktionary.org/wiki/पाँचवाँ (पाँचवाँ / पाँचवें / पाँचवीं) and
# https://en.wiktionary.org/wiki/पहला (पहला / पहले / पहली).
#
# पहले is withheld from the table even though the paradigm generates it: it is
# also the ordinary adverb "before, ago" (en.wiktionary.org, "पहले"), which is
# the very marker the past-offset construction reads in "तीन दिन पहले".  Folding
# it to the number 1 would eat that marker and silently turn "three days ago"
# into a bare quantity.  The Sanskritic register (प्रथम, द्वितीय, तृतीय, दशम)
# is a separate closed class and is not shipped.
# ---------------------------------------------------------------------------
_ORD_STEMS: Dict[int, Tuple[str, ...]] = {
    1: ("पहल",), 2: ("दूसर",), 3: ("तीसर",), 4: ("चौथ",),
}

#: the -वाँ ordinals, keyed by value; every surface is the attested headword
_ORD_WA: Dict[int, Tuple[str, ...]] = {
    5: ("पाँचवाँ",), 6: ("छठवाँ", "छठा"), 7: ("सातवाँ", "सातवां"),
    8: ("आठवाँ", "आठवां"), 9: ("नवाँ", "नौवाँ"), 10: ("दसवाँ",),
    11: ("ग्यारहवाँ",), 12: ("बारहवाँ",), 13: ("तेरहवाँ",), 14: ("चौदहवाँ",),
    15: ("पंद्रहवाँ", "पन्दरहवाँ", "पन्द्रहवाँ"), 16: ("सोलहवाँ",),
    17: ("सत्तरहवाँ", "सत्रहवाँ"), 18: ("अठारहवाँ",), 19: ("उन्नीसवाँ",),
    20: ("बीसवाँ",), 21: ("इक्कीसवाँ",), 22: ("बाईसवाँ",), 23: ("तेईसवाँ",),
    24: ("चौबीसवाँ",), 25: ("पच्चीसवाँ",), 26: ("छब्बीसवाँ",),
    27: ("सत्ताईसवाँ",), 28: ("अट्ठाईसवाँ",), 29: ("उनतीसवाँ",),
    30: ("तीसवाँ",), 31: ("इकत्तीसवाँ",), 100: ("सौवाँ",),
}

_ORDINALS: Dict[str, int] = {}
for _v, _stems in _ORD_STEMS.items():
    for _s in _stems:
        # पहले is the "ago" marker and never an ordinal surface here
        _ORDINALS.update({_s + "ा": _v, _s + "ी": _v})
        if _v != 1:
            _ORDINALS[_s + "े"] = _v
for _v, _heads in _ORD_WA.items():
    for _h in _heads:
        _ORDINALS[_h] = _v
        # the ā̃-stem paradigm: -वाँ / -वां direct masc, -वें oblique/plural
        # masc, -वीं feminine.  छठा is an ā-stem doublet of छठवाँ and takes
        # the ā-stem endings instead.
        if _h.endswith("वाँ") or _h.endswith("वां"):
            _ORDINALS[_h[:-3] + "वें"] = _v
            _ORDINALS[_h[:-3] + "वीं"] = _v
        elif _h.endswith("ा"):
            _ORDINALS[_h[:-1] + "े"] = _v
            _ORDINALS[_h[:-1] + "ी"] = _v


# ---------------------------------------------------------------------------
# The run reader
# ---------------------------------------------------------------------------

def read_run(text: str) -> Optional[int]:
    """Read the value of a joined run of Hindi number-word surfaces.

    Additive over the suppletive 0..99 words; सौ multiplies the group
    accumulated so far ("उन्नीस सौ" == 1900) and हज़ार multiplies it and closes
    it into the running total ("दो हज़ार चौबीस" == 2024).  Returns ``None`` when
    a word is not a number-word, so the fold leaves the run alone rather than
    committing a partial reading.
    """
    total = 0
    group = 0
    seen = False
    for word in text.split():
        if word.isdigit():
            group += int(word)
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


#: the magnitude class of a cardinal surface, which is what licenses one
#: number-word to continue a run another opened.  A composed Hindi numeral
#: descends through the classes -- a lower class may follow a higher one
#: ("दो हज़ार चौबीस") and सौ or हज़ार may follow a lower one as its multiplier
#: ("उन्नीस सौ", "दो हज़ार").  Two words of the SAME class never compose, which
#: is what keeps two adjacent suppletive numerals two numbers rather than the
#: single sum an unconditioned run scan would read.
_UNIT_CLASS, _HUNDRED_CLASS, _SCALE_CLASS = 1, 2, 3


def _magnitude(word: str) -> int:
    if word in _SCALE:
        return _SCALE_CLASS
    if word in _HUNDRED:
        return _HUNDRED_CLASS
    return _UNIT_CLASS


def _composes(previous: str, following: str) -> bool:
    prev, nxt = _magnitude(previous), _magnitude(following)
    if nxt > prev:
        return nxt in (_HUNDRED_CLASS, _SCALE_CLASS)
    return nxt < prev


def _devanagari_digits(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Rewrite a token containing Devanagari digits to its ASCII spelling."""
    out, changed = [], False
    for t in tokens:
        folded = t.text.translate(_DEV_DIGITS)
        if folded == t.text:
            out.append(t)
            continue
        out.append(Token(text=folded, raw=t.raw, index=t.index,
                         is_number=t.is_number,
                         value=int(folded) if folded.isdigit() else t.value,
                         char_start=t.char_start, char_end=t.char_end))
        changed = True
    return reindex(out) if changed else tokens


def _cardinal_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Fold a well-formed run of spelled cardinals into one digit token."""
    out, i, n, changed = [], 0, len(tokens), False
    while i < n:
        t = tokens[i]
        if t.is_number or t.text not in _CARDINALS:
            out.append(t)
            i += 1
            continue
        j = i + 1
        while (j < n and not tokens[j].is_number
               and tokens[j].text in _CARDINALS
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


def _ordinal_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Fold a spelled ordinal to the digit its ``ORD`` slot binds."""
    out, changed = [], False
    for t in tokens:
        if not t.is_number and t.text in _ORDINALS:
            out.append(_numeric(t, _ORDINALS[t.text]))
            changed = True
        else:
            out.append(t)
    return reindex(out) if changed else tokens


def _compose(*passes: Callable) -> Callable:
    def run(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        for p in passes:
            tokens = p(tokens)
        return tokens
    return run


fold_hi = _compose(_devanagari_digits, _ordinal_rewrite, _cardinal_rewrite)
