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
import json
from bisect import bisect_right
from dataclasses import dataclass, field, replace
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import (Collection, Dict, FrozenSet, List, Mapping, Optional,
                    Tuple, Union)

from numtag import Form, Kind, NumberMention, Scale, tag_numbers

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex

#: chronologia locale -> numtag language.  chronologia's ``pt`` locale is
#: European Portuguese and its ``fr`` locale the French of France.  A region
#: tag goes to numtag as it is: ``pt-BR`` reads the Brazilian lexicon, whose
#: short scale makes "dois bilhões" 2*10^9, and ``fr-BE`` reads "septante".
NUMTAG_LANGS = {"pt": "pt-PT", "en": "en", "es": "es", "gl": "gl", "ca": "ca",
                "it": "it", "fr": "fr-FR", "de": "de", "nl": "nl", "da": "da",
                "sv": "sv", "nb": "nb", "nn": "nn", "fy": "fy", "ar": "ar", "el": "el",
                "fa": "fa", "he": "he", "id": "id", "kab": "kab", "ms": "ms", "et": "et",
                "fi": "fi", "hu": "hu", "eu": "eu", "tr": "tr", "az": "az", "an": "an", "ast": "ast",
                "mwl": "mwl", "oc": "oc", "ro": "ro", "bg": "bg", "cs": "cs", "hr": "hr",
                "pl": "pl", "ru": "ru", "sk": "sk", "sl": "sl", "uk": "uk"}

_LOCALE_DIR = Path(__file__).resolve().parent.parent / "locale"


VOCAB_FORMAT_VERSION = 1


def _unique_keys(pairs):
    """``object_pairs_hook`` that refuses an object with a repeated key."""
    keys = [key for key, _ in pairs]
    if len(set(keys)) != len(keys):
        repeated = sorted({key for key in keys if keys.count(key) > 1})
        raise ValueError(f"repeated key(s) {repeated}")
    return dict(pairs)


def read_vocabulary(lang_dir) -> Dict[str, List[str]]:
    """The surfaces of ``<lang_dir>/vocab.json``, by resource base name."""
    path = Path(lang_dir) / "vocab.json"
    with open(path, encoding="utf-8") as fh:
        try:
            data = json.load(fh, object_pairs_hook=_unique_keys)
        except ValueError as error:
            raise ValueError(f"{path}: {error}") from error
    version = data.get("format_version")
    if type(version) is not int or version != VOCAB_FORMAT_VERSION:
        raise ValueError(
            f"{path}: format_version {version!r} is not "
            f"supported, expected {VOCAB_FORMAT_VERSION}")
    return data["words"]


@lru_cache(maxsize=None)
def vocabulary(lang: str) -> Dict[str, List[str]]:
    """The surfaces of ``locale/<lang>/vocab.json``, by resource base name."""
    return read_vocabulary(_LOCALE_DIR / lang)


@lru_cache(maxsize=None)
def locale_words(lang: str, *prefixes: str) -> FrozenSet[str]:
    """The lower-cased surfaces of every vocabulary of ``lang`` whose base
    name starts with one of ``prefixes``.  The test runs on the base name with a
    dot appended, so a prefix that ends in a dot matches that base name and the
    dotted names under it: ``marker_in.`` names ``marker_in`` and no
    ``marker_in_*``, and ``scale_1000.`` names ``scale_1000`` and
    ``scale_1000.short``."""
    return frozenset(
        s.lower() for base, surfaces in vocabulary(lang).items()
        if (base + ".").startswith(prefixes) for s in surfaces)


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
    try:
        found = tag_numbers(text, NUMTAG_LANGS.get(lang, lang))
    except IndexError:
        # numtag 0.15.3a1 raises on a number and a joiner at the end of
        # the text ("zwei und", "két és").  The text then reads no number.
        return ()
    return tuple(m for m in found if m.form in (Form.WORDS, Form.MIXED))


#: The punctuation that ends a clause.  A cue before it is no cue for a
#: number after it: "esperei até. Dois mil turistas chegaram ontem".
_CLAUSE_BREAK = re.compile(r"[.,;:!?]")
#: The place of a whole mention in :attr:`Token.before` and
#: :attr:`Token.after`.
NUMBER = "\x00"
#: The place of a currency symbol in the words after a mention, which the
#: tokenizer drops.
SYMBOL = "\x01"


def _same_clause(left: Token, right: Token, text: str) -> bool:
    """Whether no clause punctuation of ``text`` stands between two tokens."""
    return (left.char_end is not None and right.char_start is not None
            and not _CLAUSE_BREAK.search(text, left.char_end,
                                         right.char_start))


def words_after(tokens: Tuple[Token, ...], end: int) -> Tuple[str, ...]:
    """The words after the mention that ends before ``tokens[end]``, in its
    clause: a currency symbol (:data:`SYMBOL`) right after the mention, then
    up to two words, each with its own symbol.  A word is its text, but three
    capitals keep their case, for an ISO 4217 code ("USD")."""
    out = []
    if end > 0 and tokens[end - 1].trailing_currency:
        out.append(SYMBOL)
    for tok in tokens[end:end + 2]:
        if tok.break_before:
            break
        out.append(tok.text.upper() if tok.upper and len(tok.text) == 3
                   else tok.text)
        if tok.trailing_currency:
            out.append(SYMBOL)
    return tuple(out[:3])


def _words_before(tokens: Tuple[Token, ...], i: int, text: str
                  ) -> Tuple[str, ...]:
    """The texts of the up to three tokens before ``tokens[i]`` in its
    clause of ``text``."""
    out = []
    for j in range(i - 1, max(-1, i - 4), -1):
        if not _same_clause(tokens[j], tokens[j + 1], text):
            break
        out.append(tokens[j].text)
    return tuple(reversed(out))


def _closes_range(tokens: Tuple[Token, ...], last_end: int, i: int,
                  text: str) -> bool:
    """Whether the mention that starts at ``tokens[i]`` can close the range
    of the mention that ends at ``tokens[last_end]``.

    One or two words stand between the mentions, the last of them the word
    that closes the range.  No clause mark stands between the closing word and
    the second mention, nor between the first mention and the closing word,
    except one comma before the closing word: "from two thousand, to three
    thousand dollars" (ruling 25).
    """
    if not 2 <= i - last_end <= 3 or not _same_clause(tokens[i - 1],
                                                      tokens[i], text):
        return False
    for j in range(last_end, i - 1):
        left, right = tokens[j], tokens[j + 1]
        if left.char_end is None or right.char_start is None:
            return False
        gap = text[left.char_end:right.char_start]
        if j == i - 2:
            gap = gap.replace(",", "", 1)
        if _CLAUSE_BREAK.search(gap):
            return False
    return True


def attach(tokens: Tuple[Token, ...], text: str,
           lang: str) -> Tuple[Token, ...]:
    """Give each token inside a mention of ``text`` that mention.

    ``lang`` is a chronologia locale or a region tag (``pt-BR``).  The first
    token of each mention also gets the words before it in its clause
    (:attr:`Token.before`).  A mention one or two words after another mention
    (:func:`_closes_range`) gets that mention's words, :data:`NUMBER` and the
    words between: "from two thousand to two thousand and ten" gives the
    second mention ("from", NUMBER, "to"), and "from two thousand dollars to
    three thousand" gives it ("from", NUMBER, "dollars", "to").  The first
    mention then gets the closing word, :data:`NUMBER` and the word after the
    second mention (:attr:`Token.after`): "between two thousand and three
    thousand dollars" gives the first mention ("and", NUMBER, "dollars").
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
    # the words before the last mention, the index of its first token and
    # the index of its last token
    last_before, last_first, last_end = None, None, None
    # the first token of a mention and of the mention that closes its range
    pairs = []
    for i, t in enumerate(tokens):
        m = None
        if t.char_start is not None and t.char_end is not None:
            k = bisect_right(starts, t.char_start) - 1
            if k >= 0 and t.char_end <= found[k].char_span[1]:
                m = found[k]
        if m is None:
            out.append(t)
            continue
        if t.char_start == m.char_span[0]:
            before = _words_before(tokens, i, text)
            if (last_end is not None
                    and _closes_range(tokens, last_end, i, text)):
                # a cue of up to three words, the mention, up to two words
                # and the closing word: a run of mentions keeps a window of
                # fixed length
                before = (last_before + (NUMBER,) + tuple(
                    w.text for w in tokens[last_end + 1:i]))[-6:]
                pairs.append((last_first, i))
            last_before, last_first = before, i
            out.append(replace(t, mention=m, before=before))
        else:
            out.append(replace(t, mention=m))
        last_end = i
    for first, second in pairs:
        end, mention = second, out[second].mention
        while end + 1 < len(out) and out[end + 1].mention is mention:
            end += 1
        out[first] = replace(out[first],
                             after=(tokens[second - 1].text, NUMBER)
                             + words_after(tokens, end + 1))
    return tuple(out)


def scale_factors(lang: str) -> Dict[Optional[Scale], Dict[str, int]]:
    """The factors of the deep-time scale words of the locale ``lang``.

    The ``scale_<factor>`` vocabularies name the words with one factor on both
    scales (key ``None``); ``scale_<factor>.short`` and ``.long`` name the
    factor of a billion-cognate on that scale.
    """
    out: Dict[Optional[Scale], Dict[str, int]] = {
        None: {}, Scale.SHORT: {}, Scale.LONG: {}}
    for base, surfaces in vocabulary(lang).items():
        if base.startswith("scale_"):
            factor, _, scale = base[len("scale_"):].partition(".")
            out[Scale(scale) if scale else None].update(
                (s.lower(), int(factor)) for s in surfaces)
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
                 ordinal=mention.kind is Kind.ORDINAL, mention=mention,
                 before=first.before, after=first.after,
                 trailing_currency=last.trailing_currency)


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


@dataclass(frozen=True)
class CountWords:
    """The words of a language that tell a count from a year."""

    #: The scale words: only a mention with one can be a count.
    scales: Collection[str]
    #: The words before a mention that make it a year: "in", "since".
    cues: Collection[str]
    #: The months a year follows.
    months: Collection[str]
    #: The units of time.  A count before a unit folds into a number.
    units: Collection[str]
    #: The currency names.  A count before one keeps its words.
    currencies: Collection[str] = frozenset()
    #: The ISO 4217 codes of the currencies, in capitals.
    codes: Collection[str] = frozenset()
    #: The words that qualify a currency name: "US", "more".
    qualifiers: Collection[str] = frozenset()
    #: For a word that opens a closed range ("from", "de"), the words that
    #: close it ("to", "a").  After a cue the mention after the closing word is
    #: a year too.
    ranges: Mapping[str, Collection[str]] = field(default_factory=dict)
    #: The same for a word that opens a range of amounts and is no year cue
    #: ("entre" and "e"): two numbers in such a range count things.
    amounts: Mapping[str, Collection[str]] = field(default_factory=dict)

    def measures(self, word: str) -> bool:
        """Whether ``word`` is a unit or a currency."""
        return word in self.units or word in self.currencies

    def measured(self, words: Tuple[str, ...]) -> bool:
        """Whether the words after a mention (:func:`words_after`) measure it.

        A unit, a currency name, a currency symbol or an ISO 4217 code
        measures it, and so does a currency after a word that qualifies it:
        "US dollars", "three thousand more dollars".
        """
        if not words:
            return False
        first = words[0]
        if (first == SYMBOL or self.measures(first.lower())
                or first in self.codes):
            return True
        return (first in self.qualifiers and len(words) > 1
                and (words[1] == SYMBOL or words[1].lower() in self.currencies
                     or words[1] in self.codes))

    def closes(self, opener: Tuple[str, ...], closer: str) -> bool:
        """Whether a range word stands in ``opener`` and any closing word
        closes it, so "between two thousand to three thousand dollars" is a
        range."""
        closing = [*self.ranges.values(), *self.amounts.values()]
        return (any(w in self.ranges or w in self.amounts for w in opener)
                and any(closer in c for c in closing))

    def closes_amounts(self, opener: Tuple[str, ...], closer: str) -> bool:
        """Whether a word that opens a range of amounts stands in ``opener``
        and ``closer`` closes it."""
        return any(closer in self.amounts[w] for w in opener
                   if w in self.amounts)


def year_cue(before: Tuple[str, ...], words: CountWords) -> Optional[str]:
    """The cue at the end of ``before``, or ``None``.

    A cue can be up to three words long.  The word between two mentions is a
    cue when the first mention has a range cue that it closes: "to" after
    "from two thousand".
    """
    for k in range(1, len(before) + 1):
        cue = " ".join(before[-k:])
        if cue in words.cues:
            return cue
    if len(before) > 2 and before[-2] == NUMBER:
        opener = year_cue(before[:-2], words)
        if opener is not None and before[-1] in words.ranges.get(opener, ()):
            return before[-1]
    return None


def _mention_start(tokens: Tuple[Token, ...], end: int) -> int:
    """The index of the first token of the mention that ends before
    ``end``."""
    start = end - 1
    while start > 0 and tokens[start - 1].mention is tokens[end - 1].mention:
        start -= 1
    return start


def is_count(tokens: Tuple[Token, ...], end: int, words: CountWords) -> bool:
    """Whether the mention that ends before ``end`` is a count, not a year.

    A mention that holds a scale word and has a word or another number after
    it is a count: "comprei mil ações ontem", "dois mil e quinhentos euros",
    "paguei mil na segunda", "I saw two thousand five hundred people
    yesterday".  A scale word with no number before it ("mil") names no year
    either.  A year takes a cue before it: a year word or "em", "in" ("em
    dois mil eu nasci"), a range or since word ("since two thousand and ten
    I have lived here", "a partir de dois mil e dez"), or a month in the two
    words before ("março de dois mil e três").  The cue stands in the same
    clause (:func:`year_cue`), and a range endpoint folded alone reads it
    from the whole utterance (:attr:`Token.before`).  A unit or a currency
    after the mention makes it a count after any cue: "paguei até dois mil
    euros na segunda".  Any other mention with nothing after it stays a
    number.
    """
    mention = tokens[end - 1].mention
    start = _mention_start(tokens, end)
    said = re.split(r"[\s-]+", mention.text.lower()) if mention else []
    if not any(w in words.scales for w in said):
        return False
    nxt = tokens[end] if end < len(tokens) else None
    if words.measured(words_after(tokens, end)):
        return True
    # a range endpoint is folded on its own, so the words before a mention
    # come from the whole utterance; a part of a mention read again takes
    # them from the stream, up to a clause break
    before = tokens[start].before
    if before is None:
        before = ()
        j = start
        while j > 0 and len(before) < 3 and not tokens[j].break_before:
            before = (tokens[j - 1].text,) + before
            j -= 1
    cue = year_cue(before, words)
    after = tokens[start].after or ()
    # a mention that closes a range has the opening words, then NUMBER and
    # the words between the mentions, the last of them the closing word
    opener, gap = before, ()
    if NUMBER in before:
        at = len(before) - 1 - before[::-1].index(NUMBER)
        opener, gap = before[:at], before[at + 1:]
    # a unit after either number of a closed range measures both: "between
    # two thousand and three thousand dollars", "from two thousand dollars to
    # three thousand" (ruling 24)
    if (len(after) >= 3 and words.closes(opener, after[0])
            and words.measured(after[2:])):
        return True
    if (gap and words.closes(opener, gap[-1])
            and any(words.measures(w) for w in gap[:-1])):
        return True
    if cue is not None or any(w in words.months for w in before[-2:]):
        return False
    # a range that no year cue opens holds two amounts: "entre dois mil e
    # três mil"
    if ((len(after) >= 2 and words.closes_amounts(opener, after[0]))
            or (len(gap) == 1 and words.closes_amounts(opener, gap[0]))):
        return True
    if nxt is None:
        # a range endpoint folded alone has a connector after it in the
        # utterance, and a word after the range: "vieram entre dois mil e
        # três mil turistas ontem"
        return len(said) == 1 or len(after) >= 3
    return nxt.is_number or nxt.mention is not None or nxt.text.isalpha()


def counts_things(tokens: Tuple[Token, ...], end: int,
                  words: CountWords) -> bool:
    """Whether the mention that ends before ``end`` counts things.

    It is a count (:func:`is_count`) with no word after it, or before a word
    that is neither a unit nor a number.  Its words stay words.  A count
    before a unit or a number folds into a number, because the duration
    reader reads it, and so does the first number of a range of units:
    "between two thousand and three thousand days".
    """
    nxt = tokens[end] if end < len(tokens) else None
    after = tokens[_mention_start(tokens, end)].after or ()
    if len(after) >= 3 and after[2] in words.units:
        return False
    return (is_count(tokens, end, words)
            and (nxt is None or not (nxt.is_number or nxt.mention is not None
                                     or nxt.text in words.units)))


def mark_counts(tokens: Tuple[Token, ...], words: CountWords
                ) -> Tuple[Token, ...]:
    """Mark each folded number that :func:`is_count` reads as a count.

    The mark keeps the year and military-hour slots off it: "mil e quinhentas
    horas" counts hours.
    """
    return tuple(replace(t, count=True)
                 if t.is_number and is_count(tokens, i + 1, words) else t
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
