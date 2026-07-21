"""Spelled-number folding pre-pass (English).

The tokenizer only recognises *digit* runs as numbers; natural English
speech spells them ("five days ago", "the twenty fifth", "the third week
of june").  This pass folds a maximal run of English number-words into a
single digit :class:`~chronologia.extract.model.Token` so every
``NUM``/``DAY``/``YEAR``/``ORD`` slot binds the same way whether the writer
typed ``5`` or ``five``.

Wired as a language ``hook`` in ``locale/en/lang.json`` and applied by
:meth:`DateTimeEngine.tokenize` after normalisation.  It is a pure
``tuple[Token] -> tuple[Token]`` transform, re-indexed so ``Token.index``
stays contiguous.

The value is read from :func:`ovos_number_parser.numbers_en.extract_number_en`
(``ordinals=True``); the fold owns only *which* tokens form a run.  Clock
fractions ("half", "quarter") are deliberately **not** number-words here --
they are their own ``FRACTION`` slot vocabulary and must survive intact.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Tuple

from ovos_number_parser.numbers_en import extract_number_en

from chronologia.extract.model import Token

# closed class of English number-words the fold may absorb (cardinals +
# ordinals + a few colloquial multipliers).  "half"/"quarter" are excluded
# on purpose (clock fractions); "a"/"an" are excluded (article ambiguity).
_ONES = ["one", "two", "three", "four", "five", "six", "seven", "eight",
         "nine", "ten", "eleven", "twelve", "thirteen", "fourteen",
         "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
_TENS = ["twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty",
         "ninety"]
_SCALES = ["hundred", "thousand", "million", "billion", "trillion"]
_ORD_ONES = ["first", "second", "third", "fourth", "fifth", "sixth",
             "seventh", "eighth", "ninth", "tenth", "eleventh", "twelfth",
             "thirteenth", "fourteenth", "fifteenth", "sixteenth",
             "seventeenth", "eighteenth", "nineteenth"]
_ORD_TENS = ["twentieth", "thirtieth", "fortieth", "fiftieth", "sixtieth",
             "seventieth", "eightieth", "ninetieth"]
_ORD_SCALES = ["hundredth", "thousandth", "millionth", "billionth"]
_EXTRA = ["zero", "couple", "dozen", "score"]

# NOTE: multiplier scale-words (hundred/thousand/million/billion) are
# deliberately *not* folded -- they are the ``SCALE`` slot of the deep-time
# construction ("66 million years ago"), and folding them would erase the
# very token that separates deep time from a plain "N years ago" offset.
_NUMWORDS = frozenset(_ONES + _TENS + _ORD_ONES + _ORD_TENS
                      + _ORD_SCALES + _EXTRA)
_ORD_SUFFIXES = frozenset({"st", "nd", "rd", "th"})


def _is_numword(tok: Token) -> bool:
    return tok.is_number or tok.text in _NUMWORDS


def _reindex(tokens) -> Tuple[Token, ...]:
    return tuple(replace(t, index=i) for i, t in enumerate(tokens))


def fold_en(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    # -- pass 1: merge a digit followed by a lone ordinal suffix (5 th -> 5)
    merged = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        nxt = tokens[i + 1] if i + 1 < len(tokens) else None
        if (t.is_number and nxt is not None and not nxt.is_number
                and nxt.text in _ORD_SUFFIXES):
            merged.append(replace(t, raw=t.raw + nxt.raw))
            i += 2
            continue
        merged.append(t)
        i += 1

    # -- pass 2: fold maximal runs of spelled number-words to a digit token
    out = []
    i = 0
    n = len(merged)
    while i < n:
        if not _is_numword(merged[i]):
            out.append(merged[i])
            i += 1
            continue
        j = i
        run = []
        while j < n:
            if _is_numword(merged[j]):
                run.append(merged[j])
                j += 1
            elif (merged[j].text == "and" and run and j + 1 < n
                  and _is_numword(merged[j + 1])):
                run.append(merged[j])   # internal "and": one hundred and five
                j += 1
            else:
                break
        # a run that is a single already-digit token needs no folding
        spelled = [t for t in run if not t.is_number]
        if not spelled:
            out.extend(run)
            i = j
            continue
        text = " ".join(t.text for t in run if t.text != "and")
        value = extract_number_en(text, ordinals=True)
        if value is False or value is None:
            out.extend(run)
            i = j
            continue
        num = int(value) if float(value).is_integer() else float(value)
        raw = str(num)
        out.append(Token(text=str(num), raw=raw, index=0,
                         is_number=True, value=num))
        i = j
    return _reindex(out)
