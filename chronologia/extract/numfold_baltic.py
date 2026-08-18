# -*- coding: utf-8 -*-
"""Spelled-number folding pre-pass for the Baltic family (Lithuanian).

The tokenizer only recognises *digit* runs as numbers; Lithuanian speech
spells them, and both the numeral and the noun it counts carry case
morphology ("prieš tris dienas", "po penkių dienų").  This pass folds a
maximal run of spelled number-words into a single digit
:class:`~chronologia.extract.model.Token` so a ``NUM``/``DAY``/``HOUR``/
``ORD`` slot binds the same whether the writer typed ``3`` or the word.

Unlike the Slavic and Semitic families, this module owns its number data
outright: the surface tables below are the language's own closed classes,
transcribed from the dictionary sources cited beside each of them, and the
value of a run is read by :func:`read_run` here.  Nothing is delegated to an
external number back-end.

Three passes compose into :data:`fold_lt`, in this order:

* the **day-of-month ordinal** pass, which turns the spelled day into the
  digit its ``DAY`` slot binds and joins a ``tens + unit`` compound
  ("dvidešimt penktoji" == the twenty-fifth) into the one number it names --
  it must lead so the compound claims its cardinal tens before the cardinal
  fold can take that tens for a bare number;
* the **ordinal** pass, for the lone ordinal an ``ORD`` slot reads;
* the **cardinal** pass, which joins only a well-formed composed
  numeral into one token.

The counted noun's own form is a fact of the numeral, not of the noun:
:func:`governed_case` states that rule and :data:`UNIT_FORMS` carries the
surfaces it selects among.
"""
from __future__ import annotations

from typing import Callable, Dict, Optional, Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex

# ---------------------------------------------------------------------------
# Cardinals.  Every case form the temporal constructions read is listed: the
# nominative (bare counting, and the hour named after "be"), the genitive
# (after "po", and the hour named by "pusė"), and the accusative (after
# "prieš").  Masculine and feminine agree with the counted noun's gender.
#
# Sources, per paradigm:
#   1..9, 100, 1000 -- en.wiktionary.org declension tables (vienas, du, trys,
#       keturi, penki, šeši, septyni, aštuoni, devyni, tūkstantis);
#       lt.wiktionary.org "šimtas" (Kiekinis skaitvardis, vyr. g.).
#   10 -- lt.wiktionary.org "dešimt" (vard. dešimtis/dešimt,
#       kilm. dešimties/dešimt, dgs. dešimtys/dešimčių).
#   11..19 -- en.wiktionary.org headwords (vienuolika .. devyniolika); the
#       genitive is the regular feminine ``-a`` stem ending ``-os``
#       (paradigm: dienà -> dienõs, en.wiktionary "diena").
#   20..90 -- en.wiktionary.org headwords; these tens are indeclinable.
# ---------------------------------------------------------------------------
_CARDINALS: Dict[str, int] = {}


def _card(value: int, *surfaces: str) -> None:
    for s in surfaces:
        _CARDINALS[s] = value


_card(0, "nulis", "nulio", "nulį")
_card(1, "vienas", "viena", "vieno", "vienos", "vieną", "vieni", "vienų",
      "vienus", "vienais", "vienomis")
_card(2, "du", "dvi", "dviejų", "dviem", "dviejuose", "dviejose")
_card(3, "trys", "tris", "trijų", "trims", "trimis")
_card(4, "keturi", "keturios", "keturių", "keturis", "keturias", "keturiems",
      "keturioms", "keturiais", "keturiomis")
_card(5, "penki", "penkios", "penkių", "penkis", "penkias", "penkiems",
      "penkioms", "penkiais", "penkiomis")
_card(6, "šeši", "šešios", "šešių", "šešis", "šešias", "šešiems", "šešioms",
      "šešiais", "šešiomis")
_card(7, "septyni", "septynios", "septynių", "septynis", "septynias",
      "septyniems", "septynioms", "septyniais", "septyniomis")
_card(8, "aštuoni", "aštuonios", "aštuonių", "aštuonis", "aštuonias",
      "aštuoniems", "aštuonioms", "aštuoniais", "aštuoniomis")
_card(9, "devyni", "devynios", "devynių", "devynis", "devynias", "devyniems",
      "devynioms", "devyniais", "devyniomis")
_card(10, "dešimt", "dešimtis", "dešimties", "dešimtys", "dešimčių")

_TEENS = {11: "vienuolika", 12: "dvylika", 13: "trylika", 14: "keturiolika",
          15: "penkiolika", 16: "šešiolika", 17: "septyniolika",
          18: "aštuoniolika", 19: "devyniolika"}
for _v, _w in _TEENS.items():
    _card(_v, _w, _w[:-1] + "os")

_TENS: Dict[str, int] = {
    "dvidešimt": 20, "trisdešimt": 30, "keturiasdešimt": 40,
    "penkiasdešimt": 50, "šešiasdešimt": 60, "septyniasdešimt": 70,
    "aštuoniasdešimt": 80, "devyniasdešimt": 90}
_CARDINALS.update(_TENS)

_HUNDRED = {"šimtas", "šimto", "šimtą", "šimtai", "šimtų", "šimtus"}
_SCALE = {"tūkstantis": 1000, "tūkstančio": 1000, "tūkstantį": 1000,
          "tūkstančiai": 1000, "tūkstančių": 1000, "tūkstančius": 1000}
_card(100, *_HUNDRED)
_CARDINALS.update(_SCALE)


# ---------------------------------------------------------------------------
# Ordinals.  The day of the month is a FEMININE ordinal in the pronominal
# (definite) declension, agreeing with an elided "diena" -- "liepos penktoji"
# is the fifth of July.  The masculine nominative is the form an ``ORD`` slot
# reads elsewhere, and the plain feminine nominative is its indefinite
# counterpart.  All three columns are the nominative-singular row of the
# en.wiktionary.org declension tables for pirmas .. devynioliktas,
# dvidešimtas, trisdešimtas.  A compound day inflects its LAST element only,
# the tens staying the bare cardinal ("dvidešimt penktoji").
# ---------------------------------------------------------------------------
_ORD_STEMS = {
    1: "pirm", 2: "antr", 3: "treči", 4: "ketvirt", 5: "penkt", 6: "šešt",
    7: "septint", 8: "aštunt", 9: "devint", 10: "dešimt", 11: "vienuolikt",
    12: "dvylikt", 13: "trylikt", 14: "keturiolikt", 15: "penkiolikt",
    16: "šešiolikt", 17: "septyniolikt", 18: "aštuoniolikt",
    19: "devyniolikt", 20: "dvidešimt", 30: "trisdešimt"}

#: feminine pronominal nominative singular ("pirmoji") -- the day-of-month form
_DAY_ORD_LT: Dict[str, int] = {}
#: masculine and feminine indefinite nominative singular ("pirmas", "pirma")
_ORD_LT: Dict[str, int] = {}
for _v, _stem in _ORD_STEMS.items():
    _DAY_ORD_LT[_stem + "oji"] = _v
    _ORD_LT[_stem + "as"] = _v
    _ORD_LT[_stem + "a"] = _v
    _ORD_LT[_stem + "asis"] = _v
# "dešimta"/"dešimtas" (tenth) would otherwise be shadowed by nothing, but the
# tens cardinal "dvidešimt"/"trisdešimt" IS a cardinal surface as well: it is
# the compound-day prefix, and the day pass below claims it before the
# cardinal fold sees it.

#: the tens element of a compound day, which stays a bare cardinal
_DAY_TENS_LT = {"dvidešimt": 20, "trisdešimt": 30}


# ---------------------------------------------------------------------------
# Numeral government.  The form of the counted noun keys off the numeral's
# LAST digit, not its magnitude: a numeral ending in 1 (but not 11) takes the
# singular, one ending in 2..9 (but not 12..19) the plural, and one ending in
# 0 or falling in 11..19 the genitive plural -- "31 litas", "25 litai",
# "110 litų", "111 litų".  The singular and plural agree in CASE with the
# numeral itself (so they surface as accusatives after "prieš"); the genitive
# plural is fixed regardless of the numeral's own case.
# Sources: Wikipedia, "Lithuanian grammar" (numerals, worked examples);
# infkf.github.io/litsheets/numerals.html; LearnLT, cardinal numerals.
# ---------------------------------------------------------------------------
SINGULAR = "sg"
PLURAL = "pl"
GENITIVE_PLURAL = "gen_pl"


def governed_case(n: int) -> str:
    """The form the noun counted by ``n`` takes: ``sg``/``pl``/``gen_pl``."""
    n = abs(int(n))
    if 11 <= n % 100 <= 19 or n % 10 == 0:
        return GENITIVE_PLURAL
    if n % 10 == 1:
        return SINGULAR
    return PLURAL


#: unit noun surfaces per governed form, in the nominative and the accusative
#: (the case "prieš" imposes).  Same declension tables the ``unit_*.voc``
#: files cite: en.wiktionary.org for diena, savaitė, mėnuo, metai, valanda,
#: minutė, amžius, dešimtmetis.
UNIT_FORMS: Dict[str, Dict[str, str]] = {
    "day": {"sg": "diena", "pl": "dienos", "gen_pl": "dienų",
            "acc_sg": "dieną", "acc_pl": "dienas"},
    "week": {"sg": "savaitė", "pl": "savaitės", "gen_pl": "savaičių",
             "acc_sg": "savaitę", "acc_pl": "savaites"},
    "month": {"sg": "mėnuo", "pl": "mėnesiai", "gen_pl": "mėnesių",
              "acc_sg": "mėnesį", "acc_pl": "mėnesius"},
    # "metai" is a plurale tantum: it has no singular, so the singular slot of
    # the government rule is filled by the plural form ("vieni metai").
    "year": {"sg": "metai", "pl": "metai", "gen_pl": "metų",
             "acc_sg": "metus", "acc_pl": "metus"},
    "hour": {"sg": "valanda", "pl": "valandos", "gen_pl": "valandų",
             "acc_sg": "valandą", "acc_pl": "valandas"},
    "minute": {"sg": "minutė", "pl": "minutės", "gen_pl": "minučių",
               "acc_sg": "minutę", "acc_pl": "minutes"},
    "century": {"sg": "amžius", "pl": "amžiai", "gen_pl": "amžių",
                "acc_sg": "amžių", "acc_pl": "amžius"},
    "decade": {"sg": "dešimtmetis", "pl": "dešimtmečiai",
               "gen_pl": "dešimtmečių", "acc_sg": "dešimtmetį",
               "acc_pl": "dešimtmečius"},
}


def unit_surface(n: int, kind: str, accusative: bool = False) -> str:
    """The surface of unit ``kind`` as governed by the numeral ``n``.

    ``accusative`` selects the form required after "prieš"; the genitive
    plural is case-invariant, so it is returned either way.
    """
    case = governed_case(n)
    forms = UNIT_FORMS[kind]
    if case == GENITIVE_PLURAL or not accusative:
        return forms[case]
    return forms["acc_sg" if case == SINGULAR else "acc_pl"]


# ---------------------------------------------------------------------------
# The run reader
# ---------------------------------------------------------------------------

def read_run(text: str) -> Optional[int]:
    """Read the value of a joined run of Lithuanian number-word surfaces.

    Additive over units, teens and tens; "šimtas" multiplies the group
    accumulated so far, "tūkstantis" multiplies it and closes it into the
    running total ("du tūkstančiai dvidešimt penki" == 2025).  Returns
    ``None`` when a word is not a number-word, so the fold leaves the run
    alone rather than committing a partial reading.
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
#: number-word to continue the run another opened.  A composed Lithuanian
#: numeral descends through the classes -- a lower class may follow a higher
#: one ("dvidešimt penki" 25, "šimtas dvidešimt penki" 125) and a HUNDRED or
#: SCALE word may follow a lower one as its multiplier ("penki šimtai" 500,
#: "du tūkstančiai" 2000).  Two words of the SAME class never compose, which
#: is what keeps the clock's "be penkių trys" (five to three) two numbers
#: rather than the single 8 an unconditioned run scan would read.
_UNIT_CLASS, _TEN_CLASS, _HUNDRED_CLASS, _SCALE_CLASS = 1, 2, 3, 4


def _magnitude(word: str) -> int:
    if word in _SCALE:
        return _SCALE_CLASS
    if word in _HUNDRED:
        return _HUNDRED_CLASS
    if word in _TENS:
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


def _day_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Fold the spelled day-of-month ordinal, tens compound included."""
    out, i, n, changed = [], 0, len(tokens), False
    while i < n:
        t = tokens[i]
        if not t.is_number and t.text in _DAY_TENS_LT and i + 1 < n:
            unit = _DAY_ORD_LT.get(tokens[i + 1].text, 0)
            if 1 <= unit <= 9:
                out.append(_numeric(t, _DAY_TENS_LT[t.text] + unit,
                                    tokens[i + 1]))
                i, changed = i + 2, True
                continue
        if not t.is_number and t.text in _DAY_ORD_LT:
            out.append(_numeric(t, _DAY_ORD_LT[t.text]))
            i, changed = i + 1, True
            continue
        out.append(t)
        i += 1
    return reindex(out) if changed else tokens


def _ord_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Fold a lone spelled ordinal to the digit its ``ORD`` slot binds."""
    out, changed = [], False
    for t in tokens:
        if not t.is_number and t.text in _ORD_LT:
            out.append(_numeric(t, _ORD_LT[t.text]))
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


fold_lt = _compose(_day_rewrite, _ord_rewrite, _cardinal_rewrite)
