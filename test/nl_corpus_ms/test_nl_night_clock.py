# -*- coding: utf-8 -*-
"""ms: "pukul <N> malam" is a midnight-crossing BAND, not a uniform +12.

"malam" (night) spoken with a clock hour is not a flat PM shift: the small
hours 1..5 stay AM ("pukul satu malam" == 01:00, not 13:00), the late-night
hours 6..11 go PM ("pukul sebelas malam" == 23:00) and twelve is midnight
00:00.  Evening "malam" opens at 19:00 (CLDR ms night [19:00, 00:00),
transcribed in chronologia.dayparts); the small hours read as "malam"
colloquially.  Source: Wiktionary, malam (Malay).

Gold is the band-split computed here, never read back from the parser.
Anchor 2026-07-15 12:00 (from ._corpus): 01..05 and 00 land tomorrow
(before noon), 18..23 stay today.
"""
import pytest

from ._corpus import ANCHOR, ad, start


def _night(h):
    # midnight-crossing band: 12 -> midnight, 1..5 stay AM, 6..11 go PM
    if h == 12:
        return 0
    return h if h <= 5 else h + 12


def clk(h24):
    from datetime import timedelta
    dt = ANCHOR.replace(hour=h24, minute=0, second=0, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    return ad(dt)


@pytest.mark.parametrize("h", list(range(1, 13)))
def test_pukul_malam_band(h):
    assert start(f"pukul {h} malam") == clk(_night(h))
