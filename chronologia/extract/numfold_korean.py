# -*- coding: utf-8 -*-
"""Spelled-number folding for Korean, where the counter chooses the numeral.

Korean runs two complete cardinal series side by side.  The native series
(하나, 둘, 셋 ...) has a distinct *attributive* shape before a counter -- 한,
두, 세, 네, 스무 -- and the Sino-Korean series (일, 이, 삼 ...) is positional,
built on 십, 백, 천, 만, 억, 조 and grouped by ten thousands rather than by
thousands.  Both are live, and which one a number wears is decided by the word
being counted: the hours of the clock take the native series, while the
minutes and seconds beside them and every calendar field -- the year, the
month, the day of the month, the month count 개월 and the week count -- take
Sino.  So one clock phrase carries both, 세 시 십 분, and reading 세 as three
depends entirely on knowing that 시 follows it.

That dependency is the whole design of this module.  A numeral is folded only
where a counter licenses it, and only in the series that counter selects; a
native numeral standing before a minute, or a Sino numeral standing before an
hour, reads as nothing at all and the phrase resolves to nothing.  The
alternative -- reading either series in either slot -- turns a mismatched
phrase into a confident wrong time rather than a refusal.

Korean is written with no space between a numeral and its counter as often as
with one (열두시반 beside 열두 시 반), and the grammatical particles are
suffixed to the noun with no space at all (3시부터).  A whitespace tokenizer
therefore hands this fold one token where the grammar needs three.  The fold
segments such a token, but only under the same licensing rule: every counter
inside it must be preceded by a numeral of the series it selects, and the
segmentation must cover the token exactly.  A word that merely happens to
contain a counter syllable (시일, 일요일) fails that test and is left whole,
which is what keeps the segmenter from inventing a time inside ordinary prose.

Two homograph guards are carved out by hand, because the numeral reading of
each is a real Korean word with no temporal sense.  The myriad scale words 만,
억 and 조 are refused when they carry no multiplier, so 만일 ("if") does not
read as ten thousand days, and 일일 ("daily", "day by day") is refused
outright rather than read as one day.

Sources: en.wiktionary.org, ``Module:number_list/data/ko`` (the
machine-readable numeral table, whose ``isol``/``attr``/``sino`` keys are the
three columns below, and whose composition builds 10^11 as 천억 -- myriad
grouping, not thousands); Unicode CLDR 47, ko ``dateFields`` for the counter
inventory and for the 개월 month-count spelling that is not the calendar label
월; Korean Study Junkie, "Telling Time in Korean: when to use Sino & Native
Korean numbers", for the rule that the native series tells the hours and the
Sino series the minutes and seconds; Elon.io, Korean grammar, "Half, To, and
Past: 반, 전, 후", whose worked example 세 시 십 분 전 carries the native hour
and the Sino minute in one phrase.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex

#: native cardinals below ten, isolated and attributive.  Only 1-4 (and 20
#: below) have a separate attributive shape; from five up the two coincide.
_NATIVE_UNITS: Dict[str, int] = {
    "하나": 1, "한": 1, "둘": 2, "두": 2, "셋": 3, "세": 3, "넷": 4, "네": 4,
    "다섯": 5, "여섯": 6, "일곱": 7, "여덟": 8, "아홉": 9,
}

#: native tens.  스무 is the attributive of 스물.
_NATIVE_TENS: Dict[str, int] = {
    "열": 10, "스물": 20, "스무": 20, "서른": 30, "마흔": 40, "쉰": 50,
    "예순": 60, "일흔": 70, "여든": 80, "아흔": 90,
}

#: Sino-Korean digits.  육 and 륙 are the same digit under the initial-sound
#: rule; both spellings occur.
_SINO_DIGITS: Dict[str, int] = {
    "일": 1, "이": 2, "삼": 3, "사": 4, "오": 5, "육": 6, "륙": 6,
    "칠": 7, "팔": 8, "구": 9,
}

#: Sino positional words below the myriad.
_SINO_SMALL: Dict[str, int] = {"십": 10, "백": 100, "천": 1000}

#: Sino myriad scales.  Grouping runs by ten thousands, so 억 is 10^8 and 조
#: is 10^12 -- a thousands-grouped reading would misread every large number.
_SINO_MYRIAD: Dict[str, int] = {"만": 10 ** 4, "억": 10 ** 8, "조": 10 ** 12}

#: counter -> the numeral series it licenses.
NATIVE, SINO = "native", "sino"
_COUNTERS: Dict[str, str] = {
    # the hour of the clock, and only the hour, takes the native series
    "시": NATIVE,
    # the minute and second beside it, and every calendar field, take Sino
    "분": SINO, "초": SINO, "년": SINO, "월": SINO, "일": SINO,
    "개월": SINO, "주": SINO, "주일": SINO,
}

#: the half-hour word, which stands where a minute count would (반 replaces
#: 삼십 분), so it may close an hour group and nothing else.
_HALF = "반"

#: suffixed grammatical particles, written onto the preceding noun with no
#: space: 에 (at/on), 부터 (from), 까지 (until), 마다 (every).
_PARTICLES: Tuple[str, ...] = ("부터", "까지", "마다", "에")

#: the relative-period determiners, which lead their unit word.
_REL: Tuple[str, ...] = ("지난", "이번", "다음")

#: unit nouns a relative determiner may lead when the two are written as one
#: word (지난주, 지난달) -- the spelling CLDR carries for the "last" forms.
_REL_UNITS: Tuple[str, ...] = ("주일", "주", "달", "해")

#: single words CLDR gives for a whole relative period, expanded to the
#: determiner-plus-unit pair the grammar binds.  작년/올해/내년 are suppletive
#: -- they contain no determiner to split off -- so the expansion is lexical,
#: stating the meaning CLDR states, not a claim about their morphology.
_LEXICAL: Dict[str, Tuple[str, ...]] = {
    "작년": ("지난", "해"),
    "올해": ("이번", "해"),
    "내년": ("다음", "해"),
}

#: words whose numeral segmentation is a homograph of an ordinary,
#: non-temporal word.  일일 is "daily"/"day by day", not one day.
_BLOCKED: frozenset = frozenset({"일일"})

_SORTED_COUNTERS = tuple(sorted(_COUNTERS, key=len, reverse=True))
_SORTED_REL_UNITS = tuple(sorted(_REL_UNITS, key=len, reverse=True))


def read_native(text: str) -> Optional[int]:
    """The value of a run of native cardinal syllables, or ``None``.

    Tens word plus units word with no linker, exactly as the numeral table
    composes 열 + 하나 for eleven.
    """
    if not text:
        return None
    for tens, tval in _NATIVE_TENS.items():
        if text == tens:
            return tval
        if text.startswith(tens):
            rest = text[len(tens):]
            if rest in _NATIVE_UNITS:
                return tval + _NATIVE_UNITS[rest]
    return _NATIVE_UNITS.get(text)


def read_sino(text: str) -> Optional[int]:
    """The value of a run of Sino-Korean numeral syllables, or ``None``.

    Positional, myriad-grouped: each 만/억/조 closes the group accumulated
    before it and multiplies it, so 삼천오백만 is 35 000 000 and not
    3 500 * 10 000 read the other way round.  A myriad scale with no
    multiplier in front of it is refused -- see the module docstring for why.
    """
    if not text:
        return None
    total = 0            # groups already closed by a myriad scale
    group = 0            # the group being read
    current = 0          # the digit awaiting a positional word
    seen = False
    for ch in text:
        if ch in _SINO_DIGITS:
            if current:
                return None          # two bare digits in a row read as none
            current = _SINO_DIGITS[ch]
            seen = True
            continue
        small = _SINO_SMALL.get(ch)
        if small is not None:
            group += (current or 1) * small
            current = 0
            seen = True
            continue
        myriad = _SINO_MYRIAD.get(ch)
        if myriad is not None:
            unit = group + current
            if not unit:
                return None          # a bare 만/억/조 carries no count
            total += unit * myriad
            group = current = 0
            seen = True
            continue
        return None
    return total + group + current if seen else None


_READ = {NATIVE: read_native, SINO: read_sino}


def _numeral_prefixes(text: str, series: str):
    """Every prefix of ``text`` that reads as a numeral of ``series``."""
    read = _READ[series]
    for k in range(len(text), 0, -1):
        value = read(text[:k])
        if value is not None:
            yield k, value


def split_word(text: str) -> Optional[Tuple[str, ...]]:
    """Segment one written-together Korean word into grammar tokens.

    Returns the segments, or ``None`` when the word is not a temporal
    compound.  A counter may appear only immediately after a numeral of the
    series it licenses; 반 may close an hour group; a relative determiner may
    lead one.  The segmentation must cover the word exactly, so an ordinary
    word containing a counter syllable is left alone.
    """
    if text in _BLOCKED or len(text) < 2:
        return None
    n = len(text)
    seen: Dict[tuple, Optional[Tuple[str, ...]]] = {}

    def walk(i: int, prev: Optional[str], numeric: bool
             ) -> Optional[Tuple[str, ...]]:
        if i == n:
            return () if numeric else None
        key = (i, prev, numeric)
        if key in seen:
            return seen[key]
        out: Optional[Tuple[str, ...]] = None
        if i == 0:
            for rel in _REL:
                if text.startswith(rel):
                    for unit in _SORTED_REL_UNITS:
                        if text[len(rel):] == unit:
                            out = (rel, unit)
                            break
                    if out is not None:
                        break
        if out is None and prev == "시" and text.startswith(_HALF, i):
            tail = walk(i + len(_HALF), _HALF, True)
            if tail is not None:
                out = (_HALF,) + tail
        if out is None:
            for counter in _SORTED_COUNTERS:
                series = _COUNTERS[counter]
                for k, _value in _numeral_prefixes(text[i:], series):
                    if not text.startswith(counter, i + k):
                        continue
                    tail = walk(i + k + len(counter), counter, True)
                    if tail is not None:
                        out = (text[i:i + k], counter) + tail
                        break
                if out is not None:
                    break
        seen[key] = out
        return out

    segments = walk(0, None, False)
    return segments if segments and len(segments) > 1 else None


def _is_bare_numeral(text: str) -> bool:
    """Does the whole token read as one numeral in either series?

    Such a token must never be segmented, even where a counter syllable sits
    at its end: 삼십일 is thirty-one, and cutting it into 삼십 + 일 would turn
    the thirty-one minutes of 네 시 삼십일 분 into thirty days.  The counter
    that follows the token is what licenses it, exactly as for a spaced run.
    """
    return read_sino(text) is not None or read_native(text) is not None


def _respan(tok: Token, parts: Tuple[str, ...], index: int) -> List[Token]:
    """Re-cut ``tok`` into ``parts``, carrying the character extents across."""
    out: List[Token] = []
    offset = 0
    for part in parts:
        start = end = None
        if tok.char_start is not None and len(tok.raw) == len(tok.text):
            start = tok.char_start + offset
            end = start + len(part)
        out.append(Token(text=part, raw=part, index=index + len(out),
                         char_start=start, char_end=end))
        offset += len(part)
    return out


def _split_pass(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Cut written-together compounds and suffixed particles into tokens."""
    out: List[Token] = []
    changed = False
    for tok in tokens:
        parts: Optional[Tuple[str, ...]] = None
        if not tok.is_number and not _is_bare_numeral(tok.text):
            parts = _LEXICAL.get(tok.text) or split_word(tok.text)
        if parts is None:
            out.append(tok)
            continue
        out.extend(_respan(tok, parts, len(out)))
        changed = True
    return reindex(out) if changed else tokens


def _particle_pass(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Cut a suffixed particle off the noun it is written onto.

    A particle attaches to any noun, including one carrying no numeral at all
    (내일에, 지난주에), so it comes off first and the compound segmenter then
    sees the bare noun it knows how to read.
    """
    out: List[Token] = []
    changed = False
    for tok in tokens:
        parts = None
        if not tok.is_number:
            for part in _PARTICLES:
                if tok.text.endswith(part) and len(tok.text) > len(part):
                    parts = (tok.text[:-len(part)], part)
                    break
        if parts is None:
            out.append(tok)
            continue
        out.extend(_respan(tok, parts, len(out)))
        changed = True
    return reindex(out) if changed else tokens


def _numeric(first: Token, last: Token, value: int, index: int) -> Token:
    return Token(text=str(value), raw=str(value), index=index,
                 is_number=True, value=value, char_start=first.char_start,
                 char_end=last.char_end)


def _fold_pass(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Fold each spaced numeral run the counter after it licenses."""
    out: List[Token] = []
    i, n, changed = 0, len(tokens), False
    while i < n:
        counter_at = None
        for j in range(i + 1, n):
            if tokens[j].is_number:
                break
            if tokens[j].text in _COUNTERS:
                counter_at = j
                break
        if counter_at is None or tokens[i].is_number:
            out.append(tokens[i])
            i += 1
            continue
        series = _COUNTERS[tokens[counter_at].text]
        read = _READ[series]
        value = None
        start = i
        while start < counter_at:
            value = read("".join(t.text for t in tokens[start:counter_at]))
            if value is not None:
                break
            start += 1
        if value is None:
            out.append(tokens[i])
            i += 1
            continue
        for k in range(i, start):
            out.append(tokens[k])
        out.append(_numeric(tokens[start], tokens[counter_at - 1], value,
                            len(out)))
        i = counter_at
        changed = True
    return reindex(out) if changed else tokens


def fold_ko(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Segment Korean compounds and fold every counter-licensed numeral."""
    return _fold_pass(_split_pass(_particle_pass(tokens)))
