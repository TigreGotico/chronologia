# -*- coding: utf-8 -*-
"""Spelled-number folding pre-pass for Georgian.

The tokenizer only recognises *digit* runs as numbers; Georgian speech spells
them, so a maximal run of spelled number-words is folded into a single digit
:class:`~chronologia.extract.model.Token` and a ``NUM``/``DAY``/``HOUR`` slot
then binds the same whether the writer typed ``3`` or the word.

Georgian counts in **base twenty**.  Between the score multiples -- ოცი 20,
ორმოცი 40 ("two-twenty"), სამოცი 60, ოთხმოცი 80 -- a value is the score's
stem, the joiner და ("and") and the remainder, all fused into ONE orthographic
word: ოცდაათი is "twenty-and-ten" == 30, ორმოცდაშვიდი "forty-and-seven" == 47,
ოთხმოცდაცხრამეტი "eighty-and-nineteen" == 99.  A tens/ones decomposition of the
kind the Germanic and Slavic folds use is therefore wrong for every value from
21 to 99, and :func:`surface` and :func:`read_word` both go through the score
base instead.  The remainder is itself drawn from the 1..19 series, whose teens
(თერთმეტი 11 .. ცხრამეტი 19) are their own formation, not vigesimal compounds.

The hundreds are single fused words too (ორასი 200, რვაასი 800), and a hundred
with a remainder splits into two words with the hundred losing its final -ი:
ორას ორმოცდაათი == 250 nests a whole vigesimal expression inside the hundreds
one.  ათასი (1000, literally "ten hundred") multiplies what precedes it and
loses the same -ი before a remainder: ორი ათას ათი == 2010.

The clock reads the hour in the GENITIVE, and it names the hour being
approached: ორის ნახევარი is "half toward two" == 01:30 and სამის ნახევარი
== 02:30.  :data:`GENITIVE_HOURS` carries those hour surfaces, and
:func:`fold_ka` folds a genitive hour only when the half-word follows it, while
refusing to fold a NOMINATIVE cardinal there -- the case marking is the only
thing that makes the phrase a time, so a nominative before ნახევარი names no
hour and must not resolve to one.

Sources.  Cardinals: the en.wiktionary.org entry for each numeral word below,
whose "Georgian numbers" navigation box states the value (ნული, ერთი .. ათი,
the teens თერთმეტი .. ცხრამეტი, the scores ოცი/ორმოცი/სამოცი/ოთხმოცი, the
hundreds ასი .. ცხრაასი, ათასი) and, for the vigesimal compounds, the entries
ოცდაერთი 21, ოცდახუთი 25, ოცდაცხრა 29, ოცდაათი 30, ორმოცდაერთი 41,
ორმოცდაათი 50, ორმოცდაცხრამეტი 59, ოთხმოცდაათი 90, ოთხმოცდაცხრამეტი 99.  The
genitive clock hour: en.wiktionary.org, ნახევარი ("ორის ნახევარი -- half past
one") and the -ი -> -ის genitive the same site's declension tables show on
every unit noun.  Nothing is delegated to an external number back-end.
"""
from __future__ import annotations

from typing import Callable, Dict, Optional, Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex

#: 0..10, the primitives every larger numeral is built from.
ONES: Dict[int, str] = {
    0: "ნული", 1: "ერთი", 2: "ორი", 3: "სამი", 4: "ოთხი", 5: "ხუთი",
    6: "ექვსი", 7: "შვიდი", 8: "რვა", 9: "ცხრა", 10: "ათი",
}

#: 11..19 -- a reduced "ten" prefix plus -მეტი ("more"), not a vigesimal
#: compound, so they are listed rather than composed.
TEENS: Dict[int, str] = {
    11: "თერთმეტი", 12: "თორმეტი", 13: "ცამეტი", 14: "თოთხმეტი",
    15: "თხუთმეტი", 16: "თექვსმეტი", 17: "ჩვიდმეტი", 18: "თვრამეტი",
    19: "ცხრამეტი",
}

#: the score multiples -- the base of the counting system.
SCORES: Dict[int, str] = {
    20: "ოცი", 40: "ორმოცი", 60: "სამოცი", 80: "ოთხმოცი",
}

#: the fused hundreds.
HUNDREDS: Dict[int, str] = {
    100: "ასი", 200: "ორასი", 300: "სამასი", 400: "ოთხასი", 500: "ხუთასი",
    600: "ექვსასი", 700: "შვიდასი", 800: "რვაასი", 900: "ცხრაასი",
}

#: 1000, itself "ten hundred".
THOUSAND = "ათასი"
#: the joiner inside a vigesimal compound word.
JOINER = "და"
#: the half-word the toward-the-hour clock is built on.
HALF = "ნახევარი"


def _stem(word: str) -> str:
    """A numeral's combining form -- the citation form minus its final -ი.

    A hundred or ათასი followed by a remainder appears in this form
    ("ორას ორმოცდაათი", "ორი ათას ათი"), and a score opens its vigesimal
    compound in it ("ოც" + "და" + "ათი").
    """
    return word[:-1] if word.endswith("ი") else word


def surface(n: int) -> str:
    """The spelled surface of ``n``, 0..999999.

    Defined over exactly the shapes the numeral entries attest: the 0..19
    series, the vigesimal 20..99, the fused hundreds with an optional
    remainder, and ათასი multiplied by any of those.
    """
    n = int(n)
    if not 0 <= n <= 999999:
        raise ValueError(f"no attested Georgian surface for {n}")
    if n >= 1000:
        thousands, rest = divmod(n, 1000)
        head = THOUSAND if thousands == 1 else f"{surface(thousands)} {THOUSAND}"
        if rest == 0:
            return head
        return f"{_stem(head)} {surface(rest)}"
    if n >= 100:
        hundreds, rest = divmod(n, 100)
        head = HUNDREDS[hundreds * 100]
        if rest == 0:
            return head
        return f"{_stem(head)} {surface(rest)}"
    if n >= 20:
        score, rest = (n // 20) * 20, n % 20
        if rest == 0:
            return SCORES[score]
        return f"{_stem(SCORES[score])}{JOINER}{surface(rest)}"
    if n >= 11:
        return TEENS[n]
    return ONES[n]


#: the genitive hour the toward-the-hour clock names.  Only the -ი stems take
#: the plain -ის genitive the declension tables and "ორის ნახევარი" attest;
#: რვა (8) and ცხრა (9) end in -ა and no source consulted spells their
#: genitive, and one o'clock is named by the ordinal პირველი rather than by
#: ერთი at all, so all three are absent and the hour they would name refuses.
GENITIVE_HOURS: Dict[str, int] = {
    _stem(word) + "ის": value
    for value, word in {**ONES, **TEENS}.items()
    if 2 <= value <= 12 and word.endswith("ი")
}


#: every single-word cardinal surface, mapped to its value.  The vigesimal
#: compounds are generated rather than listed: the compound IS the score stem
#: plus და plus the 1..19 remainder, and generating it is what keeps the fold
#: and :func:`surface` from ever disagreeing.
CARDINALS: Dict[str, int] = {}
for _v in list(range(0, 100)):
    CARDINALS[surface(_v)] = _v
for _v, _w in HUNDREDS.items():
    CARDINALS[_w] = _v
    CARDINALS[_stem(_w)] = _v

#: ათასი multiplies the group accumulated before it, so it is read as a scale
#: rather than as a value; both its citation and its combining form appear.
SCALE: Dict[str, int] = {THOUSAND: 1000, _stem(THOUSAND): 1000}

_UNIT_CLASS, _HUNDRED_CLASS, _SCALE_CLASS = 1, 2, 3


def _magnitude(word: str) -> int:
    if word in SCALE:
        return _SCALE_CLASS
    if CARDINALS.get(word, 0) >= 100:
        return _HUNDRED_CLASS
    return _UNIT_CLASS


def _composes(previous: str, following: str) -> bool:
    """Whether ``following`` may continue the run ``previous`` opened.

    A composed numeral descends through the magnitudes ("ორას ორმოცდაათი",
    "ათას ათი"), and ათასი may follow a lower magnitude as its multiplier
    ("ორი ათასი").  Two words of the SAME magnitude never compose, so a bare
    "ორი ორი" stays two numbers.
    """
    prev, nxt = _magnitude(previous), _magnitude(following)
    if nxt > prev:
        return nxt == _SCALE_CLASS
    return nxt < prev


def read_run(text: str) -> Optional[int]:
    """Read the value of a space-joined run of Georgian number-words.

    Additive over the 0..99 words and the hundreds; ათასი multiplies the group
    accumulated so far and closes it into the running total.  Returns ``None``
    when a word is not a number-word, so the fold leaves the run alone rather
    than committing a partial reading.
    """
    total = 0
    group = 0
    seen = False
    for word in text.split():
        if word.isdigit():
            group += int(word)
            seen = True
            continue
        if word in SCALE:
            group = (group or 1) * SCALE[word]
            total += group
            group = 0
            seen = True
            continue
        value = CARDINALS.get(word)
        if value is None:
            return None
        group += value
        seen = True
    return total + group if seen else None


def read_word(word: str) -> Optional[int]:
    """The value of a single Georgian numeral word, or ``None``."""
    if word in SCALE:
        return SCALE[word]
    return CARDINALS.get(word)


def _numeric(tok: Token, value: int, end: Token = None) -> Token:
    return Token(text=str(value), raw=str(value), index=tok.index,
                 is_number=True, value=value, char_start=tok.char_start,
                 char_end=(end or tok).char_end)


def _clock_hour_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Fold the genitive hour of the toward-the-hour clock.

    The genitive is what makes ორის ნახევარი a time rather than two nouns, and
    it is read only in that position: a genitive hour standing alone names no
    time and is left as text.
    """
    out, i, n, changed = [], 0, len(tokens), False
    while i < n:
        t = tokens[i]
        value = None if t.is_number else GENITIVE_HOURS.get(t.text)
        if value is not None and i + 1 < n and tokens[i + 1].text == HALF:
            out.append(_numeric(t, value))
            i, changed = i + 1, True
            continue
        out.append(t)
        i += 1
    return reindex(out) if changed else tokens


def _cardinal_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Fold a well-formed run of spelled cardinals into one digit token."""
    out, i, n, changed = [], 0, len(tokens), False
    while i < n:
        t = tokens[i]
        if t.is_number or t.text not in CARDINALS:
            out.append(t)
            i += 1
            continue
        j, previous = i + 1, t.text
        while (j < n and not tokens[j].is_number
               and tokens[j].text in CARDINALS
               and _composes(previous, tokens[j].text)):
            previous, j = tokens[j].text, j + 1
        # the clock names its hour in the genitive; a nominative cardinal
        # before the half-word is not an hour, so it stays a word and the
        # clock construction finds no hour to read.
        if j < n and tokens[j].text == HALF:
            out.append(t)
            i += 1
            continue
        value = read_run(" ".join(tok.text for tok in tokens[i:j]))
        if value is None:
            out.append(t)
            i += 1
            continue
        out.append(_numeric(t, value, tokens[j - 1]))
        i, changed = j, True
    return reindex(out) if changed else tokens


def _compose(*passes: Callable) -> Callable:
    def run(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        for p in passes:
            tokens = p(tokens)
        return tokens
    return run


fold_ka = _compose(_clock_hour_rewrite, _cardinal_rewrite)
