"""Date words over the numtag number layer, shared by the Romance folds.

numtag reads every number of the Romance languages in
:data:`~chronologia.extract.numlayer.NUMTAG_LANGS`.  In some positions a
number word is a date word, and the date grammar must read the word: the
half or quarter of a clock hour ("las tres y media"), the deep-time scale
("hace dos millones de años"), the unit "segundos".  :class:`DateWords` names
the words of one language, and :func:`date_words` finds those positions from
the words around each mention and from the facts of the mention.  A language
module adds the positions of its own homographs and calls :func:`fold`.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Callable, Collection, Dict, FrozenSet, Optional, Set, Tuple

from numtag import ARTICLE_CONFIDENCE, Kind, Role

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex
from chronologia.extract.numlayer import (CountWords, counts_things,
                                          fold_mentions, locale_words,
                                          mark_counts, scale_factor,
                                          scale_factors,
                                          withhold_split_counts)

#: The claimed words, the words a language keeps as numbers against a shared
#: claim, and the deep-time scale words with their factors, by token index.
Claims = Tuple[Set[int], Set[int], Dict[int, int]]


_scale_factors = lru_cache(maxsize=None)(scale_factors)


@dataclass(frozen=True)
class DateWords:
    """The words of one language that the date grammar reads in a mention."""
    #: The chronologia locale.
    lang: str
    #: The clock fractions: "media", "cuarto", "tres cuartos".
    fractions: FrozenSet[str]
    #: The definite articles.  After one, a clock fraction that is also an
    #: ordinal is the ordinal: "el cuarto lunes".
    definite: FrozenSet[str]
    #: The articles a clock quarter keeps as a word: "e un quarto".
    quarter_articles: FrozenSet[str]
    #: The plural units of time that numtag also reads as an ordinal:
    #: "segundos".
    unit_nouns: FrozenSet[str]
    #: Their singular: a unit after a cardinal ("un segundo"), an ordinal
    #: everywhere else ("el segundo lunes").
    unit_ordinals: FrozenSet[str]
    #: The words that tell a count from a year.
    counts: CountWords
    #: Whether an indefinite article stays a word: "un giorno", "une
    #: semaine".  numtag reads it as one with a low confidence.
    articles_are_words: bool = False
    #: The prepositions after which the article-like word is the hour 1:
    #: it "alle una di notte".
    clock_prepositions: FrozenSet[str] = frozenset()


def count_words(lang: str, since: Collection[str] = ()) -> CountWords:
    """The :class:`CountWords` of a locale from its vocabulary files.

    The cues are the year words, the year prepositions and ``since``.  A
    since word makes a year of the number after it, and its until word makes
    a year of the number that closes the range.
    """
    until = locale_words(lang, "marker_until")
    return CountWords(
        scales=locale_words(lang, "scale_"),
        cues=(locale_words(lang, "marker_year_word", "marker_in.")
              | frozenset(since)),
        months=locale_words(lang, "month_"),
        units=locale_words(lang, "unit_"),
        currencies=locale_words(lang, "currency"),
        ranges={word: until for word in since})


def ends_mention(tok: Token) -> bool:
    return tok.mention is not None and tok.mention.char_span[1] == tok.char_end


def mention_end(tokens: Tuple[Token, ...], i: int) -> int:
    """The index after the last token of the mention of ``tokens[i]``."""
    j = i
    while j < len(tokens) and tokens[j].mention is tokens[i].mention:
        j += 1
    return j


def _alone(tok: Token) -> bool:
    """Whether the mention of ``tok`` is this one word."""
    return (tok.mention is not None
            and tok.mention.char_span == (tok.char_start, tok.char_end))


def _cardinal(tok: Token) -> bool:
    """Whether ``tok`` is a digit token or a word of a cardinal mention."""
    return tok.is_number or (tok.mention is not None
                             and tok.mention.kind is Kind.CARDINAL)


def _minus(tok: Token) -> bool:
    """Whether ``tok`` is the minus word of its mention: "moins" in "moins
    dix"."""
    return any(part.role is Role.MINUS
               and part.char_span == (tok.char_start, tok.char_end)
               for part in tok.mention.parts)


def _claim_mention(tokens: Tuple[Token, ...], i: int, claimed: Set[int]):
    """Claim every word of the mention that ends at ``tokens[i]``."""
    k = i
    while k >= 0 and tokens[k].mention is tokens[i].mention:
        claimed.add(k)
        k -= 1


def date_words(tokens: Tuple[Token, ...], words: DateWords) -> Claims:
    """The number words the date grammar reads as words, and the deep-time
    scale words with their factors."""
    claimed: Set[int] = set()
    scales: Dict[int, int] = {}
    factors = _scale_factors(words.lang)
    year_words = locale_words(words.lang, "marker_year_word")
    of = locale_words(words.lang, "marker_of")
    quarter_nouns = locale_words(words.lang, "marker_quarter_word")
    roman = locale_words(words.lang, "roman_anchor_")
    n = len(tokens)
    for i, tok in enumerate(tokens):
        if tok.mention is None or tok.is_number:
            continue
        nxt = tokens[i + 1].text if i + 1 < n else None
        nxt2 = tokens[i + 2].text if i + 2 < n else None
        end = mention_end(tokens, i)
        after = tokens[end].text if end < n else None
        after2 = tokens[end + 1].text if end + 1 < n else None
        word = tok.text
        prev = tokens[i - 1] if i > 0 else None
        if _minus(tok):
            # the clock direction, not a sign: "dix heures moins dix", "les
            # cinc menys deu".  No date reads a negative number
            claimed.add(i)
        elif word in words.unit_nouns or (
                word in words.unit_ordinals and _alone(tok)
                and prev is not None and _cardinal(prev)):
            # the unit of time, not the ordinal: "hace cinco segundos",
            # "dentro de un segundo"
            claimed.add(i)
        elif word in roman and _alone(tok) and nxt in of:
            # the Roman Nones before the month ("las nonas de julio"); the
            # ninth everywhere else ("las nonas jornadas")
            claimed.add(i)
        elif (words.articles_are_words and _alone(tok)
              and tok.mention.confidence <= ARTICLE_CONFIDENCE
              and not (prev is not None
                       and prev.text in words.clock_prepositions)):
            # the indefinite article: "un giorno", "une semaine"
            claimed.add(i)
        elif word in words.quarter_articles and nxt in words.fractions:
            claimed.add(i)
        elif word in words.fractions:
            # the half or quarter of a clock hour: "las tres y media" is 3.5,
            # "las dos menos cuarto" is 1:45.  After a definite article or
            # before the quarter noun the word is the ordinal ("el cuarto
            # lunes", "cuarto trimestre"), and in a count ("una docena y
            # media") the half is part of the number.  The unit of a compound
            # ordinal is the ordinal too: "o décimo cuarto mes" is the 14th
            compound = (tok.mention.kind is Kind.ORDINAL and prev is not None
                        and prev.mention is tok.mention and not _minus(prev))
            if ((prev is None or prev.text not in words.definite)
                    and nxt not in quarter_nouns and not compound
                    and ends_mention(tok)
                    and tok.mention.kind is not Kind.CARDINAL):
                claimed.add(i)
        elif (word in words.counts.scales and tok.char_start != tok.mention.char_span[0]
              and not any(t.text in words.counts.scales for t in tokens[i + 1:end])
              and (after in year_words
                   or (after in of and after2 in year_words))):
            # the deep-time SCALE ("hace sesenta y seis millones de años"):
            # the count before it is the mention value in units of this word
            factor = scale_factor(word, tok.mention, factors)
            if factor is not None:
                claimed.add(i)
                scales[i] = factor
        elif (ends_mention(tok) and after not in of
              and counts_things(tokens, end, words.counts)):
            # a count of things is no date number
            _claim_mention(tokens, i, claimed)
        elif (word in words.counts.scales and ends_mention(tok)
              and nxt in of
              and nxt2 not in words.counts.units
              and scale_factor(word, tok.mention, factors) not in (None, 1000)):
            # a scale noun that counts things after "de" ("un millón de
            # razones")
            _claim_mention(tokens, i, claimed)
    return claimed, set(), scales


def fold(tokens: Tuple[Token, ...], words: DateWords,
         extra: Optional[Callable[[Tuple[Token, ...]], Claims]] = None
         ) -> Tuple[Token, ...]:
    """Fold every mention into one number token, except the words the date
    grammar reads as words.  ``extra`` names the positions of the language's
    own homographs; its claims join those of :func:`date_words`."""
    tokens = reindex(withhold_split_counts(tokens, words.counts.units,
                                           _scale_factors(words.lang)))
    claimed, kept, scales = date_words(tokens, words)
    if extra is not None:
        more, more_kept, more_scales = extra(tokens)
        claimed |= more
        kept |= more_kept
        scales.update(more_scales)
    folded = fold_mentions(tokens, words.lang, claimed - kept, scales)
    return mark_counts(folded, words.counts)
