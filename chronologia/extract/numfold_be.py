# -*- coding: utf-8 -*-
"""Spelled-number folding for Belarusian.

Belarusian has no ``ovos_number_parser`` model, so -- like the Serbian fold in
:mod:`chronologia.extract.numfold_slavic` -- the number-word set and the value
arithmetic are owned here as closed tables.  Every surface below is transcribed
from Wiktionary's ``Module:number list/data/be``, the same per-language Lua data
table Wiktionary's own numeral templates render from
(https://en.wiktionary.org/wiki/Module:number_list/data/be), with the stress
marks it carries dropped -- running text does not write them.

Three passes compose, in the order the Slavic family established:

* the day-of-month ordinal (genitive masculine, agreeing with an elided "дня")
  leads, so a compound day claims its bare-cardinal tens before the cardinal
  fold can take that tens for a number of its own;
* the cardinal fold, preceded by the masculine-nominative ordinal the quarter
  and scoped-ordinal constructions read;
* the toward-hour ordinal trails, so its surfaces never merge with the
  adjacent fraction word of the spoken clock.
"""
from __future__ import annotations

from typing import Callable, Dict, Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import NumberGrammar, make_fold, reindex

#: The single-word year deictics -> the determiner + unit-noun pair the
#: ordinary relative-period grammar already reads.  CLDR's relative-type--1
#: and relative-type-0 for the be year field are летась and сёлета, single
#: words where every other language in the family says "in the last/this
#: year"; the locative phrases they are equivalent to (у мінулым годзе, у
#: гэтым годзе) are CLDR's own synonyms for them, and en.wiktionary's entries
#: for летась and сёлета give exactly those as the synonym gloss.  Splitting
#: the adverb here keeps the whole reading local to this locale.
_YEAR_ADVERB: Dict[str, tuple] = {
    "летась": ("мінулым", "годзе"),
    "сёлета": ("гэтым", "годзе"),
}

_ONES: Dict[str, int] = {
    "адзін": 1, "два": 2, "тры": 3, "чатыры": 4, "пяць": 5, "шэсць": 6,
    "сем": 7, "восем": 8, "дзевяць": 9}
# "два" agrees in gender: the feminine "дзве" is the form every feminine
# temporal noun takes ("дзве гадзіны", "дзве хвіліны"), and "адзін" likewise
# has the feminine nominative/accusative/oblique trio.  Wiktionary, "дзве"
# (nominative/accusative feminine plural of два) and "адна".
_FEMININE: Dict[str, int] = {
    "дзве": 2, "дзвюх": 2, "трох": 3, "адна": 1, "адну": 1, "адной": 1}
_TEENS: Dict[str, int] = {
    "дзесяць": 10, "адзінаццаць": 11, "дванаццаць": 12, "трынаццаць": 13,
    "чатырнаццаць": 14, "пятнаццаць": 15, "шаснаццаць": 16,
    # 17 is written both ways: "сямнаццаць" in Wiktionary's numeral module,
    # "семнаццаць" as the headword of the academic Тлумачальны слоўнік
    # беларускай мовы.  Both are current; both are read.
    "сямнаццаць": 17, "семнаццаць": 17,
    "васямнаццаць": 18, "дзевятнаццаць": 19}
_TENS: Dict[str, int] = {
    "дваццаць": 20, "трыццаць": 30, "сорак": 40, "пяцьдзясят": 50,
    "шэсцьдзясят": 60, "семдзесят": 70, "восемдзесят": 80, "дзевяноста": 90}
_HUNDREDS: Dict[str, int] = {
    "сто": 100, "дзвесце": 200, "трыста": 300, "чатырыста": 400,
    "пяцьсот": 500, "шэсцьсот": 600, "семсот": 700, "восемсот": 800,
    "дзевяцьсот": 900}

_WORDS: Dict[str, int] = {"нуль": 0}
for _table in (_ONES, _FEMININE, _TEENS, _TENS, _HUNDREDS):
    _WORDS.update(_table)


def _extract_be(text: str):
    """Compose a spelled Belarusian cardinal from its parts -- an optional
    hundred, an optional ten-or-teen, an optional unit: "сто дваццаць пяць" ==
    125.  Any unknown word fails the whole run, so the fold never invents a
    number out of a word that merely sits next to one."""
    words = text.split()
    if not words or any(w not in _WORDS for w in words):
        return False
    return float(sum(_WORDS[w] for w in words))


def _make_fold_be() -> Callable[[Tuple[Token, ...]], Tuple[Token, ...]]:
    return make_fold(NumberGrammar(
        is_number=lambda tok: tok.is_number or tok.text in _WORDS,
        extract=_extract_be))


# -- ordinals ----------------------------------------------------------------
# The ordinal stems come from the same Wiktionary numeral module; the case
# endings are the ordinary Belarusian adjective paradigm, verified against the
# declension tables of en.wiktionary's "першы", "другі", "трэці", "пяты",
# "шосты", "восьмы" and "дзявяты" (hard stems in -ы, plus the end-stressed
# "другі" and the soft "трэці"):
#
#     masculine nominative  першы    другі     трэці
#     masculine genitive    першага  другога   трэцяга
#     feminine  nominative  першая   другая    трэцяя
#     feminine  genitive    першай   другой    трэцяй
#     feminine  accusative  першую   другую    трэцюю
#
# Only the surfaces the constructions actually bind are tabulated: the
# masculine nominative for the quarter, the masculine genitive for the day of
# the month, and the three feminine forms the spoken clock names its hour with.
_STEMS = (("перш", 1), ("чацвёрт", 4), ("пят", 5), ("шост", 6), ("сём", 7),
          ("восьм", 8), ("дзявят", 9), ("дзясят", 10), ("адзінаццат", 11),
          ("дванаццат", 12), ("трынаццат", 13), ("чатырнаццат", 14),
          ("пятнаццат", 15), ("шаснаццат", 16), ("сямнаццат", 17),
          ("семнаццат", 17), ("васямнаццат", 18), ("дзевятнаццат", 19),
          ("дваццат", 20), ("трыццат", 30))


def _decline(ending: str, second: str, third: str) -> Dict[str, int]:
    out = {stem + ending: v for stem, v in _STEMS}
    out["друг" + second] = 2
    out["трэц" + third] = 3
    return out


#: masculine nominative -- the ``ORD`` slot of the quarter ("другі квартал").
_ORD_BE = _decline("ы", "і", "і")
#: masculine genitive -- the day of the month ("дваццаць пятага сакавіка").
_DAY_BE = _decline("ага", "ога", "яга")
#: the tens element of a compound day, which stays a bare cardinal and inflects
#: only its unit ("дваццаць пятага" == the twenty-fifth).
_TENS_BE = {"дваццаць": 20, "трыццаць": 30}
#: the three feminine forms the spoken clock names its hour with -- accusative
#: after "на" ("палова на пятую"), nominative in the subtractive idiom ("без
#: дзесяці першая") and genitive/locative in the dictionary's "палова пятай"
#: and in the "калі?" answer "а другой".
_HOUR_BE = {**_decline("ую", "ую", "юю"),
            **_decline("ая", "ая", "яя"),
            **_decline("ай", "ой", "яй")}
_HOUR_BE = {w: v for w, v in _HOUR_BE.items() if v <= 12}


def _rewrite(table: Dict[str, int]) -> Callable:
    frozen = dict(table)

    def rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        out, changed = [], False
        for t in tokens:
            if not t.is_number and t.text in frozen:
                v = frozen[t.text]
                out.append(Token(text=str(v), raw=str(v), index=t.index,
                                 is_number=True, value=v,
                                 char_start=t.char_start, char_end=t.char_end))
                changed = True
            else:
                out.append(t)
        return reindex(out) if changed else tokens

    return rewrite


def _day_rewrite(ords: Dict[str, int], tens: Dict[str, int]) -> Callable:
    """Fold the declined day-of-month ordinal to its digit, adding a compound
    ``tens + unit`` pair into the one number it names.  Folding only the unit
    and dropping the tens would answer the fifth of the month when the speaker
    said the twenty-fifth."""
    ords = dict(ords)
    tens = dict(tens)
    tens.update({w: v for w, v in ords.items() if v in (20, 30)})

    def _num(t: Token, value: int, end: Token = None) -> Token:
        return Token(text=str(value), raw=str(value), index=t.index,
                     is_number=True, value=value, char_start=t.char_start,
                     char_end=(end or t).char_end)

    def rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        out, i, n, changed = [], 0, len(tokens), False
        while i < n:
            t = tokens[i]
            if t.is_number:
                out.append(t)
                i += 1
                continue
            if t.text in tens and i + 1 < n \
                    and ords.get(tokens[i + 1].text, 0) in range(1, 10):
                out.append(_num(t, tens[t.text] + ords[tokens[i + 1].text],
                                tokens[i + 1]))
                i, changed = i + 2, True
                continue
            if t.text in ords:
                out.append(_num(t, ords[t.text]))
                i, changed = i + 1, True
                continue
            out.append(t)
            i += 1
        return reindex(out) if changed else tokens

    return rewrite


def _year_adverb_split(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Rewrite летась/сёлета as their relative determiner plus the year noun,
    so the one-word deictic reaches the same relative-period reading as the
    periphrastic wording."""
    out, changed = [], False
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


def _compose(*passes: Callable) -> Callable:
    def run(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        for p in passes:
            tokens = p(tokens)
        return tokens
    return run


fold_be = _compose(_year_adverb_split,
                   _day_rewrite(_DAY_BE, _TENS_BE),
                   _rewrite(_ORD_BE),
                   _make_fold_be(),
                   _rewrite(_HOUR_BE))
