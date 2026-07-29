# -*- coding: utf-8 -*-
"""Second-pass sweep: calendar quarters "le N trimestre <year>" and "QN
<year>" across all four quarters and twenty years spread over five decades
(1999-2049), none overlapping the small hand-picked sample already pinned in
test_nl_quarter.py.

Quarter N spans months [3N-2 .. 3N]; the exclusive end is the first of the
month after the quarter closes, rolling into the following year for Q4.
Gold is plain arithmetic, independent of the parser.
"""
import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end


_QNAMES = {1: "premier", 2: "deuxième", 3: "troisième", 4: "quatrième"}

_YEARS = [1999, 2001, 2004, 2008, 2011, 2013, 2016, 2018, 2022, 2024,
          2027, 2029, 2031, 2034, 2036, 2039, 2041, 2044, 2046, 2049]


def _bounds(y, n):
    sm = 3 * n - 2
    em = sm + 3
    if em > 12:
        return AstroDate(y, sm, 1), AstroDate(y + 1, em - 12, 1)
    return AstroDate(y, sm, 1), AstroDate(y, em, 1)


def _word_sweep():
    return [(f"{_QNAMES[n]} trimestre {y}", y, n) for y in _YEARS for n in (1, 2, 3, 4)]


def _q_sweep():
    return [(f"Q{n} {y}", y, n) for y in _YEARS for n in (1, 2, 3, 4)]


@pytest.mark.parametrize("text,y,n", _word_sweep())
def test_quarter_word_years_sweep(text, y, n):
    s, e = start_end(text)
    want_s, want_e = _bounds(y, n)
    assert (s, e) == (want_s, want_e), f"{text!r} -> {s}..{e}"


@pytest.mark.parametrize("text,y,n", _q_sweep())
def test_quarter_qnotation_years_sweep(text, y, n):
    s, e = start_end(text)
    want_s, want_e = _bounds(y, n)
    assert (s, e) == (want_s, want_e), f"{text!r} -> {s}..{e}"
