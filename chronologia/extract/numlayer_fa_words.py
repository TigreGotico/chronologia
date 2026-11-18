"""Persian written forms that read as a date word only in some positions.

Persian writes the weekdays Monday to Thursday and Sunday as a number glued to
"شنبه" ("سه‌شنبه"), and a writer or a speech recognizer often leaves a space
instead of the joiner.  The bare word "می" is both the Gregorian month May and
the durative verb prefix.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex

#: the number that opens each weekday name, with the name the locale lists.
#: "سه‌شنبه": Wiktionary, "Tuesday", from "سه" (three) and "شنبه" (Saturday).
_SPACED_WEEKDAYS = {
    "دو": "دوشنبه",
    "سه": "سه‌شنبه",
    "چهار": "چهارشنبه",
    "پنج": "پنج‌شنبه",
    "یک": "یکشنبه",
}
_SATURDAY = "شنبه"
_MAY = "می"
_MONTH_WORD = "ماه"
#: "می" followed by a verb is the durative prefix: Wiktionary lists "می" as
#: the month May only for Dari and Indo-Persian, and as "wine" for Iranian
#: Persian, and the prefix is a clitic of the verb that follows it.
_VERB_PREFIX = "می‌"


def fuse_spaced_weekdays(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Join "سه شنبه" into the one word "سه‌شنبه" (the Persian ``pre_hook``).

    Without the join the number is read as 3 and "شنبه" as Saturday.
    """
    out = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        nxt = tokens[i + 1] if i + 1 < len(tokens) else None
        name = _SPACED_WEEKDAYS.get(t.text)
        if name is not None and nxt is not None and nxt.text == _SATURDAY:
            out.append(replace(t, text=name, raw=f"{t.raw} {nxt.raw}",
                               char_end=nxt.char_end))
            i += 2
            continue
        out.append(t)
        i += 1
    return reindex(out)


def mark_verb_prefix(tokens: Tuple[Token, ...], spec=None) -> Tuple[Token, ...]:
    """Keep "می" a month only beside a day, a year, "ماه" or a clause end
    (the Persian ``post_hook``).

    A "می" with a verb after it is the durative prefix and names no month.
    """
    out = []
    for i, t in enumerate(tokens):
        if t.text == _MAY:
            prev = tokens[i - 1] if i > 0 else None
            nxt = tokens[i + 1] if i + 1 < len(tokens) else None
            month = ((prev is not None and (prev.is_number
                                            or prev.text == _MONTH_WORD))
                     or nxt is None or nxt.is_number or nxt.break_before)
            if not month:
                t = replace(t, text=_VERB_PREFIX)
        out.append(t)
    return tuple(out)
