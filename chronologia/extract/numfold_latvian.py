# -*- coding: utf-8 -*-
"""Spelled-number folding pre-pass for Latvian.

The tokenizer only recognises *digit* runs as numbers, and Latvian speech
spells them.  This pass folds a maximal run of spelled number-words into a
single digit :class:`~chronologia.extract.model.Token` so a ``NUM``/``DAY``/
``HOUR``/``ORD`` slot binds the same whether the writer typed ``3`` or the
word.

The module owns its number data outright, transcribed from the dictionary
sources cited beside each table; nothing is delegated to an external number
back-end.  It is separate from the Lithuanian fold next door because the two
languages share no surface and compose differently: Latvian writes a
tens+unit compound as two words that must join ("divdesmit pieci" == 25) and
writes the spoken half hour as ONE word that must SPLIT ("pusčetri" == half
toward four == 03:30).

Three passes compose into :data:`fold_lv`, in this order:

* the **half-hour** pass, which splits ``pus`` + the cardinal naming the
  coming hour into the two tokens the ``FRACTION HOUR`` clock order reads;
* the **ordinal** pass, for the day-of-month or ``ORD`` slot, joining a
  ``tens + ordinal`` compound ("divdesmit piektais") into the one number it
  names -- it must precede the cardinal fold so the compound claims its
  cardinal tens before a bare-number reading can take it;
* the **cardinal** pass, which joins only a well-formed composed numeral.

The counted noun's form is a fact of the numeral, not of the noun.  Latvian
states that twice over, in two independent systems, and this module keeps
them apart: :func:`governed_form` is the case a preposition-marked duration
imposes, and :func:`counting_registers` is the register split of a bare
count.
"""
from __future__ import annotations

from typing import Callable, Dict, Optional, Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex

# ---------------------------------------------------------------------------
# Cardinals.  Every case form the temporal constructions read is listed: the
# nominative (bare counting), the genitive (the "of" forms), and above all the
# DATIVE, which is the case "pirms" and "pēc" impose on both the numeral and
# the noun it counts -- "pirms diviem gadiem" (two years ago), "pirms
# sešdesmit gadiem" (sixty years ago).
#
# Sources, per paradigm:
#   0..9 -- en.wiktionary.org declension tables (nulle, viens, divi, trīs,
#       četri, pieci, seši, septiņi, astoņi, deviņi).
#   10, 11..19 -- en.wiktionary.org headwords (desmit, vienpadsmit ..
#       deviņpadsmit); these have only the instrumental and locative filled in
#       their tables, every other cell being the bare indeclinable headword.
#   20..90 -- en.wiktionary.org headwords, listed in full in the "Latvian
#       cardinal numbers from 0 to 99" box on any of the pages above; they are
#       indeclinable, and a compound is written as two words
#       ("divdesmit pieci").
#   100 -- en.wiktionary.org "simts", with the synonym "simt".
#   1000 -- en.wiktionary.org declension table of "tūkstotis".
# ---------------------------------------------------------------------------
_CARDINALS: Dict[str, int] = {}


def _card(value: int, *surfaces: str) -> None:
    for s in surfaces:
        _CARDINALS[s] = value


_card(0, "nulle", "nulles", "nullei", "nulli", "nullē")
_card(1, "viens", "viena", "vienam", "vienu", "vienā", "vieni", "vienas",
      "vienai", "vieniem", "vienām", "vienus", "vienos", "vienās")
_card(2, "divi", "divas", "divu", "diviem", "divām", "divus", "divos", "divās")
_card(3, "trīs", "triju", "trim", "trijiem", "trijām", "trijos", "trijās")
_card(4, "četri", "četras", "četru", "četriem", "četrām", "četrus", "četros",
      "četrās")
_card(5, "pieci", "piecas", "piecu", "pieciem", "piecām", "piecus", "piecos",
      "piecās")
_card(6, "seši", "sešas", "sešu", "sešiem", "sešām", "sešus", "sešos", "sešās")
_card(7, "septiņi", "septiņas", "septiņu", "septiņiem", "septiņām", "septiņus",
      "septiņos", "septiņās")
_card(8, "astoņi", "astoņas", "astoņu", "astoņiem", "astoņām", "astoņus",
      "astoņos", "astoņās")
_card(9, "deviņi", "deviņas", "deviņu", "deviņiem", "deviņām", "deviņus",
      "deviņos", "deviņās")
_card(10, "desmit", "desmitiem", "desmitos")

_TEENS = {11: "vienpadsmit", 12: "divpadsmit", 13: "trīspadsmit",
          14: "četrpadsmit", 15: "piecpadsmit", 16: "sešpadsmit",
          17: "septiņpadsmit", 18: "astoņpadsmit", 19: "deviņpadsmit"}
for _v, _w in _TEENS.items():
    _card(_v, _w, _w + "iem", _w + "os")

_TENS: Dict[str, int] = {
    "divdesmit": 20, "trīsdesmit": 30, "četrdesmit": 40, "piecdesmit": 50,
    "sešdesmit": 60, "septiņdesmit": 70, "astoņdesmit": 80,
    "deviņdesmit": 90}
_CARDINALS.update(_TENS)

_HUNDRED = {"simts", "simt"}
_SCALE = {"tūkstotis": 1000, "tūkstoša": 1000, "tūkstotim": 1000,
          "tūkstoti": 1000, "tūkstotī": 1000, "tūkstoši": 1000,
          "tūkstošu": 1000, "tūkstošiem": 1000, "tūkstošus": 1000,
          "tūkstošos": 1000}
_card(100, *_HUNDRED)
_CARDINALS.update(_SCALE)


# ---------------------------------------------------------------------------
# Ordinals.  The day of the month is written with a digit and a dot in
# Latvian ("29. maijs"), so the spelled ordinal is what an ``ORD`` slot reads
# rather than the ordinary date form.  Only the DEFINITE masculine nominative
# singular ships: it is the citation form en.wiktionary.org attests as a
# headword for each value (pirmais .. deviņpadsmitais, divdesmitais,
# trīsdesmitais), and the definite feminine "-ā" is homographic with the
# locative that carries the adverbial date, which would make every "maijā"
# neighbour ambiguous.  A compound inflects its LAST element only, the tens
# staying the bare cardinal ("divdesmit piektais").
# ---------------------------------------------------------------------------
_ORD_STEMS = {
    1: "pirm", 2: "otr", 3: "treš", 4: "ceturt", 5: "piekt", 6: "sest",
    7: "septīt", 8: "astot", 9: "devīt", 10: "desmit", 11: "vienpadsmit",
    12: "divpadsmit", 13: "trīspadsmit", 14: "četrpadsmit",
    15: "piecpadsmit", 16: "sešpadsmit", 17: "septiņpadsmit",
    18: "astoņpadsmit", 19: "deviņpadsmit", 20: "divdesmit",
    30: "trīsdesmit"}

_ORD_LV: Dict[str, int] = {stem + "ais": v for v, stem in _ORD_STEMS.items()}

#: the tens element of a compound ordinal, which stays a bare cardinal
_ORD_TENS_LV = {"divdesmit": 20, "trīsdesmit": 30}


# ---------------------------------------------------------------------------
# The spoken half hour, which names the COMING hour: "pusčetri" is 03:30 and
# "pusastoņi" 07:30, the prefix "pus" (half) fused onto the masculine
# nominative cardinal of the hour being counted toward.  Written as one word,
# so the fold SPLITS it into the ``FRACTION HOUR`` pair the clock order reads;
# ``bare_half_to`` + ``toward_hour_12h`` in ``lang.json`` then roll the named
# hour back by one.
#
# Sources: pronuncia.io, "How to Tell Time and Dates in Latvian for English
# Speakers" ("Ir pusastoņi" == it is 7:30, "pusčetri" == half past three); a
# second, independent survey repeating the same rule and the same worked
# example ("pusseptiņi" == 6:30, "pusčetri" == 3:30).  The cardinals
# themselves are the dictionary-attested nominatives above.
#
# "pusviens" (12:30) is NOT here.  Every hour from two upward takes the
# masculine nominative PLURAL, which is the only form the sources attest in
# the compound; "viens" is a singular that declines for gender, no source
# gives the compound, and guessing between "pusviens" and "pusviena" would be
# inventing a surface.  A refusal test pins the omission.
# ---------------------------------------------------------------------------
_HALF_PREFIX = "pus"

_TOWARD_HOUR: Dict[str, int] = {
    "divi": 2, "trīs": 3, "četri": 4, "pieci": 5, "seši": 6, "septiņi": 7,
    "astoņi": 8, "deviņi": 9, "desmit": 10, "vienpadsmit": 11,
    "divpadsmit": 12}


# ---------------------------------------------------------------------------
# Numeral government, system one: the case a duration marker imposes.
#
# "pirms" (ago) and "pēc" (in) put their whole phrase in the dative, and the
# unit noun's NUMBER follows the CLDR plural rule for Latvian: the singular
# when the numeral ends in 1 and is not 11, the plural otherwise -- "pirms
# gada" / "pirms 21 gada" against "pirms 11 gadiem" / "pirms 20 gadiem".  The
# singular slot surfaces as the genitive singular and the plural as the
# dative plural, which is the pair CLDR 47 ``dateFields.json`` for ``lv``
# spells out for every unit and en.wiktionary.org's declension tables confirm
# cell by cell.  Note this is the DATIVE plural (gadiem, dienām), not the
# genitive plural (gadu, dienu): the two are distinct in every Latvian
# declension.
# ---------------------------------------------------------------------------
GENITIVE_SINGULAR = "gen_sg"
DATIVE_PLURAL = "dat_pl"


def governed_form(n: int) -> str:
    """The form of the noun ``n`` counts after "pirms"/"pēc"."""
    n = abs(int(n))
    if n % 10 == 1 and n % 100 != 11:
        return GENITIVE_SINGULAR
    return DATIVE_PLURAL


# ---------------------------------------------------------------------------
# Numeral government, system two: the register split of a bare count.
#
# After 11-19 and the round tens, a Latvian bare count has TWO live surfaces:
# a formal one putting the noun in the genitive plural ("vienpadsmit gadu")
# and a colloquial one leaving it in the case the sentence otherwise wants,
# which for a bare count is the nominative ("vienpadsmit gadi").  The split is
# real and corroborated, but no source gives a mechanical trigger for which
# register a given text is written in -- so this module states which surfaces
# are ADMISSIBLE and never claims to know which one a writer chose.  Both are
# in the vocabulary; nothing infers the register from the input.
# ---------------------------------------------------------------------------
NOMINATIVE = "nom"
GENITIVE_PLURAL = "gen_pl"


def counting_registers(n: int) -> Tuple[str, ...]:
    """The noun forms a bare count of ``n`` may surface in.

    One form outside the split's range, two inside it -- and never a choice
    between them, because the choice is the writer's register, not a fact
    about ``n``.
    """
    n = abs(int(n))
    if 11 <= n % 100 <= 19 or n % 10 == 0:
        return (NOMINATIVE, GENITIVE_PLURAL)
    return (NOMINATIVE,)


#: unit noun surfaces per form.  Declension tables: en.wiktionary.org for
#: diena, nedēļa, mēnesis, gads, stunda, minūte, gadsimts, desmitgade.
UNIT_FORMS: Dict[str, Dict[str, str]] = {
    "day": {"nom": "dienas", "gen_pl": "dienu", "gen_sg": "dienas",
            "dat_pl": "dienām", "nom_sg": "diena", "acc_sg": "dienu",
            "loc_sg": "dienā"},
    "week": {"nom": "nedēļas", "gen_pl": "nedēļu", "gen_sg": "nedēļas",
             "dat_pl": "nedēļām", "nom_sg": "nedēļa", "acc_sg": "nedēļu",
             "loc_sg": "nedēļā"},
    "month": {"nom": "mēneši", "gen_pl": "mēnešu", "gen_sg": "mēneša",
              "dat_pl": "mēnešiem", "nom_sg": "mēnesis", "acc_sg": "mēnesi",
              "loc_sg": "mēnesī"},
    "year": {"nom": "gadi", "gen_pl": "gadu", "gen_sg": "gada",
             "dat_pl": "gadiem", "nom_sg": "gads", "acc_sg": "gadu",
             "loc_sg": "gadā"},
    "hour": {"nom": "stundas", "gen_pl": "stundu", "gen_sg": "stundas",
             "dat_pl": "stundām", "nom_sg": "stunda", "acc_sg": "stundu",
             "loc_sg": "stundā"},
    "minute": {"nom": "minūtes", "gen_pl": "minūšu", "gen_sg": "minūtes",
               "dat_pl": "minūtēm", "nom_sg": "minūte", "acc_sg": "minūti",
               "loc_sg": "minūtē"},
    "century": {"nom": "gadsimti", "gen_pl": "gadsimtu",
                "gen_sg": "gadsimta", "dat_pl": "gadsimtiem",
                "nom_sg": "gadsimts", "acc_sg": "gadsimtu",
                "loc_sg": "gadsimtā"},
    "decade": {"nom": "desmitgades", "gen_pl": "desmitgažu",
               "gen_sg": "desmitgades", "dat_pl": "desmitgadēm",
               "nom_sg": "desmitgade", "acc_sg": "desmitgadi",
               "loc_sg": "desmitgadē"},
}


def unit_surface(n: int, kind: str, form: str) -> str:
    """The surface of unit ``kind`` in ``form``, for a count of ``n``.

    ``n`` selects the singular for the one form that has one: the genitive
    singular a marker imposes on a numeral ending in 1.  Every other form is
    plural and independent of ``n``.
    """
    forms = UNIT_FORMS[kind]
    if form == NOMINATIVE and governed_form(n) == GENITIVE_SINGULAR:
        return forms["nom_sg"]
    return forms[form]


# ---------------------------------------------------------------------------
# The run reader
# ---------------------------------------------------------------------------

def read_run(text: str) -> Optional[int]:
    """Read the value of a joined run of Latvian number-word surfaces.

    Additive over units, teens and tens; "simts" multiplies the group
    accumulated so far, "tūkstotis" multiplies it and closes it into the
    running total ("divi tūkstoši divdesmit pieci" == 2025).  Returns ``None``
    when a word is not a number-word, so the fold leaves the run alone rather
    than committing a partial reading.
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
#: number-word to continue the run another opened.  A composed Latvian numeral
#: descends through the classes -- a lower class may follow a higher one
#: ("divdesmit pieci" 25, "simts divdesmit pieci" 125) and a HUNDRED or SCALE
#: word may follow a lower one as its multiplier ("divi simti" 200, "divi
#: tūkstoši" 2000).  Two words of the same class never compose, and a TEEN
#: never continues a run at all: 11-19 are whole numerals in Latvian, so
#: "divdesmit vienpadsmit" is not a number and must not read as one.
_UNIT_CLASS, _TEEN_CLASS, _TEN_CLASS, _HUNDRED_CLASS, _SCALE_CLASS = 1, 2, 3, 4, 5


def _magnitude(word: str) -> int:
    if word in _SCALE:
        return _SCALE_CLASS
    if word in _HUNDRED:
        return _HUNDRED_CLASS
    if word in _TENS:
        return _TEN_CLASS
    if _CARDINALS.get(word) in _TEENS:
        return _TEEN_CLASS
    return _UNIT_CLASS


def _composes(previous: str, following: str) -> bool:
    prev, nxt = _magnitude(previous), _magnitude(following)
    if nxt == _TEEN_CLASS:
        return False
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


def _ord_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Fold a spelled ordinal, tens compound included."""
    out, i, n, changed = [], 0, len(tokens), False
    while i < n:
        t = tokens[i]
        if not t.is_number and t.text in _ORD_TENS_LV and i + 1 < n:
            unit = _ORD_LV.get(tokens[i + 1].text, 0)
            if 1 <= unit <= 9:
                out.append(_numeric(t, _ORD_TENS_LV[t.text] + unit,
                                    tokens[i + 1]))
                i, changed = i + 2, True
                continue
        if not t.is_number and t.text in _ORD_LV:
            out.append(_numeric(t, _ORD_LV[t.text]))
            i, changed = i + 1, True
            continue
        out.append(t)
        i += 1
    return reindex(out) if changed else tokens


def _half_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Split "pusčetri" into the ``pus`` + hour pair the clock order reads."""
    out, changed = [], False
    for t in tokens:
        hour = (None if t.is_number or not t.text.startswith(_HALF_PREFIX)
                else _TOWARD_HOUR.get(t.text[len(_HALF_PREFIX):]))
        if hour is None:
            out.append(t)
            continue
        cut = (None if t.char_start is None
               else t.char_start + len(_HALF_PREFIX))
        out.append(Token(text=_HALF_PREFIX, raw=_HALF_PREFIX, index=t.index,
                         char_start=t.char_start, char_end=cut, cap=t.cap))
        out.append(Token(text=str(hour), raw=str(hour), index=t.index,
                         is_number=True, value=hour, char_start=cut,
                         char_end=t.char_end))
        changed = True
    return reindex(out) if changed else tokens


def _compose(*passes: Callable) -> Callable:
    def run(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        for p in passes:
            tokens = p(tokens)
        return tokens
    return run


fold_lv = _compose(_half_rewrite, _ord_rewrite, _cardinal_rewrite)
