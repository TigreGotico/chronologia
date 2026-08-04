# -*- coding: utf-8 -*-
"""Hebrew *gematria* numeral → integer conversion.

Hebrew traditionally writes numbers with letters: the units א..ט are 1..9,
the tens י..צ are 10..90, and the hundreds ק..ת are 100..400, larger
hundreds combining additively (תק = 500, תר = 600 … תת = 800, תתק = 900).
A numeral is marked typographically -- a **geresh** ``׳`` (U+05F3) after a
lone letter, or a **gershayim** ``״`` (U+05F4) before the final letter of a
multi-letter numeral (``תשפ״ה``).  Their ASCII look-alikes ``'`` and ``"``
are accepted too.

Calendar years in the current (sixth) millennium are almost always written
in the *small count* (פרט קטן): the thousands (5000) are dropped and only
the hundreds-and-below are spelled -- ``תשפ״ה`` = ת(400)+ש(300)+פ(80)+ה(5)
= 785, meaning the Hebrew year **5785**.  The full count spells the
thousands explicitly with a leading geresh: ``ה׳תשפ״ה`` = ה(5)×1000 + 785.

``gematria_value`` gives the raw additive letter sum; ``hebrew_year_value``
applies the thousands / small-count rules to yield a calendar year.
"""
from __future__ import annotations

#: geresh / gershayim and their ASCII look-alikes.
GERESH = "׳"       # ׳
GERSHAYIM = "״"     # ״
_ASCII_GERESH = "'"
_ASCII_GERSHAYIM = '"'

#: letter → value, including the five final (sofit) forms, which carry the
#: same value as their non-final counterpart.
_LETTER = {
    "א": 1, "ב": 2, "ג": 3, "ד": 4, "ה": 5, "ו": 6, "ז": 7, "ח": 8, "ט": 9,
    "י": 10, "כ": 20, "ך": 20, "ל": 30, "מ": 40, "ם": 40, "נ": 50, "ן": 50,
    "ס": 60, "ע": 70, "פ": 80, "ף": 80, "צ": 90, "ץ": 90,
    "ק": 100, "ר": 200, "ש": 300, "ת": 400,
}


def _normalise_marks(text: str) -> str:
    """Fold the ASCII look-alikes onto the real geresh / gershayim."""
    return (text.replace(_ASCII_GERSHAYIM, GERSHAYIM)
                .replace(_ASCII_GERESH, GERESH))


def gematria_value(text: str) -> int:
    """The additive letter sum of a bare Hebrew numeral (marks stripped).

    Raises ``ValueError`` on any character that is not a Hebrew numeral
    letter.  ``ה`` → 5, ``תק`` → 500, ``תשפה`` → 785.
    """
    total = 0
    for ch in text:
        if ch in (GERESH, GERSHAYIM):
            continue
        try:
            total += _LETTER[ch]
        except KeyError:
            raise ValueError(f"not a Hebrew numeral letter: {ch!r}")
    if total == 0:
        raise ValueError(f"empty Hebrew numeral: {text!r}")
    return total


def is_gematria_numeral(text: str) -> bool:
    """Whether ``text`` is a marked Hebrew numeral (carries a geresh or
    gershayim and is otherwise all numeral letters).

    The typographic mark is required: an unmarked run of letters is ordinary
    Hebrew text (a word, a weekday name) and must never be read as a number.
    """
    s = _normalise_marks(text)
    if GERESH not in s and GERSHAYIM not in s:
        return False
    letters = [c for c in s if c not in (GERESH, GERSHAYIM)]
    if not letters:
        return False
    return all(c in _LETTER for c in letters)


def hebrew_year_value(text: str) -> int:
    """Convert a gematria year to its integer, applying the thousands rules.

    * Full count -- a leading thousands block set off by a geresh followed by
      more letters (``ה׳תשפ״ה``): the block is multiplied by 1000 and added
      to the remainder (5000 + 785 = 5785).
    * Small count -- a bare value below 1000 (``תשפ״ה`` = 785): the implied
      current-millennium thousands (5000) are added → 5785.
    * A value already ≥ 1000 is returned unchanged.

    Raises ``ValueError`` on non-numeral input.
    """
    s = _normalise_marks(text)
    thousands = 0
    if GERESH in s:
        idx = s.index(GERESH)
        head, tail = s[:idx], s[idx + 1:]
        head_letters = [c for c in head if c not in (GERESH, GERSHAYIM)]
        tail_letters = [c for c in tail if c not in (GERESH, GERSHAYIM)]
        if head_letters and tail_letters:
            # explicit thousands block: ה׳תשפ״ה
            thousands = gematria_value(head) * 1000
            s = tail
        # otherwise the geresh only marks a lone-letter numeral -> ignore it
    value = gematria_value(s)
    if thousands:
        return thousands + value
    if value < 1000:
        # small count (פרט קטן): the dropped 5000 is implied.
        return 5000 + value
    return value
