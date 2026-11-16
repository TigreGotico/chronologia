"""The number layer: numtag mentions beside the token stream.

numtag is the one number reader for the languages in :data:`NUMTAG_LANGS`.
:func:`attach` tags the input text once and gives each token inside a
spelled mention a reference to that mention.  The tokens keep their words, so
the language fold can still read a word as a date word ("segunda" as Monday,
"meia" in a clock, "million" in deep time).  The fold names those date words,
and :func:`fold_mentions` turns every other mention into one number token.

chronologia keeps no number words and no number arithmetic for these
languages.  A value is numtag's digit string, converted once by
:func:`mention_number`.  When a date word cuts a mention in two, each side is
read again by numtag, on its own words.  A deep-time scale word is the one
cut that is not read again: the count before it is the mention value in
units of the scale word.
"""
from __future__ import annotations

import re
from bisect import bisect_right
from dataclasses import replace
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Collection, Dict, Mapping, Optional, Tuple, Union

from numtag import Form, Kind, NumberMention, Scale, tag_numbers
from ovos_spec_tools import expand, read_resource_file

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex

#: chronologia locale -> numtag language.  chronologia's ``pt`` locale is
#: European Portuguese.  A region tag goes to numtag as it is: ``pt-BR`` reads
#: the Brazilian lexicon, whose short scale makes "dois bilhões" 2*10^9.
NUMTAG_LANGS = {"pt": "pt-PT", "en": "en"}

_LOCALE_DIR = Path(__file__).resolve().parent.parent / "locale"


def reads(lang: str) -> bool:
    """Whether numtag reads the numbers of ``lang``, a locale or a region
    tag."""
    return lang.split("-")[0] in NUMTAG_LANGS


@lru_cache(maxsize=4096)
def mentions(text: str, lang: str) -> Tuple[NumberMention, ...]:
    """The spelled mentions of ``text``: WORDS and MIXED.

    DIGITS mentions are left out, because the tokenizer reads digits with the
    locale's decimal mark and its date literals ("3.5.2025", "15h30").  Roman
    numerals are left out too: :mod:`numfold_roman` reads one only next to a
    century word or after a year marker, so a bare "MMXX" stays a word.
    """
    return tuple(m for m in tag_numbers(text, NUMTAG_LANGS.get(lang, lang))
                 if m.form in (Form.WORDS, Form.MIXED))


def attach(tokens: Tuple[Token, ...], text: str,
           lang: str) -> Tuple[Token, ...]:
    """Give each token inside a mention of ``text`` that mention.

    ``lang`` is a chronologia locale or a region tag (``pt-BR``).
    """
    if not reads(lang):
        return tokens
    found = mentions(text, lang)
    if not found:
        return tokens
    # numtag gives the mentions in reading order and without overlap, so the
    # only mention that can hold a token is the last one that starts at or
    # before it
    starts = [m.char_span[0] for m in found]
    out = []
    for t in tokens:
        m = None
        if t.char_start is not None and t.char_end is not None:
            k = bisect_right(starts, t.char_start) - 1
            if k >= 0 and t.char_end <= found[k].char_span[1]:
                m = found[k]
        out.append(t if m is None else replace(t, mention=m))
    return tuple(out)


def scale_factors(lang: str) -> Dict[Optional[Scale], Dict[str, int]]:
    """The factors of the deep-time scale words of the locale ``lang``.

    The ``scale_<factor>.voc`` files name the words with one factor on both
    scales (key ``None``); ``scale_<factor>.short.voc`` and ``.long.voc`` name
    the factor of a billion-cognate on that scale.
    """
    out: Dict[Optional[Scale], Dict[str, int]] = {
        None: {}, Scale.SHORT: {}, Scale.LONG: {}}
    for path in sorted((_LOCALE_DIR / lang).glob("scale_*.voc")):
        factor, _, scale = path.stem[len("scale_"):].partition(".")
        table = out[Scale(scale) if scale else None]
        for template in read_resource_file(path):
            table.update((s.lower(), int(factor)) for s in expand(template, {}))
    return out


def scale_factor(word: str, mention: NumberMention,
                 factors: Mapping[Optional[Scale], Mapping[str, int]]
                 ) -> Optional[int]:
    """The factor of the scale word ``word`` inside ``mention``, on the scale
    numtag read the mention with."""
    if mention.number_scale is not None:
        factor = factors[mention.number_scale].get(word)
        if factor is not None:
            return factor
    return factors[None].get(word)


def mention_number(mention: NumberMention,
                   per: int = 1) -> Union[int, float]:
    """The mention value as the number a token carries, counted in units of
    ``per``: an ``int`` when it is whole, else a ``float``."""
    value = Fraction(mention.value) / per
    return int(value) if value.denominator == 1 else float(value)


def number_token(mention: NumberMention, first: Token, last: Token,
                 per: int = 1) -> Token:
    """One number token for ``mention``, over the source extent of the tokens
    from ``first`` to ``last``.  ``per`` counts the value in units of a scale
    word that stays outside the token."""
    num = mention_number(mention, per)
    return Token(text=str(num), raw=str(num), index=0, is_number=True,
                 value=num, char_start=first.char_start,
                 char_end=last.char_end,
                 ordinal=mention.kind is Kind.ORDINAL, mention=mention)


def covers(run: Tuple[Token, ...], mention: NumberMention) -> bool:
    """Whether ``run`` spans ``mention`` from its first to its last character."""
    return (run[0].char_start == mention.char_span[0]
            and run[-1].char_end == mention.char_span[1])


def reread(run: Tuple[Token, ...], lang: str) -> Tuple[Token, ...]:
    """Read ``run`` again with numtag, on its own words.

    A date word that cuts a mention, or a stream cut to a range endpoint,
    leaves a part of a mention.  The part is a new text for numtag: the raw
    words of the run, one space apart.  The mention a new number token carries
    has its offsets in that text.
    """
    ends = []
    pos = -1
    for t in run:
        pos += len(t.raw) + 1
        ends.append(pos)
    found = {m.char_span[0]: m
             for m in mentions(" ".join(t.raw for t in run), lang)}
    out = []
    i = 0
    n = len(run)
    while i < n:
        m = found.get(ends[i] - len(run[i].raw))
        j = i
        while m is not None and j < n and ends[j] <= m.char_span[1]:
            j += 1
        if m is None or j == i or ends[j - 1] != m.char_span[1]:
            out.append(run[i])
            i += 1
            continue
        out.append(number_token(m, run[i], run[j - 1]))
        i = j
    return tuple(out)


def withhold_split_counts(tokens: Tuple[Token, ...], units: Collection[str],
                          factors: Mapping[Optional[Scale], Mapping[str, int]]
                          ) -> Tuple[Token, ...]:
    """Withhold a count that a missing "e" splits in two, with its unit.

    The standard Portuguese form of 1200 is "mil e duzentos": the "e" joins
    the thousand and the hundred when the number ends in a round hundred
    (Cunha and Cintra, Nova Gramática do Português Contemporâneo, 1984,
    p. 372, quoted in Ciberdúvidas 34389: "1800 = mil e oitocentos").  The
    Gramática do Português (Fundação Calouste Gulbenkian), pp. 932-933, which
    Ciberdúvidas 8981 quotes for the same rule, was not consulted.  numtag
    reads "mil duzentos" as two numbers, 1000 and 200, so in "há mil
    duzentos anos" the count of years is not settled.

    Such a pair is a cardinal mention that ends in a scale word ("mil",
    "milhões", "thousand"), then a cardinal mention smaller than that scale,
    then a unit word, with no clause break between them.  The pair and its
    unit become one word token that binds no slot, so no part of the pair
    reads as a count and the unit does not read as one unit.  Two numbers that
    do not have this shape ("chapter one two days ago") stay as they are.
    """
    out = []
    n = len(tokens)
    i = 0
    while i < n:
        first = tokens[i].mention
        if first is None or first.kind is not Kind.CARDINAL:
            out.append(tokens[i])
            i += 1
            continue
        mid = i
        while mid < n and tokens[mid].mention is first:
            mid += 1
        second = tokens[mid].mention if mid < n else None
        end = mid
        while end < n and second is not None and tokens[end].mention is second:
            end += 1
        factor = scale_factor(tokens[mid - 1].text, first, factors)
        if (second is not None and second.kind is Kind.CARDINAL
                and factor is not None and Fraction(second.value) < factor
                and end < n and tokens[end].text in units
                and not any(t.break_before for t in tokens[mid:end + 1])):
            raw = " ".join(t.raw for t in tokens[i:end + 1])
            out.append(Token(text=raw, raw=raw, index=0,
                             char_start=tokens[i].char_start,
                             char_end=tokens[end].char_end))
            i = end + 1
        else:
            out.extend(tokens[i:mid])
            i = mid
    return tuple(out)


def is_count(tokens: Tuple[Token, ...], end: int, scales: Collection[str],
             cues: Collection[str], months: Collection[str]) -> bool:
    """Whether the mention that ends before ``end`` is a count, not a year.

    A mention that holds a scale word and has a word or another number after
    it is a count: "comprei mil ações ontem", "dois mil e quinhentos euros",
    "paguei mil na segunda", "I saw two thousand five hundred people
    yesterday".  A year takes a cue before it: a year word or "em", "in"
    ("em dois mil eu nasci"), or a month in the two words before ("março de
    dois mil e três").  A mention with nothing after it stays a number.
    """
    mention = tokens[end - 1].mention
    start = end - 1
    while start > 0 and tokens[start - 1].mention is mention:
        start -= 1
    if (end >= len(tokens) or mention is None
            or not any(w in scales
                       for w in re.split(r"[\s-]+", mention.text.lower()))):
        return False
    nxt = tokens[end]
    if not (nxt.is_number or nxt.mention is not None or nxt.text.isalpha()):
        return False
    return not (start > 0 and (tokens[start - 1].text in cues
                               or any(t.text in months
                                      for t in tokens[max(0, start - 2):start])))


def counts_things(tokens: Tuple[Token, ...], end: int,
                  scales: Collection[str], cues: Collection[str],
                  months: Collection[str], units: Collection[str]) -> bool:
    """Whether the mention that ends before ``end`` counts things.

    It is a count (:func:`is_count`) before a word that is neither a unit nor
    a number.  Its words stay words.  A count before a unit or a number folds
    into a number, because the duration reader reads it.
    """
    nxt = tokens[end] if end < len(tokens) else None
    return (is_count(tokens, end, scales, cues, months)
            and not nxt.is_number and nxt.mention is None
            and nxt.text not in units)


def mark_counts(tokens: Tuple[Token, ...], scales: Collection[str],
                cues: Collection[str], months: Collection[str]
                ) -> Tuple[Token, ...]:
    """Mark each folded number that :func:`is_count` reads as a count.

    The mark keeps the year and military-hour slots off it: "mil e quinhentas
    horas" counts hours.
    """
    return tuple(replace(t, count=True)
                 if t.is_number and is_count(tokens, i + 1, scales, cues,
                                             months) else t
                 for i, t in enumerate(tokens))


def fold_mentions(tokens: Tuple[Token, ...], lang: str,
                  claimed: Collection[int] = (),
                  scales: Optional[Mapping[int, int]] = None
                  ) -> Tuple[Token, ...]:
    """Fold each mention in ``tokens`` into one number token.

    ``claimed`` holds the indices of the words a date rule reads as words.
    A claimed word stays a word, and the parts of its mention on either side
    are read again (:func:`reread`).  A run of digit tokens stays as the
    tokenizer read it.

    ``scales`` maps a claimed deep-time scale word, the last scale word of
    its mention, to its factor.  The words before it are the count, and the
    count is the mention value in units of the scale word: "one million two
    hundred thousand years" counts 1200 thousands, "dois milhões e meio"
    counts 2.5 milhões.  The words after the scale word ("e meio") are in that
    count already, so the scale word token spans them.  When another claim
    cuts the count from the start of its mention, the count has no value and
    its words stay words.
    """
    out = []
    i = 0
    n = len(tokens)
    while i < n:
        m = tokens[i].mention
        if scales and i in scales:
            j = i + 1
            while j < n and tokens[j].mention is m and j not in claimed:
                j += 1
            out.append(replace(tokens[i], char_end=tokens[j - 1].char_end))
            i = j
            continue
        if m is None or i in claimed:
            out.append(tokens[i])
            i += 1
            continue
        j = i
        while j < n and tokens[j].mention is m and j not in claimed:
            j += 1
        run = tokens[i:j]
        if all(t.is_number for t in run):
            out.extend(run)
        elif covers(run, m):
            out.append(number_token(m, run[0], run[-1]))
        elif scales and j in scales and tokens[j].mention is m:
            if run[0].char_start == m.char_span[0]:
                # resolve_bp reads the count in the unit of the scale word, so
                # its span is one unit of the last digit said in that unit
                out.append(number_token(m, run[0], run[-1], per=scales[j]))
            else:
                out.extend(run)
        else:
            out.extend(reread(run, lang))
        i = j
    return reindex(out)
