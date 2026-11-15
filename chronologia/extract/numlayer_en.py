"""English date words over the numtag number layer.

numtag reads every English number (:mod:`chronologia.extract.numlayer`).
Some number words are also date words, and in some positions the date grammar
must read the word: "half" and "quarter" in a clock ("half past three"),
"million" as the SCALE of a deep-time phrase ("sixty six million years ago").
This module names those positions.  Every other mention folds to its number.

Three date rules then compose the folded numbers:

* a year pair: "in nineteen ninety nine" is the two mentions 19 and 99, and
  after a year cue they are the year 1999;
* a deep-time article: "a million years ago" counts one million, said as a
  colloquial point rather than a measured age;
* a duration fraction: "two and a half hours", "half a year", "an hour and a
  half" are lengths, and a fraction of a year is counted in months.
"""
from __future__ import annotations

import re
from dataclasses import replace
from pathlib import Path
from typing import FrozenSet, Set, Tuple

from numtag import Kind
from ovos_spec_tools import expand, read_resource_file

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex
from chronologia.extract.numlayer import fold_mentions, mention_number, mentions

_LANG_DIR = Path(__file__).resolve().parent.parent / "locale" / "en"


def _voc(*bases: str) -> FrozenSet[str]:
    """The surfaces of the English ``.voc`` files whose names start with one
    of ``bases``."""
    out = set()
    for path in sorted(_LANG_DIR.glob("*.voc")):
        if path.name.startswith(bases):
            for template in read_resource_file(path):
                out.update(s.lower() for s in expand(template, {}))
    return frozenset(out)


_UNITS = _voc("unit_")
_YEAR_UNITS = _voc("unit_year")
_YEAR_WORDS = _voc("marker_year_word")
#: The words that announce a calendar year: "in ...", "the year ...".
_YEAR_CUES = _YEAR_WORDS | _voc("marker_in.")
#: The Gregorian months.  The other calendars' month files name months that
#: never head a Gregorian year.
_MONTHS = frozenset().union(*(
    _voc(path.name) for path in _LANG_DIR.glob("month_*.voc")
    if re.fullmatch(r"month_\d+\.voc", path.name)))
#: The clock fractions, and the plural of "three quarters of an hour".
_FRACTIONS = _voc("clock_fraction_") | {"quarters"}
#: The deep-time SCALE words ("thousand", "million", "billion").
_SCALES = _voc("scale_")
_INDEF = frozenset({"a", "an"})
_ORDLAST = _voc("marker_ordlast")
#: The words between a fraction and its unit: "half a year", "three quarters
#: of an hour".  "the" is not one: "the first half of the century" names a
#: part of a period, not a length.
_FILLER = _INDEF | {"of"}
_ORD_SUFFIXES = frozenset({"st", "nd", "rd", "th"})


def _merge_ord_suffix(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Merge a digit and the ordinal suffix after it ("5 th" -> 5)."""
    merged = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        nxt = tokens[i + 1] if i + 1 < len(tokens) else None
        if (t.is_number and nxt is not None and not nxt.is_number
                and nxt.text in _ORD_SUFFIXES):
            # the merged surface runs through the suffix, so its extent does
            # too: "the 6th" must not be cut to "the 6" in a remainder
            merged.append(replace(t, raw=t.raw + nxt.raw,
                                  char_end=nxt.char_end, ordinal=True))
            i += 2
            continue
        merged.append(t)
        i += 1
    return tuple(merged)


#: era abbreviations the tokenizer splits on their dots ("b.c." -> b, c),
#: glued back into the one token the ``bc``/``ad`` connector binds.
_ERA_GLUE = {
    ("b", "c", "e"): "bce", ("b", "c"): "bc",
    ("c", "e"): "ce", ("a", "d"): "ad",
}


def _dotted_run(run: Tuple[Token, ...]) -> bool:
    """Whether the fragments were written as ONE dotted abbreviation.

    Single letters become adjacent once the tokenizer drops punctuation, so
    adjacency alone reads "b/c" ("because") and "b, c" as BC.  The written
    abbreviation separates its letters by exactly one full stop; the unended
    "3 b.c" reads as 3 BC too.
    """
    return all(a.trailing_dot and a.char_end is not None
               and b.char_start == a.char_end + 1
               for a, b in zip(run, run[1:]))


def _glue_era(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    seqs = sorted(_ERA_GLUE, key=len, reverse=True)
    out = []
    i = 0
    while i < len(tokens):
        for seq in seqs:
            k = len(seq)
            if (tuple(t.text for t in tokens[i:i + k]) == seq
                    and _dotted_run(tokens[i:i + k])):
                run = tokens[i:i + k]
                out.append(Token(text=_ERA_GLUE[seq],
                                 raw="".join(t.raw for t in run), index=0,
                                 char_start=run[0].char_start,
                                 char_end=run[-1].char_end))
                i += k
                break
        else:
            out.append(tokens[i])
            i += 1
    return reindex(out)


def _skip_filler(tokens: Tuple[Token, ...], k: int) -> int:
    while k < len(tokens) and tokens[k].text in _FILLER:
        k += 1
    return k


def _mention_end(tokens: Tuple[Token, ...], i: int) -> int:
    """The index after the last token of the mention of ``tokens[i]``."""
    j = i
    while j < len(tokens) and tokens[j].mention is tokens[i].mention:
        j += 1
    return j


def _date_words(tokens: Tuple[Token, ...]) -> Set[int]:
    """The indices of the number words the date grammar reads as words.

    A clock fraction stays a word unless its mention is a length: a fraction
    followed by a unit ("two and a half hours", "half a year").  A scale word
    stays a word in the deep-time frame, before a year word ("sixty six
    million years ago").
    """
    claimed = set()
    n = len(tokens)
    for i, tok in enumerate(tokens):
        m = tok.mention
        if m is None or tok.is_number:
            continue
        if tok.text in _FRACTIONS:
            unit = _skip_filler(tokens, _mention_end(tokens, i))
            if not (m.kind is Kind.FRACTION and unit < n
                    and tokens[unit].text in _UNITS):
                claimed.add(i)
        elif (tok.text in _SCALES and i + 1 < n
              and tokens[i + 1].text in _YEAR_WORDS):
            claimed.add(i)
    return claimed


def ordinal_to_last(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Give the ordinal of "the second-to-last friday" its mention.

    The hyphens make "second-to-last" one compound for numtag, so the layer
    finds no number in it.  Before "to last" the word is the ordinal the
    NTOLAST order counts with, so numtag reads the word on its own.  This is
    the ``pre_hook`` of the English locale: it runs before the layer is
    attached, so the range split, which folds the ordinal alone, reads it too.
    """
    out = list(tokens)
    n = len(tokens)
    for i, tok in enumerate(tokens):
        if (tok.is_number or tok.char_start is None or i + 2 >= n
                or tokens[i + 1].text != "to"
                or tokens[i + 2].text not in _ORDLAST):
            continue
        found = mentions(tok.raw, "en")
        if (len(found) == 1 and found[0].text == tok.raw
                and found[0].kind is Kind.ORDINAL):
            out[i] = replace(tok, mention=replace(
                found[0], char_span=(tok.char_start, tok.char_end)))
    return tuple(out)


def _whole(tok: Token, low: int, high: int) -> bool:
    return (tok.is_number and tok.value is not None
            and float(tok.value).is_integer() and low <= tok.value <= high)


def _after_month_day(out) -> bool:
    """A calendar month and its day stand right before: "july 4", "september
    first", "december thirty first".  With the day filled, a spelled pair
    after them can only be the year."""
    return (len(out) >= 2 and _whole(out[-1], 1, 31)
            and out[-2].text in _MONTHS)


def _year_pairs(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Join a spelled year pair into the year it names.

    English says a year as two numbers: "nineteen ninety nine" is the century
    19 and the year 99 of it.  numtag reads them as two cardinals.  The pair
    is a year only after a year cue ("in", "the year") or after a month and
    its day, where the year is the one date field still open.  The century
    is one word in 10..99 and the year 10..99, so "in twenty five days" stays
    a count, and a unit or scale word after the pair ("nineteen ninety
    years") leaves it two numbers.
    """
    out = []
    i = 0
    n = len(tokens)
    while i < n:
        tok = tokens[i]
        nxt = tokens[i + 1] if i + 1 < n else None
        after = tokens[i + 2].text if i + 2 < n else None
        cued = out and (out[-1].text in _YEAR_CUES or _after_month_day(out))
        if (cued and nxt is not None
                and _spelled_cardinal(tok) and " " not in tok.mention.text
                and _spelled_cardinal(nxt)
                and _whole(tok, 10, 99) and _whole(nxt, 10, 99)
                and after not in _UNITS and after not in _SCALES):
            year = int(tok.value) * 100 + int(nxt.value)
            out.append(Token(text=str(year), raw=str(year), index=0,
                             is_number=True, value=year,
                             char_start=tok.char_start,
                             char_end=nxt.char_end))
            i += 2
            continue
        out.append(tok)
        i += 1
    return reindex(out)


def _spelled_cardinal(tok: Token) -> bool:
    return (tok.is_number and tok.mention is not None
            and tok.mention.kind is Kind.CARDINAL)


def _deep_time_article(tokens: Tuple[Token, ...],
                       claimed_scales: FrozenSet[int]) -> Tuple[Token, ...]:
    """Count a deep-time phrase said with the indefinite article.

    "a million years ago" and "a hundred thousand years ago" are a colloquial
    count back from now; "sixty six million years ago" is a measured age with
    its own span.  The article count is one, times any number between the
    article and the scale ("a hundred"); its token is marked ``article`` for
    the resolver.
    """
    out = []
    n = len(tokens)
    for i, tok in enumerate(tokens):
        before_scale = i + 1 < n and tokens[i + 1].index in claimed_scales
        if before_scale and not tok.is_number and tok.text in _INDEF:
            out.append(Token(text="1", raw=tok.raw, index=0, is_number=True,
                             value=1, char_start=tok.char_start,
                             char_end=tok.char_end, article=True))
        elif (before_scale and tok.is_number and tok.mention is not None
              and tok.mention.text.split()[0].lower() in _INDEF):
            out.append(replace(tok, article=True))
        else:
            out.append(tok)
    return reindex(out)


def _duration_fraction(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Read a fraction of a unit as one count before the unit.

    "two and a half hours" and "half a year" fold to one FRACTION mention
    before the unit; "an hour and a half" and "two hours and a half" put the
    fraction after it, and the count is the number before the unit plus the
    fraction.  A fractional year has no decimal offset (the resolver steps
    whole months), so a year fraction that is a whole number of months is
    counted in months: "half a year" is 6 months.
    """
    out = []
    i = 0
    n = len(tokens)
    while i < n:
        tok = tokens[i]
        combined = unit_pos = end = None
        if (tok.is_number and tok.mention is not None
                and tok.mention.kind is Kind.FRACTION):
            k = _skip_filler(tokens, i + 1)
            if k < n and tokens[k].text in _UNITS:
                combined, unit_pos, end = tok.value, k, k + 1
        elif tok.is_number or tok.text in _INDEF:
            count = tok.value if tok.is_number else 1
            k = _skip_filler(tokens, i + 1)
            m = k + 1
            if (k < n and tokens[k].text in _UNITS and m < n
                    and tokens[m].text == "and"):
                m = _skip_filler(tokens, m + 1)
                if (m < n and tokens[m].text in _FRACTIONS
                        and tokens[m].mention is not None
                        and tokens[m].mention.kind is Kind.FRACTION):
                    combined = count + mention_number(tokens[m].mention)
                    unit_pos, end = k, m + 1
        if combined is None:
            out.append(tok)
            i += 1
            continue
        unit = tokens[unit_pos]
        if unit.text in _YEAR_UNITS and not float(combined).is_integer():
            months = combined * 12
            if not float(months).is_integer():
                out.append(tok)
                i += 1
                continue
            out.append(_count(months, tok, tokens[end - 1]))
            out.append(Token(text="months", raw="months", index=0,
                             char_start=unit.char_start,
                             char_end=unit.char_end))
        else:
            out.append(_count(combined, tok, tokens[end - 1]))
            out.append(unit)
        i = end
    return reindex(out)


def _count(value, first: Token, last: Token) -> Token:
    v = int(value) if float(value).is_integer() else value
    return Token(text=str(v), raw=str(v), index=0, is_number=True, value=v,
                 char_start=first.char_start, char_end=last.char_end)


def fold_en(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """The English number fold: every numtag mention becomes one number
    token, except the words the date grammar reads as words; then the year
    pair, the deep-time article and the duration fraction compose."""
    tokens = reindex(_merge_ord_suffix(_glue_era(tokens)))
    claimed = _date_words(tokens)
    scales = frozenset(i for i in claimed if tokens[i].text in _SCALES)
    folded = fold_mentions(tokens, "en", claimed)
    # the claimed scale words keep their place in the folded stream; find
    # them again by their source extent
    extents = {(tokens[i].char_start, tokens[i].char_end) for i in scales}
    scale_idx = frozenset(t.index for t in folded
                          if not t.is_number and t.text in _SCALES
                          and (t.char_start, t.char_end) in extents)
    folded = _deep_time_article(folded, scale_idx)
    return _duration_fraction(_year_pairs(folded))
