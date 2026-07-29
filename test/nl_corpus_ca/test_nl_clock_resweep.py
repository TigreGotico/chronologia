# -*- coding: utf-8 -*-
"""Second-pass clock sweep for Catalan -- fresh combinations not touched by
``test_nl_clock.py`` (which only exercises h=1,3,9 for the fraction/meridiem
shapes) nor ``test_nl_campanar_clock.py`` (the "un/dos/tres quarts de X"
bell-tower system, deliberately out of scope here).

Two families, both anchored 2017-06-27 13:04 with prefer_future roll:

1. "les/la <hour> <fraction>" -- en punt / i quart / i mitja / menys quart --
   swept across all 12 literal hours.  Gold is the literal (hour, minute)
   pair with the standard prefer-future roll; "menys quart" targets hour
   (h-1):45 by the ordinary quarter-to convention.
2. "les/la <hour> <dayperiod>" -- del matí / de la tarda / del vespre / de
   la nit -- swept across all 12 hours.  Gold uses the standard 12h->24h
   AM/PM correspondence: matí keeps h mod 12 (12 -> 0, midnight); tarda and
   vespre use h if h==12 else h+12.  "de la nit" is a midnight-crossing BAND,
   not a uniform +12: the small hours 1..5 stay AM ("la una de la nit" ==
   01:00), the evening hours 6..11 are PM ("les deu de la nit" == 22:00) and
   twelve is midnight 00:00.  AM ceiling follows the ca madrugada band
   [00:00, 06:00); DIEC2 s.v. "nit".  This is the ordinary civil-time
   convention, not something inferred from the parser.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, start, span

_HOUR_WORDS = [
    (1, "una"), (2, "dues"), (3, "tres"), (4, "quatre"), (5, "cinc"),
    (6, "sis"), (7, "set"), (8, "vuit"), (9, "nou"), (10, "deu"),
    (11, "onze"), (12, "dotze"),
]


def _art(h):
    return "la" if h == 1 else "les"


def clk(h, mi, s=0):
    dt = ANCHOR.replace(hour=h % 24, minute=mi, second=s, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    return ad(dt)


# ---------------------------------------------------------------------------
# family 1: en punt / i quart / i mitja / menys quart, all 12 hours.
# ---------------------------------------------------------------------------

def _fraction_cases():
    out = []
    for h, w in _HOUR_WORDS:
        out.append(("%s %s en punt" % (_art(h), w), h, 0))
        out.append(("%s %s i quart" % (_art(h), w), h, 15))
        out.append(("%s %s i mitja" % (_art(h), w), h, 30))
        target_h = (h - 1) % 12  # quarter-to: hour before the named one
        out.append(("%s %s menys quart" % (_art(h), w), target_h, 45))
    return out


_FRACTION_CASES = _fraction_cases()


@pytest.mark.parametrize(
    "text,h,mi", _FRACTION_CASES,
    ids=["%s" % t for t, _, _ in _FRACTION_CASES],
)
def test_hour_fraction_all_hours(text, h, mi):
    assert start(text) == clk(h, mi)
    assert span(text).width == timedelta(minutes=1)


# ---------------------------------------------------------------------------
# family 2: del matí / de la tarda / del vespre / de la nit, all 12 hours.
# ---------------------------------------------------------------------------

def _nit(h):
    # midnight-crossing band: 12 -> midnight, 1..5 stay AM, 6..11 go PM
    if h == 12:
        return 0
    return h if h <= 5 else h + 12


_PERIODS = [
    ("del matí", lambda h: h % 12),
    ("de la tarda", lambda h: h if h == 12 else h + 12),
    ("del vespre", lambda h: h if h == 12 else h + 12),
    ("de la nit", _nit),
]


def _period_cases():
    out = []
    for h, w in _HOUR_WORDS:
        for suffix, fn in _PERIODS:
            text = "%s %s %s" % (_art(h), w, suffix)
            out.append((text, fn(h)))
    return out


_PERIOD_CASES = _period_cases()


@pytest.mark.parametrize(
    "text,h24", _PERIOD_CASES,
    ids=["%s" % t for t, _ in _PERIOD_CASES],
)
def test_hour_dayperiod_all_hours(text, h24):
    assert start(text) == clk(h24, 0)
