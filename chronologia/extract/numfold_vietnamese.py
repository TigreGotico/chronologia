# -*- coding: utf-8 -*-
"""Spelled-number folding pre-pass for Vietnamese.

The tokenizer only recognises *digit* runs as numbers; Vietnamese speech
spells them, so a maximal run of spelled number-words is folded into a single
digit :class:`~chronologia.extract.model.Token` and a ``NUM``/``DAY``/``HOUR``
slot then binds the same whether the writer typed ``3`` or the word.

Vietnamese is isolating -- nothing declines, nothing agrees -- so there is no
case or gender machinery here at all.  What there is instead is a set of
POSITIONAL substitutions: the same digit is spoken with a different word
depending on where it sits in the numeral, and reading the citation form in
those positions gives a wrong value rather than no value.

* ``mười`` (10) is the free form and opens the teens (``mười lăm`` 15), but a
  tens digit above twenty takes the reduced ``mươi``: ``hai mươi`` 20,
  ``năm mươi`` 50.
* a final 5 above ten is ``lăm`` (northern also ``nhăm``), never ``năm``:
  ``mười lăm`` 15, ``hai mươi lăm`` 25.  The substitution exists because
  ``năm`` is also the word for "year", and it is why this fold never reads a
  bare ``năm`` as five (see :data:`PLAIN`).
* a final 1 after ``mươi`` is ``mốt``: ``hai mươi mốt`` 21.
* a final 4 after ``mười``/``mươi`` is commonly ``tư``: ``mười tư`` 14,
  ``hai mươi tư`` 24.
* a hundreds group with an empty tens digit is filled by ``linh`` (northern)
  or ``lẻ`` (southern/central): ``một trăm linh một`` 101.  A final 5 in that
  position keeps ``năm`` -- the ``lăm`` rule does not reach it -- so ``năm``
  reads as five there and nowhere else outside a multiplier position.
* the thousand is ``nghìn`` in the north and ``ngàn`` in the south; both are
  read, because the choice is regional rather than stylistic.

Two positions are deliberately left unfolded.  A numeral directly after
``thứ`` or ``tháng`` is a NAME component, not a count -- ``thứ hai`` is Monday
and ``tháng tư`` is April -- and the locale lists those surfaces whole, in
both their spelled and their CLDR digit spelling, so folding the numeral there
would only destroy the surface the vocabulary matches.  And ``năm`` standing
alone is read as the noun "year", never as five: the two are the same word
with the same tone, Vietnamese itself resorts to ``lăm`` to keep them apart in
compounds, and no cue distinguishes them in "năm năm" or "năm giờ".  Refusing
is the only reading that cannot be silently wrong; the digit spelling ``5``
carries the count instead.

The spoken clock hangs its minutes off the hour with ``phút``: ``bốn giờ mười
phút`` is 04:10.  That shape is fused here into one clock literal, because a
minute count only ever reaches the resolver alongside a direction word, and
the additive form has none -- read as a bare hour it would silently drop the
minutes.  The subtractive ``kém`` form (``ba giờ kém mười lăm`` == 02:45) is
NOT fused: it carries its direction word and the clock grammar reads it.

Sources.  Cardinals, the mười/mươi alternation, lăm/nhăm-for-five,
mốt-for-one, tư-for-four, the linh/lẻ filler with its ``05`` exception and the
nghìn/ngàn regional pair: en.wikipedia.org, "Vietnamese numerals",
https://en.wikipedia.org/wiki/Vietnamese_numerals.  ``năm`` as both five and
year, with the lăm shift stated as its own usage note: en.wiktionary.org,
https://en.wiktionary.org/wiki/n%C4%83m.  The additive minute clock
("4 giờ 5 phút" == 5 past 4): en.wiktionary.org,
https://en.wiktionary.org/wiki/ph%C3%BAt.  Nothing is delegated to an external
number back-end.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Optional, Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex

#: 0..9 in their citation form.
BASE: Dict[str, int] = {
    "không": 0, "một": 1, "hai": 2, "ba": 3, "bốn": 4,
    "năm": 5, "sáu": 6, "bảy": 7, "tám": 8, "chín": 9,
}

#: the units a BARE numeral may be.  ``năm`` is absent: alone it is the noun
#: "year", and nothing in the string tells the two apart.
PLAIN: Dict[str, int] = {w: v for w, v in BASE.items() if w != "năm"}

#: the unit closing a teen ("mười lăm"), with the positional substitutes.
TEEN_UNIT: Dict[str, int] = {**PLAIN, "lăm": 5, "nhăm": 5, "tư": 4}

#: the unit closing a tens compound ("hai mươi mốt"), which additionally
#: substitutes ``mốt`` for one.
TENS_UNIT: Dict[str, int] = {**TEEN_UNIT, "mốt": 1}

#: the unit after a zero-filler ("sáu trăm linh năm" 605) -- the only position
#: outside a multiplier where ``năm`` is unambiguously five.
FILLER_UNIT: Dict[str, int] = dict(BASE)

TEN = "mười"
TENS = "mươi"
HUNDRED = "trăm"
THOUSAND = frozenset({"nghìn", "ngàn"})
FILLER = frozenset({"linh", "lẻ"})

#: every word that may take part in a numeral run.
NUMBER_WORDS = (frozenset(BASE) | frozenset(TENS_UNIT) | THOUSAND | FILLER
                | {TEN, TENS, HUNDRED})

#: heads whose following numeral names a weekday or a month rather than
#: counting anything.
NAME_HEADS = frozenset({"thứ", "tháng"})

#: first word of every time-unit noun.  A ``năm`` immediately before one of
#: these is counting it, so it is the numeral five and not the noun "year" --
#: "năm ngày" is five days, and "năm năm" is five years, the second ``năm``
#: being the noun the first one counts.  Anywhere else a bare ``năm`` stays
#: the noun, because nothing in the string separates the two senses.
COUNTED_UNIT_HEADS = frozenset({
    "giây", "phút", "giờ", "ngày", "tuần", "tháng", "năm",
    "thập", "thế", "thiên",
})

#: the hour word, which is also the additive clock's separator.
HOUR_WORD = "giờ"
#: the minute word that closes the additive clock reading.
MINUTE_WORD = "phút"


def _group(words: List[str], i: int) -> Tuple[Optional[int], int]:
    """Read one hundreds group starting at ``i``; ``(None, i)`` when there
    is no numeral there."""
    n = len(words)
    start, value, seen = i, 0, False
    if i + 1 < n and words[i] in BASE and words[i + 1] == HUNDRED:
        value, i, seen = BASE[words[i]] * 100, i + 2, True
        if (i + 1 < n and words[i] in FILLER
                and words[i + 1] in FILLER_UNIT):
            return value + FILLER_UNIT[words[i + 1]], i + 2
    if i < n and words[i] == TEN:
        value, i, seen = value + 10, i + 1, True
        if i < n and words[i] in TEEN_UNIT:
            return value + TEEN_UNIT[words[i]], i + 1
        return value, i
    if i + 1 < n and words[i] in BASE and words[i + 1] == TENS:
        value, i, seen = value + BASE[words[i]] * 10, i + 2, True
        if i < n and words[i] in TENS_UNIT:
            return value + TENS_UNIT[words[i]], i + 1
        return value, i
    if not seen and i < n and words[i] in PLAIN:
        return PLAIN[words[i]], i + 1
    return (value, i) if seen else (None, start)


def read(words: List[str]) -> Tuple[Optional[int], int]:
    """Read the longest well-formed numeral at the head of ``words``.

    Returns the value and how many words it consumed, or ``(None, 0)`` when
    the head is not a numeral -- a partial reading is never committed.
    """
    value, i = _group(words, 0)
    if value is None:
        return None, 0
    if i < len(words) and words[i] in THOUSAND:
        total, i = value * 1000, i + 1
        rest, i = _group(words, i)
        return total + (rest or 0), i
    return value, i


def read_run(text: str) -> Optional[int]:
    """The value of a space-joined numeral phrase, or ``None`` when the phrase
    is not a single well-formed numeral end to end."""
    words = text.split()
    value, used = read(words)
    return value if value is not None and used == len(words) else None


def surface(n: int) -> str:
    """The spelled surface of ``n``, 0..999999 -- the positional substitutions
    applied, so it and :func:`read` can never disagree."""
    n = int(n)
    if not 0 <= n <= 999999:
        raise ValueError(f"no attested Vietnamese surface for {n}")
    if n >= 1000:
        thousands, rest = divmod(n, 1000)
        head = f"{surface(thousands)} nghìn"
        if rest == 0:
            return head
        if rest < 100:
            return f"{head} không {HUNDRED} {_under_hundred(rest)}"
        return f"{head} {surface(rest)}"
    if n >= 100:
        hundreds, rest = divmod(n, 100)
        head = f"{_digit(hundreds)} {HUNDRED}"
        if rest == 0:
            return head
        if rest < 10:
            return f"{head} linh {_digit(rest)}"
        return f"{head} {_under_hundred(rest)}"
    return _under_hundred(n)


def _digit(n: int) -> str:
    return next(w for w, v in BASE.items() if v == n)


def _under_hundred(n: int) -> str:
    if n < 10:
        return _digit(n)
    tens, unit = divmod(n, 10)
    head = TEN if tens == 1 else f"{_digit(tens)} {TENS}"
    if unit == 0:
        return head
    if unit == 5:
        return f"{head} lăm"
    if unit == 1 and tens > 1:
        return f"{head} mốt"
    return f"{head} {_digit(unit)}"


def _numeric(first: Token, value: int, last: Token) -> Token:
    return Token(text=str(value), raw=str(value), index=first.index,
                 is_number=True, value=value, char_start=first.char_start,
                 char_end=last.char_end)


def _cardinal_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    out: List[Token] = []
    i, n, changed = 0, len(tokens), False
    while i < n:
        tok = tokens[i]
        if tok.is_number or tok.text not in NUMBER_WORDS:
            out.append(tok)
            i += 1
            continue
        # a numeral right after "thứ"/"tháng" spells part of a weekday or
        # month name; the locale matches that name whole, in either spelling.
        if out and out[-1].text in NAME_HEADS:
            while i < n and not tokens[i].is_number and tokens[i].text in NUMBER_WORDS:
                out.append(tokens[i])
                i += 1
            continue
        j = i
        while j < n and not tokens[j].is_number and tokens[j].text in NUMBER_WORDS:
            j += 1
        value, used = read([t.text for t in tokens[i:j]])
        if value is None:
            if (tok.text == "năm" and i + 1 < n
                    and tokens[i + 1].text in COUNTED_UNIT_HEADS):
                out.append(_numeric(tok, 5, tok))
                i, changed = i + 1, True
                continue
            out.append(tok)
            i += 1
            continue
        out.append(_numeric(tok, value, tokens[i + used - 1]))
        i, changed = i + used, True
    return reindex(out) if changed else tokens


def _clock_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Fuse the additive spoken clock into one clock literal.

    ``bốn giờ mười phút`` names 04:10 with no direction word at all, so the
    minute count has nothing to bind to and would be dropped; fusing it into
    ``4:10`` hands the clock grammar a literal it reads exactly.
    """
    out: List[Token] = []
    i, n, changed = 0, len(tokens), False
    while i < n:
        if (i + 3 < n and tokens[i].is_number and tokens[i + 2].is_number
                and tokens[i + 1].text == HOUR_WORD
                and tokens[i + 3].text == MINUTE_WORD):
            hour, minute = tokens[i].value, tokens[i + 2].value
            if (hour is not None and minute is not None
                    and float(hour).is_integer() and float(minute).is_integer()
                    and 0 <= hour <= 23 and 0 <= minute <= 59):
                text = f"{int(hour)}:{int(minute):02d}"
                out.append(Token(text=text, raw=text, index=tokens[i].index,
                                 char_start=tokens[i].char_start,
                                 char_end=tokens[i + 3].char_end))
                i, changed = i + 4, True
                continue
        out.append(tokens[i])
        i += 1
    return reindex(out) if changed else tokens


def _compose(*passes: Callable) -> Callable:
    def run(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        for p in passes:
            tokens = p(tokens)
        return tokens
    return run


fold_vi = _compose(_cardinal_rewrite, _clock_rewrite)
