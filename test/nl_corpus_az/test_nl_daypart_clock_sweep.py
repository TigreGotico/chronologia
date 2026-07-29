# -*- coding: utf-8 -*-
"""Daypart marker + clock hour in Azerbaijani.

The evening marker "axşam" shifts a named 1..11 hour into the 13..23 band; the
morning marker "səhər" leaves the named hour untouched.  In both cases the span
is the next occurrence of that effective hour after the anchor (2017-06-27
13:04).  Gold is computed independently from the marker semantics, never from
the parser.
"""
from datetime import datetime, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start

A = datetime(2017, 6, 27, 13, 4)

_WORD = {
    1: "bir", 2: "iki", 3: "üç", 4: "dörd", 5: "beş", 6: "altı",
    7: "yeddi", 8: "səkkiz", 9: "doqquz", 10: "on", 11: "on bir",
    12: "on iki",
}


def _night24(h12):
    """NIGHT band-split (gecə): a midnight-crossing band, not a uniform +12 PM
    shift.  Small hours 1..5 stay AM (01..05); evening hours 6..11 are PM
    (18..23); twelve is midnight (00)."""
    if h12 == 12:
        return 0
    if 6 <= h12 <= 11:
        return h12 + 12
    return h12


def _next(hour):
    cand = A.replace(hour=hour, minute=0, second=0, microsecond=0)
    if cand <= A:
        cand += timedelta(days=1)
    return AstroDate(cand.year, cand.month, cand.day, hour, 0)


@pytest.mark.parametrize("h", list(range(1, 12)))
def test_axsam_evening_shift_word(h):
    g = _next(h + 12)
    assert start("axşam saat " + _WORD[h], A) == g


@pytest.mark.parametrize("h", list(range(1, 12)))
def test_axsam_evening_shift_digit(h):
    g = _next(h + 12)
    assert start("axşam saat %d" % h, A) == g


@pytest.mark.parametrize("h", list(range(1, 12)))
def test_sehér_morning_keeps_hour_word(h):
    g = _next(h)
    assert start("səhər saat " + _WORD[h], A) == g


@pytest.mark.parametrize("h", list(range(1, 12)))
def test_sehér_morning_keeps_hour_digit(h):
    g = _next(h)
    assert start("səhər saat %d" % h, A) == g


@pytest.mark.parametrize("h", list(range(1, 13)))
def test_gece_night_band_word(h):
    """"gecə saat N" is the NIGHT band, which crosses midnight -- three at
    night is 03:00, nine at night is 21:00, twelve at night is 00:00."""
    g = _next(_night24(h))
    assert start("gecə saat " + _WORD[h], A) == g
