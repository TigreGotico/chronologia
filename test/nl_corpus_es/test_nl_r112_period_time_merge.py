# -*- coding: utf-8 -*-
"""R112 regression: a sentence-final period directly after a bare clock hour
must not block the weekday + clock_time merge.

Root cause (see chronologia/extract/matcher.py, HOUR slot): ``es`` is an
``ordinal_dot`` locale, so its tokenizer folds a digit run's trailing,
non-decimal period into the token's own ``raw`` (``"10." `` -- the dot is
never followed by a digit, so it can never be a decimal tail).  The old HOUR
guard, ``"." not in token.raw``, rejected that token exactly like a genuine
"10.42" HH.MM decimal, so ``clock_time`` never matched and "el viernes a las
10." stayed a date-only span with "a las 10." stranded in the remainder --
while plain "el viernes a las 10" (no trailing period) merged correctly, and
so did English ("friday at 10.", whose tokenizer never folds the dot into
``raw`` in the first place, since English is not ``ordinal_dot``).
"""
from datetime import timedelta

from ._corpus import ANCHOR, ad, start, span, nomatch

#: the Friday following the Tuesday ANCHOR (2017-06-27 -> 2017-06-30).
_FRIDAY_10 = ANCHOR.replace(month=6, day=30, hour=10, minute=0, second=0,
                            microsecond=0)


def test_sentence_final_period_merges():
    assert start("la reunión es el viernes a las 10.") == ad(_FRIDAY_10)
    assert span("la reunión es el viernes a las 10.").width == timedelta(
        minutes=1)


def test_no_period_control_still_merges():
    # the pre-existing, always-correct baseline this regression must not
    # disturb: no trailing period, merges exactly the same.
    assert start("la reunión es el viernes a las 10") == ad(_FRIDAY_10)


def test_bare_marker_hour_period():
    # minimal repro without the surrounding sentence: the merge failure lived
    # in the clock_time construction match itself, not in any sentence-level
    # scaffolding.  10:00 is already past the 13:04 anchor time, so
    # ``prefer_future`` rolls it to the next day (06-28), same as the
    # no-period baseline would.
    assert start("a las 10.") == ad(
        ANCHOR.replace(day=28, hour=10, minute=0, second=0, microsecond=0))
    assert start("a las 10") == ad(
        ANCHOR.replace(day=28, hour=10, minute=0, second=0, microsecond=0))
