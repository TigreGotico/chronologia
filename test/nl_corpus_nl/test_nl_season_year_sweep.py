# -*- coding: utf-8 -*-
"""Season + explicit-year sweep (nl): "<seizoen> <jaar>".

Meteorological seasons (Northern hemisphere), 3-month blocks anchored on the
first of the month, as registered in this locale:

* lente  = [Mar 1, Jun 1)
* zomer  = [Jun 1, Sep 1)
* herfst = [Sep 1, Dec 1)
* winter = [Dec 1 (Y), Mar 1 (Y+1))   -- winter straddles the year boundary

Bounds are pure literals, independent of the parser. Anchor 2017-06-27.
"""
import pytest

from ._corpus import AstroDate, parse, start_end

_YEARS = list(range(2015, 2027))

_SEASONS = {
    "lente": lambda y: ((y, 3, 1), (y, 6, 1)),
    "zomer": lambda y: ((y, 6, 1), (y, 9, 1)),
    "herfst": lambda y: ((y, 9, 1), (y, 12, 1)),
    "winter": lambda y: ((y, 12, 1), (y + 1, 3, 1)),
}


def _build():
    cases = []
    for y in _YEARS:
        for name, fn in _SEASONS.items():
            s, e = fn(y)
            cases.append((f"{name} {y}", s, e))
    return cases


_CASES = _build()


@pytest.mark.parametrize("phrase,s,e", _CASES, ids=[c[0] for c in _CASES])
def test_season_of_year(phrase, s, e):
    assert start_end(phrase) == (AstroDate(*s), AstroDate(*e)), phrase
    assert parse(phrase)[1] == "", phrase
