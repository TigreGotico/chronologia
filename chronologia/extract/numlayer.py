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
from dataclasses import dataclass, field, replace
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import (Callable, Collection, Dict, FrozenSet, Mapping,
                    Optional, Set, Tuple, Union)

from numtag import Form, Kind, NumberMention, Scale, tag_numbers
from ovos_spec_tools import expand, read_resource_file

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex, run_extent

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
                "pl": "pl", "ru": "ru", "sk": "sk", "sl": "sl", "uk": "uk",
                "bn": "bn"}

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


def voc_file_words(lang: str, name: str) -> FrozenSet[str]:
    """The surfaces of the file ``name`` of the locale ``lang``, as written."""
    return frozenset(
        s for template in read_resource_file(_LOCALE_DIR / lang / name)
        for s in expand(template, {}))


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
            # the word is in no mention of the new text, so a table of words
            # numtag does not read may still read it ("দু" of "দুটো")
            out.append(replace(run[i], mention=None))
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


# -- Date words of the languages numtag reads -------------------------------

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


# -- Token passes that prepare a stream for the number fold ----------------

# abbreviations the tokenizer shatters on their dots/hyphens ("a.c." -> a,c;
# "meio-dia" -> meio,dia).  The fold glues the fragments back into the single
# token a marker/landmark slot binds.  Keyed by the fragment tuple, longest
# match first; shared across the Romance locales (surfaces are the same).
_ABBREVIATION_GLUE = {
    ("a", "e", "c"): "aec", ("a", "c"): "ac", ("d", "c"): "dc",
    ("e", "c"): "ec", ("a", "p"): "ap",
    ("meio", "dia"): "meiodia", ("meia", "noite"): "meianoite",
    ("migdia",): "migdia",
}


def glue_abbreviations(tokens):
    seqs = sorted(_ABBREVIATION_GLUE, key=len, reverse=True)
    out = []
    i = 0
    n = len(tokens)
    while i < n:
        for seq in seqs:
            k = len(seq)
            if tuple(t.text for t in tokens[i:i + k]) == seq:
                raw = "".join(t.raw for t in tokens[i:i + k])
                cs, ce = run_extent(tokens[i:i + k])
                out.append(Token(text=_ABBREVIATION_GLUE[seq], raw=raw, index=0,
                                 char_start=cs, char_end=ce))
                i += k
                break
        else:
            out.append(tokens[i])
            i += 1
    return tuple(out)


def elision_split(tokens, proclitics):
    """Split a leading elided proclitic ("d'annees" -> "d", "annees").

    Only the closed proclitic set splits, so a lexical apostrophe inside a
    word ("aujourd'hui") stays whole."""
    out = []
    for t in tokens:
        head, sep, tail = t.text.partition("'")
        if not sep:
            head, sep, tail = t.text.partition("’")
        if sep and head in proclitics and tail:
            # keep each half's character extent into the original utterance --
            # the proclitic occupies the head chars, the elided word the tail
            # chars past the apostrophe -- so a mention built on the split word
            # ("d'abril") still recovers a char span instead of ``None``.
            cs, ce = t.char_start, t.char_end
            if cs is None or ce is None:
                h_start = h_end = w_start = None
            else:
                h_start, h_end, w_start = cs, cs + len(head), ce - len(tail)
            out.append(Token(text=head, raw=head, index=0,
                             char_start=h_start, char_end=h_end))
            out.append(Token(text=tail, raw=tail, index=0,
                             char_start=w_start, char_end=ce if cs is not None
                             else None))
        else:
            out.append(t)
    return reindex(out)


def collapse_phrase(tokens, words, surface):
    """Collapse a fixed multiword sequence ("il y a") to one token."""
    n = len(words)
    out = []
    i = 0
    while i < len(tokens):
        if [t.text for t in tokens[i:i + n]] == words:
            raw = " ".join(t.raw for t in tokens[i:i + n])
            cs, ce = run_extent(tokens[i:i + n])
            out.append(Token(text=surface, raw=raw, index=0,
                             char_start=cs, char_end=ce))
            i += n
        else:
            out.append(tokens[i])
            i += 1
    return reindex(out)


def collapse_h_clock(tokens, governors=frozenset(), followers=frozenset()):
    """Fold French/Occitan "20h30"/"20h" into one ``HH:MM`` clock literal.

    ``governors`` and ``followers`` keep "h" a word: after a counted-offset
    preposition ("dans 2 h") it is the unit of a length, and before a clock
    direction ("9 h et quart") it is the hour word the direction counts from.
    Both readings come from "h" being the symbol of "heure", so the grammar
    reads them as it reads "dans 2 heures" and "9 heures et quart".
    """
    out = []
    i = 0
    n = len(tokens)
    while i < n:
        t = tokens[i]
        nxt = tokens[i + 1] if i + 1 < n else None
        nn = tokens[i + 2] if i + 2 < n else None
        spared = ((out and out[-1].text in governors)
                  or (nn is not None and nn.text in followers))
        if (not spared
                and t.is_number and t.value is not None and 0 <= t.value <= 24
                and float(t.value).is_integer() and nxt is not None
                and nxt.text == "h"):
            if (nn is not None and nn.is_number and nn.value is not None
                    and 0 <= nn.value <= 59 and float(nn.value).is_integer()):
                lit = "%d:%02d" % (int(t.value), int(nn.value))
                cs, ce = run_extent(tokens[i:i + 3])
                out.append(Token(text=lit, raw=lit, index=0,
                                 char_start=cs, char_end=ce))
                i += 3
                continue
            lit = "%d:00" % int(t.value)
            cs, ce = run_extent(tokens[i:i + 2])
            out.append(Token(text=lit, raw=lit, index=0,
                             char_start=cs, char_end=ce))
            i += 2
            continue
        out.append(t)
        i += 1
    return reindex(out)


def drop_digit_suffix(tokens, suffixes):
    """Drop a lone ordinal-suffix word after a digit ("1 er" -> 1)."""
    out = []
    i = 0
    n = len(tokens)
    while i < n:
        t = tokens[i]
        nxt = tokens[i + 1] if i + 1 < n else None
        if (t.is_number and nxt is not None and not nxt.is_number
                and nxt.text in suffixes):
            out.append(replace(t, ordinal=True))
            i += 2
            continue
        out.append(t)
        i += 1
    return reindex(out)


def collapse_marked_h_clock(tokens, markers) -> Tuple[Token, ...]:
    """Fold "21h30"/"20h" into an ``HH:MM`` literal behind a clock marker.

    Italian, Romanian, Asturian, Greek and Swedish write the hour-letter
    notation only where a clock marker already says a clock follows -- "alle
    21h30", "la ora 21h30", "a les 21h30", "στις 21h30", "kl 21h30".  A bare
    "21h30" inside a sentence in those languages is a duration, a coordinate
    or a citation to a French source, so it is not folded there.  Said alone,
    the whole utterance is the clock and it folds.

    ``markers`` is the closed set of surfaces that may sit immediately before
    the hour, taken from that locale's own ``marker_at`` and ``marker_oclock``
    vocabularies, so the fold licenses the notation exactly where the grammar
    already licenses a clock.
    """
    out = []
    i = 0
    n = len(tokens)
    while i < n:
        t = tokens[i]
        nxt = tokens[i + 1] if i + 1 < n else None
        nn = tokens[i + 2] if i + 2 < n else None
        alone = i == 0 and nxt is not None and nxt.text == "h" and (
            n == 2 or (n == 3 and nn is not None and nn.is_number))
        marked = (bool(out) and out[-1].text in markers) or alone
        if (marked and t.is_number and t.value is not None
                and 0 <= t.value <= 24 and float(t.value).is_integer()
                and nxt is not None and nxt.text == "h"):
            if (nn is not None and nn.is_number and nn.value is not None
                    and 0 <= nn.value <= 59 and float(nn.value).is_integer()):
                lit = "%d:%02d" % (int(t.value), int(nn.value))
                cs, ce = run_extent(tokens[i:i + 3])
                out.append(Token(text=lit, raw=lit, index=0,
                                 char_start=cs, char_end=ce))
                i += 3
                continue
            lit = "%d:00" % int(t.value)
            cs, ce = run_extent(tokens[i:i + 2])
            out.append(Token(text=lit, raw=lit, index=0,
                             char_start=cs, char_end=ce))
            i += 2
            continue
        out.append(t)
        i += 1
    return reindex(out)


def with_marked_h_clock(fold, markers):
    """Wrap a number fold so the marked hour-letter clock folds ahead of it."""
    marker_set = frozenset(markers)

    def folded(tokens):
        return fold(collapse_marked_h_clock(tokens, marker_set))

    return folded


# -- The number fold of a locale, read from its ``number_fold`` data ---------

#: The keys of the ``number_fold`` object of a ``lang.json``.
NUMBER_FOLD_KEYS = frozenset({
    "word_numbers", "ordinal_suffixes", "phrase_numbers", "compounds",
    "fraction_counts", "h_clock_markers"})

#: The keys of a row of each knob that holds rows: the required keys, then the
#: optional ones.  Every row may carry a ``source``, the citation of its data.
NUMBER_FOLD_ROWS = {
    "word_numbers": (("words", "ordinal"), ("source",)),
    "phrase_numbers": (("words", "value"), ("source",)),
    "compounds": (("heads", "tails"), ("source",)),
    "fraction_counts": (("word", "value"), ("unit", "not_before", "source")),
}

Fold = Callable[[Tuple[Token, ...]], Tuple[Token, ...]]


def split_compounds(tokens: Tuple[Token, ...],
                    heads: Tuple[Tuple[str, str, FrozenSet[str]], ...]
                    ) -> Tuple[Token, ...]:
    """Split a word that is a head and a tail into two tokens.

    ``heads`` holds, longest head first, each head surface, the word the head
    token reads as, and the tails that may follow it.  Only a whole word that
    is exactly a head and a tail splits.
    """
    out = []
    changed = False
    for t in tokens:
        for stem, canonical, tails in heads:
            if (not t.is_number and t.text.startswith(stem)
                    and t.text[len(stem):] in tails):
                cs, ce = t.char_start, t.char_end
                mid = cs + len(stem) if cs is not None else None
                out.append(Token(text=canonical, raw=t.raw[:len(stem)],
                                 index=t.index, char_start=cs, char_end=mid,
                                 cap=t.cap))
                out.append(Token(text=t.text[len(stem):],
                                 raw=t.raw[len(stem):], index=t.index,
                                 char_start=mid, char_end=ce))
                changed = True
                break
        else:
            out.append(t)
    return reindex(out) if changed else tokens


def fraction_counts(tokens: Tuple[Token, ...],
                    rows: Tuple[Mapping, ...]) -> Tuple[Token, ...]:
    """Fold the count 1 and a fraction word into the fraction count.

    A row names the fraction ``word`` and its ``value``.  Without ``unit``
    the word after the fraction must be a word that is no number: "one half
    hour" counts 0.5 before "hour".  With ``unit`` the fraction word names the
    unit itself, so the count 0.5 gets that unit word in its place ("one
    quarter" is a quarter of an hour), unless the word after it is in
    ``not_before`` (a clock direction) or is a number.
    """
    by_word = {row["word"]: row for row in rows}
    out = []
    i = 0
    n = len(tokens)
    while i < n:
        t = tokens[i]
        nxt = tokens[i + 1] if i + 1 < n else None
        row = (by_word.get(nxt.text) if t.is_number and t.value == 1
               and nxt is not None and not nxt.is_number else None)
        if row is not None:
            after = tokens[i + 2] if i + 2 < n else None
            unit = row.get("unit")
            if unit is None and after is not None and not after.is_number:
                out.append(Token(text=str(row["value"]),
                                 raw=t.raw + " " + nxt.raw, index=t.index,
                                 is_number=True, value=row["value"],
                                 char_start=t.char_start,
                                 char_end=nxt.char_end))
                i += 2
                continue
            if unit is not None and (after is None or (
                    not after.is_number
                    and after.text not in row.get("not_before", ()))):
                out.append(Token(text=str(row["value"]),
                                 raw=t.raw + " " + nxt.raw, index=t.index,
                                 is_number=True, value=row["value"],
                                 char_start=t.char_start,
                                 char_end=nxt.char_start))
                out.append(Token(text=unit, raw=nxt.raw, index=t.index,
                                 char_start=nxt.char_start,
                                 char_end=nxt.char_end))
                i += 2
                continue
        out.append(t)
        i += 1
    return reindex(out)


def number_fold(lang: str, cfg: Mapping) -> Tuple[Fold, Optional[Fold]]:
    """The number fold of the locale ``lang`` and its ``pre_hook`` from the
    ``number_fold`` object of its ``lang.json``.

    The fold claims the words that numtag reads as numbers and the date
    grammar reads as words, from the ``.voc`` files of the locale
    (:func:`date_words`).  The object adds what the files cannot say:

    ``word_numbers``
        Rows ``{"words": {word: value}, "ordinal": bool}``: words numtag
        does not read, with their value and whether they are ordinals.
    ``ordinal_suffixes``
        The lone suffixes of a digit ordinal: "21e" is written "21" and "e".
    ``phrase_numbers``
        Rows ``{"words": "een paar", "value": 2}``: two words that name one
        number.
    ``compounds``
        Rows ``{"heads": {head: reading}, "tails": [...]}``.  A word that is
        a head and a tail splits in two before the grammar reads the stream
        (:func:`split_compounds`).
    ``fraction_counts``
        Rows for :func:`fraction_counts`.
    ``h_clock_markers``
        The words before which "21h30" is a clock time
        (:func:`collapse_marked_h_clock`).

    Every row may carry a ``source`` string, the citation of its data.
    """
    words = DateWords(lang=lang,
                      fractions=locale_words(lang, "clock_fraction_"),
                      counts=count_words(lang))
    table = {word: (value, row["ordinal"])
             for row in cfg.get("word_numbers", ())
             for word, value in row["words"].items()}
    suffixes = frozenset(cfg.get("ordinal_suffixes", ()))
    phrases = {tuple(row["words"].split()): row["value"]
               for row in cfg.get("phrase_numbers", ())}
    fractions = tuple(cfg.get("fraction_counts", ()))
    markers = frozenset(cfg.get("h_clock_markers", ()))
    heads = tuple(sorted(
        ((head, reading, frozenset(row["tails"]))
         for row in cfg.get("compounds", ())
         for head, reading in row["heads"].items()),
        key=lambda h: len(h[0]), reverse=True))
    tails = frozenset(t for _, _, ts in heads for t in ts)

    def split_tails(tokens: Tuple[Token, ...]) -> Claims:
        # numtag reads the whole word "তিনটে" as one number, so the tail split
        # from it is inside the mention and stays a word only when claimed
        return ({i for i, t in enumerate(tokens)
                 if t.mention is not None and t.text in tails
                 and t.char_start != t.mention.char_span[0]}, set(), {})

    def run(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        if markers:
            tokens = collapse_marked_h_clock(tokens, markers)
        folded = fold(tokens, words, extra=split_tails if tails else None,
                      table=table, ordinal_suffixes=suffixes, phrases=phrases)
        return fraction_counts(folded, fractions) if fractions else folded

    if not heads:
        return run, None
    return run, lambda tokens: split_compounds(tokens, heads)
