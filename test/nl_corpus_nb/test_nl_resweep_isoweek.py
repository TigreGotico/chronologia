"""nb: ISO-8601 weeks, second-pass resweep -- fresh years 2137-2156.

``test_nl_iso_week.py`` covers years up to 2030. Mondays computed with
stdlib ``date.fromisocalendar`` -- an oracle independent of the engine, same
technique the existing corpus file uses. Weeks 1/10/20/30/40/50 exist in
every calendar year (no week-53 ambiguity).
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate

from chronologia import extract_timespan
from ._corpus import LANG, ANCHOR


def _cases():
    out = []
    for y in range(2137, 2157):
        for w in (1, 10, 20, 30, 40, 50):
            out.append((f"uke {w} av {y}", y, w))
    return out


@pytest.mark.parametrize("text,iy,iw", _cases())
def test_iso_week_resweep(text, iy, iw):
    mon = date.fromisocalendar(iy, iw, 1)
    r = extract_timespan(text, LANG, ANCHOR)
    assert r is not None, f"{text!r} did not parse"
    s, e = r[0].start, r[0].end
    assert s == AstroDate(mon.year, mon.month, mon.day)
    nxt = mon + timedelta(days=7)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)
