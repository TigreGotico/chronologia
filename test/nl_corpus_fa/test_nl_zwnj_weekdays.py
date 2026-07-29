# -*- coding: utf-8 -*-
"""A Persian weekday resolves identically with or without its ZWNJ.

Persian orthography writes a compound word's parts joined by a zero-width
non-joiner (U+200C) that suppresses the cursive join: سه‌شنبه "Tuesday" and
پنج‌شنبه "Thursday" carry one internally.  The very same words are routinely
typed WITHOUT the ZWNJ (سهشنبه, پنجشنبه) -- the mark is invisible and many
keyboards omit it -- and both spellings are the same word.  Before the tokenizer
folded the ZWNJ out of the matching key, only the voc's spelling resolved and
the user's other spelling returned None (a silent wrong).

Gold is computed by independent weekday arithmetic against this corpus's Tuesday
anchor (prefer-future: a bare weekday names its next strictly-future
occurrence), never by re-running the parser.
"""
from datetime import timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, span

ZWNJ = "‌"

# (weekday word without ZWNJ, Monday=0 index).  The ZWNJ-bearing spelling is
# derived below by re-inserting the joiner where standard orthography places it
# (only the "X شنبه" compounds carry one); the simple names never do, and both
# of their "forms" coincide -- proving the fold leaves them untouched.
WEEKDAYS = [
    ("شنبه", 5),        # Saturday
    ("یکشنبه", 6),      # Sunday
    ("دوشنبه", 0),      # Monday
    ("سهشنبه", 1),      # Tuesday  (orthographic: سه‌شنبه)
    ("چهارشنبه", 2),    # Wednesday
    ("پنجشنبه", 3),     # Thursday (orthographic: پنج‌شنبه)
    ("جمعه", 4),        # Friday
]

# where standard Persian inserts the ZWNJ inside the "-shanbe" compounds
_ZWNJ_FORM = {
    "سهشنبه": "سه" + ZWNJ + "شنبه",
    "پنجشنبه": "پنج" + ZWNJ + "شنبه",
}


def _expected(idx):
    base = ANCHOR.replace(hour=0, minute=0, second=0, microsecond=0)
    ahead = (idx - base.weekday()) % 7 or 7
    s = base + timedelta(days=ahead)
    e = s + timedelta(days=1)
    return AstroDate(s.year, s.month, s.day), AstroDate(e.year, e.month, e.day)


def _both_spellings(plain):
    zwnj = _ZWNJ_FORM.get(plain, plain)
    return sorted({plain, zwnj})


CASES = [
    (surface, idx)
    for plain, idx in WEEKDAYS
    for surface in _both_spellings(plain)
]


@pytest.mark.parametrize("text,idx", CASES)
def test_weekday_resolves_regardless_of_zwnj(text, idx):
    sp = span(text)
    assert (sp.start, sp.end) == _expected(idx)


@pytest.mark.parametrize("plain,idx", [("سهشنبه", 1), ("پنجشنبه", 3)])
def test_zwnj_and_plain_agree(plain, idx):
    """The two genuine ZWNJ compounds land on the identical span either way."""
    with_zwnj = span(_ZWNJ_FORM[plain])
    without = span(plain)
    assert (with_zwnj.start, with_zwnj.end) == (without.start, without.end)
    assert (without.start, without.end) == _expected(idx)
