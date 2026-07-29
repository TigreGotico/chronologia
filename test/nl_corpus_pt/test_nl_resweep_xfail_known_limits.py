# -*- coding: utf-8 -*-
"""Known limitations surfaced while building the second-pass sweep files in
this directory, pinned strict-xfail with the CORRECT gold (never a wrong one)
so a future fix flips these green automatically.

1. Additive clock minutes beyond the fixed quarter/half vocabulary ("e
   vinte", "e dez", "e vinte e cinco", ...) are now composed onto the hour --
   a spoken cardinal after the "e" connector folds into the MINUTE slot, so
   the minute carries the spoken amount instead of silently staying :00.  The
   former silent-wrong is FIXED; the two pins below assert the correct minute.
   See test_nl_clock.py / test_nl_resweep_clock.py for the quarter/half sweep.

2. "início/meados/fim de <mês> de <ano>" (month-thirds with a trailing
   explicit year) now places the third inside the NAMED year -- the former
   silent-wrong (third resolved in the anchor's 2017, "de 2020" left as unread
   residue) is FIXED; the pin below asserts the correct 2020 span.  See
   test_nl_month_thirds_year.py for the full early/mid/late sweep.
"""
from datetime import timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, ad, start, start_end


def test_additive_twenty_minutes():
    dt = ANCHOR.replace(hour=7, minute=20, second=0, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    assert start("às sete e vinte") == ad(dt)


def test_additive_ten_minutes_with_meridiem():
    dt = ANCHOR.replace(hour=15, minute=10, second=0, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    assert start("às três e dez da tarde") == ad(dt)


def test_month_third_explicit_year_binds_named_year():
    # Fixed: "início/meados/fim de <mês> de <ano>" now places the third inside
    # the NAMED year (was: resolved in the anchor's own 2017, year stranded).
    s, e = start_end("início de março de 2020")
    assert s == AstroDate(2020, 3, 1)
    assert e == AstroDate(2020, 3, 11, 8, 0)
