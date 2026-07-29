# -*- coding: utf-8 -*-
"""sv (second-pass resweep): full "D <month> YYYY" dates over fresh years.

``test_sv_calendar.py`` pins a handful of historically-notable dates (mostly
pre-2020). This resweep sweeps three fresh days-of-month (5, 15, 25) across
all 12 months and years 2028-2037 -- none of those (day, month, year) triples
appear in the earlier file. Gold is the literal calendar date, since the
phrase always carries an explicit year (no prefer-future roll applies).

Anchor Tuesday 2017-06-27 13:04.
"""
from datetime import timedelta

import pytest

from ._corpus import AstroDate, start, parse, span

_MONTHS = {
    1: "januari", 2: "februari", 3: "mars", 4: "april", 5: "maj", 6: "juni",
    7: "juli", 8: "augusti", 9: "september", 10: "oktober", 11: "november",
    12: "december",
}
_DAYS = [5, 15, 25]
_YEARS = list(range(2028, 2038))


def _build():
    cases = []
    for mo in range(1, 13):
        for d in _DAYS:
            for yr in _YEARS:
                cases.append((f"{d} {_MONTHS[mo]} {yr}", AstroDate(yr, mo, d)))
    return cases


_CASES = _build()


@pytest.mark.parametrize("text,gold", _CASES, ids=[c[0] for c in _CASES])
def test_full_dmy_resweep(text, gold):
    assert start(text) == gold
    assert span(text).width == timedelta(days=1)
    assert parse(text)[1] == ""
