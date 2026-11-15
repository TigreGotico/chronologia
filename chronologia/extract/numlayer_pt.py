"""Portuguese date words over the numtag number layer.

numtag reads every Portuguese number (:mod:`chronologia.extract.numlayer`).
Some number words are also date words, and in some positions the date grammar
must read the word: "segunda" is Monday, "meia" is the half of a clock hour,
"milhões" is the SCALE of a deep-time phrase, "dez" is December.  This module
names those positions, from the words around each one and from the facts of
its mention.  Every other mention folds to its number.
"""
from __future__ import annotations

import os
from dataclasses import replace
from typing import Dict, FrozenSet, Set, Tuple

from numtag import Kind

from chronologia.extract.model import Token
from chronologia.extract.numfold_romance import (_LOCALE_ROOT,
                                                 _collapse_h_clock, _glue)
from chronologia.extract.numfold_engine import reindex
from chronologia.extract.numlayer import (fold_mentions, mention_number,
                                          scale_factor, scale_factors,
                                          split_counts)


def _voc(*prefixes: str) -> FrozenSet[str]:
    """The pt surfaces of every ``locale/pt/<prefix>*.voc`` file."""
    folder = os.path.join(_LOCALE_ROOT, "pt")
    out = set()
    for name in os.listdir(folder):
        if name.startswith(prefixes) and name.endswith(".voc"):
            with open(os.path.join(folder, name), encoding="utf-8") as fh:
                out.update(line.strip().lower() for line in fh
                           if line.strip() and not line.startswith("#"))
    return frozenset(out)


#: The feminine ordinals that are also weekday names, singular and plural:
#: "segunda" is the second and Monday, "quintas" the fifths and Thursdays.
_WEEKDAY_ORDINALS = frozenset({"segunda", "quarta", "quinta", "sexta",
                               "segundas", "quartas", "quintas", "sextas"})
#: The week nouns.  A weekday name does not take a following "semana", so
#: before one the homograph is the ordinal: "a segunda semana de março".
_WEEK_UNITS = _voc("unit_week")
#: The feminine weekday names.  Between an article and one of them, a
#: homograph is the ordinal: "a segunda terça-feira" is the second Tuesday.
_FEMININE_WEEKDAYS = frozenset({"segunda", "terça", "terca", "quarta",
                                "quinta", "sexta"})
_ORDINAL_ARTICLES = frozenset({"a", "na", "da", "à", "pela"})
#: The words that open the period after "a segunda terça-feira": "de 2026",
#: "de julho", "do mês que vem".  "deste" and "desta" open the anchor's own
#: period.  "da" is not listed: the feminine periods are "semana" and
#: "década", a week holds one of each weekday, and no order reads "da década".
_SCOPE_OPENERS = frozenset({"de", "do", "deste", "desta"})
#: The words that name a period that holds several of the same weekday.
_SCOPE_HEADS = _voc("month_", "scope_unit_", "unit_month", "unit_year")
#: A relative marker may stand between the opener and the period: "do
#: próximo mês".
_SCOPE_MARKERS = _voc("marker_next", "marker_last")
#: The definite articles and the calendar-quarter noun: the two positions
#: where "quarto" is the ordinal ("o quarto dia", "quarto trimestre").
_DEFINITE = frozenset({"o", "a", "os", "as"})
_QUARTER_NOUNS = _voc("marker_quarter_word")
#: The clock fractions ("meia", "meio", "quarto") and the plural "quartos" of
#: "três quartos de hora".
_CLOCK_FRACTIONS = _voc("clock_fraction_") | {"quartos"}
#: "um quarto" is the article and the clock quarter: Ciberdúvidas da Língua
#: Portuguesa, "as horas".
_QUARTER_ARTICLES = frozenset({"um", "uma"})
_QUARTERS = frozenset({"quarto", "quartos"})
#: "segundos" is the unit of time, never the plural ordinal.
_UNIT_NOUNS = frozenset({"segundos"})
#: The deep-time frame "NUM SCALE de anos": the SCALE slot binds the word.
_SCALES = _voc("scale_")
_THOUSANDS = _voc("scale_1000.")
_FACTORS = scale_factors("pt")
#: The units of time.  A unit after "N milhões de" makes the mention a count
#: of time ("dois mil milhões de segundos"), not a count of things.
_UNITS = _voc("unit_")
_YEAR_WORDS = _voc("marker_year_word")
_OF = _voc("marker_of")


def _number_in(tok: Token, low: float, high: float) -> bool:
    """A digit token, or a word inside a mention, whose whole value is in
    ``low..high``."""
    if tok.is_number:
        value = tok.value
    elif tok.mention is not None:
        value = mention_number(tok.mention)
    else:
        return False
    return (value is not None and float(value).is_integer()
            and low <= value <= high)


def _alone(tok: Token) -> bool:
    """Whether the mention of ``tok`` is this one word."""
    return (tok.mention is not None
            and tok.mention.char_span == (tok.char_start, tok.char_end))


def _ends_mention(tok: Token) -> bool:
    return tok.mention is not None and tok.mention.char_span[1] == tok.char_end


def _mention_end(tokens: Tuple[Token, ...], i: int) -> int:
    """The index after the last token of the mention of ``tokens[i]``."""
    j = i
    while j < len(tokens) and tokens[j].mention is tokens[i].mention:
        j += 1
    return j


def _last_scale(tokens: Tuple[Token, ...], i: int, end: int) -> bool:
    """Whether ``tokens[i]`` is the last scale word of its mention, which
    ends before ``end``."""
    return (tokens[i].text in _SCALES
            and not any(t.text in _SCALES for t in tokens[i + 1:end]))


def _period_follows(tokens: Tuple[Token, ...], k: int) -> bool:
    """Whether ``tokens[k:]`` opens with a period: a year, or a scope head
    behind an optional relative marker."""
    if k < len(tokens) and tokens[k].text in _SCOPE_MARKERS:
        k += 1
    return k < len(tokens) and (_number_in(tokens[k], 1000, float("inf"))
                                or tokens[k].text in _SCOPE_HEADS)


def _ordinal_weekday(tokens: Tuple[Token, ...], i: int) -> bool:
    """Whether the weekday homograph at ``i`` is the ordinal.

    Priberam s.v. "segundo": "adjetivo numeral ... 1. Que ou o que está logo
    depois do primeiro."  Two positions take the ordinal.  Before a week noun
    ("a segunda semana de março").  Between an article and a feminine weekday
    name, with nothing written between them, when the period it counts in
    follows ("a segunda terça-feira de julho").  A list of weekdays keeps its
    weekday reading: "na segunda terça e quarta" is Monday, Tuesday and
    Wednesday, and in "na segunda terça de manhã" no period follows.
    """
    tok = tokens[i]
    nxt = tokens[i + 1] if i + 1 < len(tokens) else None
    if nxt is None or tok.text not in _FEMININE_WEEKDAYS:
        return False
    if nxt.text in _WEEK_UNITS:
        return True
    if i == 0 or tokens[i - 1].text not in _ORDINAL_ARTICLES:
        return False
    adjacent = (tok.char_end is not None and nxt.char_start is not None
                and nxt.char_start - tok.char_end == 1)
    j = i + 2
    if j < len(tokens) and tokens[j].text == "feira":
        j += 1
    return (nxt.text in _FEMININE_WEEKDAYS and adjacent
            and j < len(tokens) and tokens[j].text in _SCOPE_OPENERS
            and _period_follows(tokens, j + 1))


def _date_words(tokens: Tuple[Token, ...]
                ) -> Tuple[Set[int], Set[int], Dict[int, int]]:
    """The indices of the number words the date grammar reads as words, of
    the homographs it reads as ordinals by their position, and of the
    deep-time scale words with their factors."""
    claimed = set()
    ordinals = set()
    scales = {}
    n = len(tokens)
    for i, tok in enumerate(tokens):
        if tok.mention is None or tok.is_number:
            continue
        prev = tokens[i - 1].text if i > 0 else None
        nxt = tokens[i + 1].text if i + 1 < n else None
        nxt2 = tokens[i + 2].text if i + 2 < n else None
        end = _mention_end(tokens, i)
        after = tokens[end].text if end < n else None
        after2 = tokens[end + 1].text if end + 1 < n else None
        word = tok.text
        if word in _WEEKDAY_ORDINALS and _alone(tok):
            (ordinals if _ordinal_weekday(tokens, i) else claimed).add(i)
        elif word in _UNIT_NOUNS:
            claimed.add(i)
        elif word in _QUARTER_ARTICLES and nxt in _QUARTERS:
            claimed.add(i)
        elif word in _CLOCK_FRACTIONS:
            if word == "quarto" and (prev in _DEFINITE
                                     or nxt in _QUARTER_NOUNS):
                ordinals.add(i)
            elif _ends_mention(tok) and tok.mention.kind is not Kind.CARDINAL:
                # the half or quarter of a clock hour: "às três e meia" is
                # 3.5, "meio-dia e quarto" holds "quarto".  In a count ("uma
                # dúzia e meia", 18) numtag reads the half as part of the
                # number, and the mention is a cardinal.
                claimed.add(i)
        elif word == "dez":
            # the CLDR abbreviation of "dezembro", in the month slot of "N de
            # MONTH": "3 de dez".  "dez de dezembro" keeps the numeral.
            if (i >= 2 and prev == "de"
                    and _number_in(tokens[i - 2], 1, 31)):
                claimed.add(i)
        elif word == "nonas":
            # the Roman Nones before the month ("as nonas de julho"); the
            # ninth everywhere else ("as nonas semanas")
            if nxt in _OF:
                claimed.add(i)
        elif (_last_scale(tokens, i, end)
              and tok.char_start != tok.mention.char_span[0]
              and (after in _YEAR_WORDS
                   or (after in _OF and after2 in _YEAR_WORDS))):
            # the deep-time SCALE ("sessenta e seis milhões de anos", "dois
            # milhões e meio de anos"); the count before it is the mention
            # value in units of this word.  A scale word that opens its
            # mention has no count before it: "mil e duzentos" is 1200
            factor = scale_factor(word, tok.mention, _FACTORS)
            if factor is not None:
                claimed.add(i)
                scales[i] = factor
        elif (word in _SCALES and word not in _THOUSANDS and _ends_mention(tok)
              and nxt in _OF and nxt2 not in _UNITS):
            # a scale noun that counts things after "de" ("um milhão de
            # razões"): the count of things is no date number, so every word
            # of its mention stays a word
            k = i
            while k >= 0 and tokens[k].mention is tok.mention:
                claimed.add(k)
                k -= 1
    return claimed, ordinals, scales


def fold_pt(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """The Portuguese number fold: every numtag mention becomes one number
    token, except the words the date grammar reads as words.

    Portuguese writes the digital clock as "15h", "15h30", "9h", so that
    literal folds to an ``HH:MM`` clock token first; the abbreviations the
    tokenizer splits ("a.c.", "meio-dia") are glued back into one word.
    """
    tokens = reindex(_glue(_collapse_h_clock(tokens)))
    claimed, ordinals, scales = _date_words(tokens)
    claimed |= split_counts(tokens, _UNITS)
    # a homograph read as an ordinal by its position keeps its written word,
    # so a mention's text shows "o quarto trimestre"
    words = {(tokens[i].char_start, tokens[i].char_end): tokens[i].raw
             for i in ordinals}
    return tuple(replace(t, raw=words[(t.char_start, t.char_end)])
                 if t.is_number and (t.char_start, t.char_end) in words else t
                 for t in fold_mentions(tokens, "pt", claimed, scales))
