# -*- coding: utf-8 -*-
"""SECOND-PASS resweep: locative ordinal/last-weekday-of-month (hr), fresh
years and full weekday x month coverage.

The genitive idiom ("treći ponedjeljak ožujka 2020") and a narrow locative
sample ("treći ponedjeljak u ožujku 2020") are already covered by
test_nl_ordinal_weekday_sweep and test_nl_lastwd_locative/
test_nl_locative_ordinal_xfail (the locative scope gap fixed upstream in
#363, promoted from strict-xfail to a plain assertion).  This resweep widens
the locative construction to all 7 weekdays x all 12 months on fresh years
that neither of those files touches (2022-2025; the earlier files use
2017/2019/2020/2021).

Gold is an INDEPENDENT calendar walk (``_nth_weekday`` / ``_last_weekday``)
that never touches the parser.  Anchor Tuesday 2017-06-27 13:04.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, parse

_LOC = {1: 'siječnju', 2: 'veljači', 3: 'ožujku', 4: 'travnju', 5: 'svibnju',
        6: 'lipnju', 7: 'srpnju', 8: 'kolovozu', 9: 'rujnu', 10: 'listopadu',
        11: 'studenom', 12: 'prosincu'}

# masculine weekdays take masculine ordinals/determiner; feminine weekdays
# (srijeda, subota, nedjelja) take feminine concord.
_MASC_WD = {'ponedjeljak': 0, 'utorak': 1, 'četvrtak': 3, 'petak': 4}
_FEM_WD = {'srijeda': 2, 'subota': 5, 'nedjelja': 6}
_ALL_WD = {**_MASC_WD, **_FEM_WD}
_MASC_ORD = {1: 'prvi', 2: 'drugi', 3: 'treći', 4: 'četvrti'}
_FEM_ORD = {1: 'prva', 2: 'druga', 3: 'treća', 4: 'četvrta'}


def _nth_weekday(y, m, weekday, n):
    d = date(y, m, 1)
    c = 0
    while d.month == m:
        if d.weekday() == weekday:
            c += 1
            if c == n:
                return d
        d += timedelta(days=1)
    return None


def _last_weekday(y, m, weekday):
    d = date(y + 1, 1, 1) if m == 12 else date(y, m + 1, 1)
    d -= timedelta(days=1)
    while d.weekday() != weekday:
        d -= timedelta(days=1)
    return d


def _assert(phrase, gold):
    r = parse(phrase)
    assert r is not None, phrase
    assert r[0].start == AstroDate(gold.year, gold.month, gold.day), phrase


# --- Nth-weekday-of-month, locative, fresh years 2022-2024 -----------------
# ordinal cycles 1..4 per month to cover every ordinal across the year
# without exploding the case count; every weekday x month pair is exercised.
_NTH_CASES = []
for _y in (2022, 2023, 2024):
    for _wn, _wd in _ALL_WD.items():
        _ord_table = _MASC_ORD if _wn in _MASC_WD else _FEM_ORD
        for _m in range(1, 13):
            _n = ((_m - 1) % 4) + 1
            _g = _nth_weekday(_y, _m, _wd, _n)
            if _g is None:
                continue
            _NTH_CASES.append(
                (f"{_ord_table[_n]} {_wn} u {_LOC[_m]} {_y}", _y, _m, _g.day))


@pytest.mark.parametrize("phrase,y,m,d", _NTH_CASES,
                          ids=[c[0] for c in _NTH_CASES])
def test_locative_nth_weekday_resweep(phrase, y, m, d):
    _assert(phrase, date(y, m, d))


# --- last-weekday-of-month, locative, fresh years 2022/2023/2025 -----------
_LAST_CASES = []
for _y in (2022, 2023, 2025):
    for _wn, _wd in _ALL_WD.items():
        _det = 'posljednji' if _wn in _MASC_WD else 'posljednja'
        for _m in range(1, 13):
            _g = _last_weekday(_y, _m, _wd)
            _LAST_CASES.append(
                (f"{_det} {_wn} u {_LOC[_m]} {_y}", _y, _m, _g.day))


@pytest.mark.parametrize("phrase,y,m,d", _LAST_CASES,
                          ids=[c[0] for c in _LAST_CASES])
def test_locative_last_weekday_resweep(phrase, y, m, d):
    _assert(phrase, date(y, m, d))
