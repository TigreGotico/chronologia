# -*- coding: utf-8 -*-
"""Known limitations surfaced while building the second-pass sweep files in
this directory, pinned strict-xfail with the CORRECT gold (never a wrong one)
so a future fix flips these green automatically.

1. Additive clock minutes beyond the fixed quarter/half vocabulary ("e
   vinte", "e dez", "e vinte e cinco", ...) are not picked up at all -- the
   minute silently stays :00 instead of adding the spoken amount. Only "e
   meia" / "e quarto" / "e um quarto" are wired (see test_nl_clock.py and
   test_nl_resweep_clock.py in this directory, which sweep exactly that
   vocabulary and nothing else).

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


@pytest.mark.xfail(strict=True, reason="additive clock minutes outside "
                    "meia/quarto/um quarto are not parsed; minute stays :00")
def test_additive_twenty_minutes_not_supported_yet():
    dt = ANCHOR.replace(hour=7, minute=20, second=0, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    assert start("às sete e vinte") == ad(dt)


@pytest.mark.xfail(strict=True, reason="additive clock minutes outside "
                    "meia/quarto/um quarto are not parsed; minute stays :00")
def test_additive_ten_minutes_with_meridiem_not_supported_yet():
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
