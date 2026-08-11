# -*- coding: utf-8 -*-
"""R112 regression: a sentence-final period directly after a bare clock hour
must not block the weekday + clock_time merge.

Root cause (see chronologia/extract/matcher.py, HOUR slot): ``fi`` is an
``ordinal_dot`` locale, so its tokenizer folds a digit run's trailing,
non-decimal period into the token's own ``raw`` (``"10."`` -- the dot is
never followed by a digit, so it can never be a decimal tail).  The old HOUR
guard, ``"." not in token.raw``, rejected that token exactly like a genuine
"10.42" HH.MM decimal, so ``clock_time`` never matched and "perjantaina klo
10." stayed a date-only span with "klo 10." stranded in the remainder --
while plain "perjantaina klo 10" (no trailing period) merged correctly.
"""
from ._corpus import ANCHOR, ad, start, span, nomatch  # noqa: F401

#: the Friday following the Tuesday ANCHOR (2017-06-27 -> 2017-06-30).
_FRIDAY_10 = ANCHOR.replace(month=6, day=30, hour=10, minute=0, second=0,
                            microsecond=0)
#: 10:00 already past the anchor's 13:04 -> the bare, weekday-less form rolls
#: to the next day (prefer_future).
_NEXT_10 = ANCHOR.replace(day=28, hour=10, minute=0, second=0, microsecond=0)


def test_sentence_final_period_merges():
    assert start("Kokous on perjantaina klo 10.") == ad(_FRIDAY_10)


def test_no_period_control_still_merges():
    assert start("Kokous on perjantaina klo 10") == ad(_FRIDAY_10)


def test_bare_marker_hour_period():
    assert start("klo 10.") == ad(_NEXT_10)
    assert start("klo 10") == ad(_NEXT_10)
