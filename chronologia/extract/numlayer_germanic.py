"""Date words over the numtag number layer, shared by the Germanic folds.

numtag reads every number of the languages in
:data:`~chronologia.extract.numlayer.NUMTAG_LANGS`.  In some positions a
number word is a date word, and the date grammar must read the word: the
half or quarter of a clock hour ("halb acht", "kwart over drie"), the
deep-time scale ("vor zwei Millionen Jahren").  :class:`DateWords` names the
words of one language, and :func:`date_words` finds those positions from the
words around each mention and from the facts of the mention.  A language
module adds the positions of its own homographs and calls :func:`fold`.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from functools import lru_cache
from typing import (Callable, Collection, Dict, FrozenSet, Mapping, Optional,
                    Set, Tuple, Union)

from numtag import Kind
from ovos_spec_tools import expand, read_resource_file

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex
from chronologia.extract.numlayer import (_LOCALE_DIR, CountWords,
                                          counts_things, fold_mentions,
                                          mark_counts, scale_factor,
                                          scale_factors,
                                          withhold_split_counts)

#: The claimed words, the words a language keeps as numbers against a shared
#: claim, and the deep-time scale words with their factors, by token index.
Claims = Tuple[Set[int], Set[int], Dict[int, int]]


@lru_cache(maxsize=None)
def locale_words(lang: str, *prefixes: str) -> FrozenSet[str]:
    """The surfaces of every ``locale/<lang>/<prefix>*.voc`` file."""
    out = set()
    for path in sorted((_LOCALE_DIR / lang).glob("*.voc")):
        if path.name.startswith(prefixes):
            for template in read_resource_file(path):
                out.update(s.lower() for s in expand(template, {}))
    return frozenset(out)


_scale_factors = lru_cache(maxsize=None)(scale_factors)


@dataclass(frozen=True)
class DateWords:
    """The words of one language that the date grammar reads in a mention."""
    #: The chronologia locale.
    lang: str
    #: The clock fractions: "halb", "viertel", "dreiviertel".
    fractions: FrozenSet[str]
    #: The words that tell a count from a year.
    counts: CountWords


def count_words(lang: str) -> CountWords:
    """The :class:`CountWords` of a locale from its vocabulary files.

    The cues are the year words, the year prepositions and the since words.
    A since word makes a year of the number after it, and its until word makes
    a year of the number that closes the range.
    """
    since = locale_words(lang, "marker_since")
    until = locale_words(lang, "marker_until")
    return CountWords(
        scales=locale_words(lang, "scale_"),
        cues=(locale_words(lang, "marker_year_word", "marker_in.") | since),
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
        if word in words.fractions:
            # the half or quarter of a clock hour: "halb acht" is 7:30,
            # "viertel nach drei" is 3:15.  In a count the fraction is part
            # of the number and the mention is a cardinal
            if ends_mention(tok) and tok.mention.kind is not Kind.CARDINAL:
                claimed.add(i)
        elif word in roman and nxt in of:
            # the Roman Nones before the month; the ninth everywhere else
            claimed.add(i)
        elif (word in words.counts.scales
              and tok.mention.kind is not Kind.ORDINAL
              and tok.char_start != tok.mention.char_span[0]
              and not any(t.text in words.counts.scales
                          for t in tokens[i + 1:end])
              and (after in year_words
                   or (after in of and after2 in year_words))):
            # the deep-time SCALE ("vor sechsundsechzig Millionen Jahren"):
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
            # a scale noun that counts things after "von" ("eine Million von
            # Gründen")
            _claim_mention(tokens, i, claimed)
    return claimed, set(), scales


def merge_digit_ordinal(tokens: Tuple[Token, ...],
                        suffixes: Collection[str]) -> Tuple[Token, ...]:
    """Merge a digit and a lone ordinal suffix into one ordinal number token:
    Dutch "21e" and "5de" are the tokens "21" and "e"."""
    out = []
    i = 0
    n = len(tokens)
    while i < n:
        t = tokens[i]
        nxt = tokens[i + 1] if i + 1 < n else None
        if (t.is_number and nxt is not None and not nxt.is_number
                and nxt.text in suffixes):
            out.append(replace(t, raw=t.raw + nxt.raw, ordinal=True))
            i += 2
            continue
        out.append(t)
        i += 1
    return reindex(tuple(out))


def word_numbers(tokens: Tuple[Token, ...],
                 table: Mapping[str, Tuple[Union[int, float], bool]]
                 ) -> Tuple[Token, ...]:
    """Turn each word of ``table`` that numtag does not read into a number
    token: the word maps to its value and whether it is an ordinal."""
    return reindex(tuple(
        replace(t, text=str(table[t.text][0]), is_number=True,
                value=table[t.text][0], ordinal=table[t.text][1])
        if not t.is_number and t.mention is None and t.text in table else t
        for t in tokens))


def join_phrases(tokens: Tuple[Token, ...],
                 phrases: Mapping[Tuple[str, str], Union[int, float]]
                 ) -> Tuple[Token, ...]:
    """Join a folded number word and the word after it into one number token
    of the phrase value: Dutch "een paar" is 2."""
    out = []
    i = 0
    n = len(tokens)
    while i < n:
        t = tokens[i]
        nxt = tokens[i + 1] if i + 1 < n else None
        word = t.mention.text.lower() if t.mention is not None else None
        value = (phrases.get((word, nxt.text))
                 if t.is_number and nxt is not None and not nxt.is_number
                 else None)
        if value is None:
            out.append(t)
            i += 1
            continue
        out.append(replace(t, text=str(value), raw=str(value), value=value,
                           char_end=nxt.char_end, mention=None))
        i += 2
    return reindex(tuple(out))


def fold(tokens: Tuple[Token, ...], words: DateWords,
         extra: Optional[Callable[[Tuple[Token, ...]], Claims]] = None,
         table: Optional[Mapping[str, Tuple[Union[int, float], bool]]] = None,
         ordinal_suffixes: Collection[str] = (),
         phrases: Optional[Mapping[Tuple[str, str], Union[int, float]]] = None
         ) -> Tuple[Token, ...]:
    """Fold every mention into one number token, except the words the date
    grammar reads as words.  ``extra`` names the positions of the language's
    own homographs; its claims join those of :func:`date_words`.  ``table``
    holds the words numtag does not read, ``ordinal_suffixes`` the lone
    suffixes of a digit ordinal, and ``phrases`` the two-word phrases that
    name one number."""
    if ordinal_suffixes:
        tokens = merge_digit_ordinal(tokens, ordinal_suffixes)
    tokens = reindex(withhold_split_counts(tokens, words.counts.units,
                                           _scale_factors(words.lang)))
    claimed, kept, scales = date_words(tokens, words)
    if extra is not None:
        more, more_kept, more_scales = extra(tokens)
        claimed |= more
        kept |= more_kept
        scales.update(more_scales)
    folded = fold_mentions(tokens, words.lang, claimed - kept, scales)
    if table:
        folded = word_numbers(folded, table)
    if phrases:
        folded = join_phrases(folded, phrases)
    return mark_counts(folded, words.counts)
