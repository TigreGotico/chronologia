"""Spelled-number folding pre-pass for Serbian.

numtag reads the numbers of Bulgarian, Croatian, Czech, Polish, Russian,
Slovak, Slovene and Ukrainian (:mod:`chronologia.extract.numlayer_slavic`).
numtag has no Serbian lexicon, so Serbian keeps this fold: a closed table of
cardinals in both scripts and the declined day-of-month ordinal.  Belarusian
(:mod:`chronologia.extract.numfold_be`) and Macedonian
(:mod:`chronologia.extract.numfold_macedonian`) keep their own folds for the
same reason.

``fold_sr`` is wired as the language ``hook`` in ``locale/sr/lang.json`` and is
a pure ``tuple[Token] -> tuple[Token]``.
"""
from __future__ import annotations

from typing import Callable, Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import NumberGrammar, make_fold, reindex


# -- calendar day: the declined ordinal that names the day of the month -------
# A date names the day with an ordinal agreeing with an elided day noun.  Days
# 21..31 are compound, and where the tens element stays a bare cardinal
# ("dvadeset petog"), ``tens_prefix`` names it and the rewrite adds the two.
# Folding only the unit would answer the fifth of the month for the
# twenty-fifth.
def _day_rewrite(ords: dict, tens_prefix: dict = None,
                 joiner: tuple = ()) -> Callable:
    """A pre-fold pass turning the declined day-of-month ordinal into the digit
    its ``DAY`` slot binds, adding a compound ``tens + unit`` pair into the one
    number it names.  Runs before the cardinal fold so a cardinal tens element
    is claimed by the compound rather than folded on its own."""
    ords = dict(ords)
    tens = dict(tens_prefix or {})
    tens.update({w: v for w, v in ords.items() if v in (20, 30)})

    def _num(t: Token, value: int, end: Token = None) -> Token:
        return Token(text=str(value), raw=str(value), index=t.index,
                     is_number=True, value=value, char_start=t.char_start,
                     char_end=(end or t).char_end, day_ordinal=True)

    def rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        out, i, n, changed = [], 0, len(tokens), False
        while i < n:
            t = tokens[i]
            if t.is_number:
                out.append(t)
                i += 1
                continue
            if t.text in tens:
                j = i + 1
                if j < n and tokens[j].text in joiner:
                    j += 1
                if j < n and ords.get(tokens[j].text, 0) in range(1, 10):
                    out.append(_num(t, tens[t.text] + ords[tokens[j].text],
                                    tokens[j]))
                    i, changed = j + 1, True
                    continue
            if t.text in ords:
                out.append(_num(t, ords[t.text]))
                i, changed = i + 1, True
                continue
            out.append(t)
            i += 1
        return reindex(out) if changed else tokens

    return rewrite


def _compose(*passes: Callable) -> Callable:
    def run(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        for p in passes:
            tokens = p(tokens)
        return tokens
    return run


# -- Serbian: dual-script cardinal/ordinal fold -------------------------------
# Neither ovos_number_parser nor numtag reads Serbian.  Below 100, Serbian cardinals form exactly like their Croatian cognates
# ("jedan, dva, tri ... dvadeset, trideset ..."), Wiktionary Appendix:
# Serbo-Croatian/Numbers (https://en.wiktionary.org/wiki/Appendix:Serbo-Croatian/Numbers),
# so this closed Latin-script table stands in for the model.  Every entry is
# doubled onto Cyrillic by the deterministic, digraph-aware transliteration
# (Gajica -> Vukovica) that every sr .voc surface in this locale also goes
# through -- the same "one closed list, both scripts" mechanism, rather than
# new engine machinery for script handling.  V1 covers 0-99 plus the bare
# hundred: the day/duration range the sr NL corpus exercises.
_SR_DIGRAPHS = (("lj", "љ"), ("nj", "њ"), ("dž", "џ"))
_SR_SINGLE = {
    "a": "а", "b": "б", "c": "ц", "č": "ч", "ć": "ћ", "d": "д", "đ": "ђ",
    "e": "е", "f": "ф", "g": "г", "h": "х", "i": "и", "j": "ј", "k": "к",
    "l": "л", "m": "м", "n": "н", "o": "о", "p": "п", "r": "р", "s": "с",
    "š": "ш", "t": "т", "u": "у", "v": "в", "z": "з", "ž": "ж"}


def sr_lat2cyr(word: str) -> str:
    """Deterministic Latin -> Cyrillic transliteration, digraphs first so
    lj/nj/dž fold to љ/њ/џ rather than their letters transliterated apart."""
    for lat, cyr in _SR_DIGRAPHS:
        word = word.replace(lat, cyr)
    return "".join(_SR_SINGLE.get(ch, ch) for ch in word)


_SR_ONES = {"jedan": 1, "jedna": 1, "jedno": 1, "dva": 2, "dve": 2, "tri": 3,
            "četiri": 4, "pet": 5, "šest": 6, "sedam": 7, "osam": 8,
            "devet": 9}
# "petnaest" (15) is deliberately absent: it is the clock's literal FRACTION
# terminal (clock_fraction_15.voc, alongside "četvrt") in "petnaest do sedam"
# == 6:45, and folding it to a digit here would strand that reading -- a
# spelled "petnaest <unit>" duration is out of scope for v1 (write the digit
# "15" instead).
_SR_TEENS = {"deset": 10, "jedanaest": 11, "dvanaest": 12, "trinaest": 13,
             "četrnaest": 14, "šesnaest": 16,
             "sedamnaest": 17, "osamnaest": 18, "devetnaest": 19}
_SR_TENS = {"dvadeset": 20, "trideset": 30, "četrdeset": 40, "pedeset": 50,
            "šezdeset": 60, "sedamdeset": 70, "osamdeset": 80,
            "devedeset": 90}
_SR_HUNDRED = {"sto": 100}
# "pola"/"četvrt" are deliberately NOT in this run set: they are the clock's
# literal FRACTION terminal (clock_fraction_15.voc/clock_fraction_30.voc),
# and folding them into a cardinal run here would fuse an adjacent HOUR
# ("pola četiri") into one wrong NUM instead of leaving FRACTION and HOUR as
# two slots.


def _sr_double(table: dict) -> dict:
    out = dict(table)
    out.update({sr_lat2cyr(w): v for w, v in table.items()})
    return out


_SR_WORDS = {**_sr_double(_SR_ONES), **_sr_double(_SR_TEENS),
             **_sr_double(_SR_TENS), **_sr_double(_SR_HUNDRED)}


def _extract_sr(text: str):
    """Compose a spelled sr cardinal from its parts (an optional hundred, an
    optional ten-or-teen, an optional one): "sto dvadeset pet" == 125,
    "dvadeset pet" == 25, "pet" == 5.  Any unknown word fails the whole run,
    mirroring the shared model-backed ``_extract``."""
    words = text.split()
    if not words or any(w not in _SR_WORDS for w in words):
        return False
    return float(sum(_SR_WORDS[w] for w in words))


def _make_fold_sr() -> Callable[[Tuple[Token, ...]], Tuple[Token, ...]]:
    return make_fold(NumberGrammar(
        is_number=lambda tok: tok.is_number or tok.text in _SR_WORDS,
        extract=_extract_sr))


# -- calendar day: genitive-masculine ordinal, elided "dana" -----------------
# Serbian names the day of the month with a genitive-masculine ordinal
# agreeing with an elided "dana" ("petog maja" = the fifth of May), the same
# shape as the other Slavic day ordinals.  Citation: Fond
# projekta Rastko / Правопис српскога језика (Матица српска), писање датума;
# spot-checked against Wiktionary's individual ordinal entries (prvi, drugi,
# treći, ...).  Compound days 21-31 leave the tens a bare cardinal and
# decline only the unit ("dvadeset petog" = 25th); both scripts via
# ``sr_lat2cyr``.
_DAY_SR = {}
for _stem, _v in (("prvog", 1), ("drugog", 2), ("trećeg", 3),
                  ("četvrtog", 4), ("petog", 5), ("šestog", 6),
                  ("sedmog", 7), ("osmog", 8), ("devetog", 9),
                  ("desetog", 10), ("jedanaestog", 11), ("dvanaestog", 12),
                  ("trinaestog", 13), ("četrnaestog", 14), ("petnaestog", 15),
                  ("šesnaestog", 16), ("sedamnaestog", 17),
                  ("osamnaestog", 18), ("devetnaestog", 19),
                  ("dvadesetog", 20), ("tridesetog", 30)):
    _DAY_SR[_stem] = _v
    _DAY_SR[sr_lat2cyr(_stem)] = _v
_TENS_SR = {"dvadeset": 20, "trideset": 30}
_TENS_SR.update({sr_lat2cyr(w): v for w, v in dict(_TENS_SR).items()})

fold_sr = _compose(_day_rewrite(_DAY_SR, _TENS_SR), _make_fold_sr())
