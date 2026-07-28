# -*- coding: utf-8 -*-
"""Deictic daypart sweep (uk): {сьогодні/завтра/вчора}? × {вранці/вдень/
ввечері/вночі} -> the CLDR day-period band on the referenced day.

Bands (chronologia dayparts): вночі 00-04, вранці 04-12, вдень 12-18,
ввечері 18-24.  The band offsets are applied to today / +1 / -1 days derived
from the anchor by pure arithmetic.  Anchor Tue 2017-06-27 13:04.
"""
from datetime import datetime, timedelta

import pytest

from chronologia.astrodate import BASIS_RECONSTRUCTED

from ._corpus import AstroDate, span

A = datetime(2017, 6, 27, 13, 4)

# band word -> (start_hour, end_hour); end_hour 24 == start of next day
_BANDS = {
    "вночі": (0, 4),
    "вранці": (4, 12),
    "вдень": (12, 18),
    "ввечері": (18, 24),
}

# deictic prefix -> day offset from the anchor date
_DAYREF = {"сьогодні": 0, "завтра": 1, "вчора": -1}


def _band_span(day_offset, sh, eh):
    base = datetime(A.year, A.month, A.day) + timedelta(days=day_offset)
    s = base + timedelta(hours=sh)
    e = base + timedelta(hours=eh)
    return AstroDate.from_datetime(s), AstroDate.from_datetime(e)


_CASES = []
for _pref, _off in _DAYREF.items():
    for _band, (_sh, _eh) in _BANDS.items():
        _CASES.append((f"{_pref} {_band}", *_band_span(_off, _sh, _eh)))


@pytest.mark.parametrize("phrase,s,e", _CASES)
def test_daypart(phrase, s, e):
    sp = span(phrase, A)
    assert (sp.start, sp.end) == (s, e), phrase
    assert sp.basis == BASIS_RECONSTRUCTED, phrase
