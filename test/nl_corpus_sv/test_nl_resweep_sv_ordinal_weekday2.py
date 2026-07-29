# -*- coding: utf-8 -*-
"""sv (second-pass resweep): "Nth <weekday>en i <month> <year>" over the
month/year cells the first sweep (``test_sv_ordinal_weekday_sweep.py``) left
untouched.

The first sweep fixed ``_MONTH_SET = [1, 3, 6, 9, 11]`` and ``_YEARS =
[2019, 2020, 2021]``. This resweep takes the complementary months
``{2, 4, 5, 7, 8, 10, 12}`` crossed with fresh years ``{2022..2026}`` -- no
(month, year) cell overlaps the original, so no phrase here was already
exercised. The gold day is computed by INDEPENDENT calendar arithmetic
(``calendar.monthrange`` + weekday enumeration), never read back from the
parser. ``femte`` cases are emitted only for month/year/weekday triples that
genuinely contain a fifth occurrence.

Anchor Tuesday 2017-06-27; every phrase carries an explicit year, so no
prefer-future roll applies.
"""
import calendar
from datetime import datetime, timedelta

import pytest

from ._corpus import start, parse, ad, span

_ORD = {"första": 1, "andra": 2, "tredje": 3, "fjärde": 4, "femte": 5}
_WD = {
    "måndagen": 0, "tisdagen": 1, "onsdagen": 2, "torsdagen": 3,
    "fredagen": 4, "lördagen": 5, "söndagen": 6,
}
_MONTHS = {
    1: "januari", 2: "februari", 3: "mars", 4: "april", 5: "maj", 6: "juni",
    7: "juli", 8: "augusti", 9: "september", 10: "oktober", 11: "november",
    12: "december",
}
_MONTH_SET = [2, 4, 5, 7, 8, 10, 12]
_YEARS = [2022, 2023, 2024, 2025, 2026]


def _nth_weekday(year, month, weekday, n):
    """Return the day-of-month of the n-th `weekday` (0=Mon) or None."""
    days = [d for d in range(1, calendar.monthrange(year, month)[1] + 1)
            if datetime(year, month, d).weekday() == weekday]
    return days[n - 1] if len(days) >= n else None


def _build():
    cases = []
    for ordw, n in _ORD.items():
        for wdw, wd in _WD.items():
            for mo in _MONTH_SET:
                for yr in _YEARS:
                    day = _nth_weekday(yr, mo, wd, n)
                    if day is None:
                        continue
                    text = f"{ordw} {wdw} i {_MONTHS[mo]} {yr}"
                    cases.append((text, datetime(yr, mo, day)))
    return cases


_CASES = _build()


@pytest.mark.parametrize("text,gold", _CASES, ids=[c[0] for c in _CASES])
def test_ordinal_weekday_of_month_resweep(text, gold):
    assert start(text) == ad(gold)
    assert parse(text)[1] == ""
    assert span(text).width == timedelta(days=1)
