# -*- coding: utf-8 -*-
"""Second-pass sweep: Bulgarian fixed holidays with an explicit year, FRESH
years disjoint from test_nl_holiday_ref.py (which only pins year 2020).

"нова година <year>" / "бъдни вечер <year>" / "коледа <year>" are registered
in the shared holiday registry and resolve to a fixed month/day WITHIN the
stated year (verified against the registry's own Julian-cycle convention
already pinned in test_nl_holiday_ref.py: Christmas Eve = Jan 6, Christmas =
Jan 7). Gold below matches that registry, never the parser's own output for
a *new* year -- only the (month, day) mapping is reused, the year is fresh
per case.

A second block documents six Bulgarian national-observance names
(Ден на Освобождението Mar 3, Ден на труда May 1, Гергьовден May 6,
Ден на българската просвета May 24, Съединение Sep 6,
Ден на независимостта Sep 22) that are NOT in the holiday registry: probing
confirms the parser silently falls back to matching only the bare year
token and returns the whole-year span instead of the named day. Those are
pinned as strict xfails with the CORRECT calendar gold (never the parser's
wrong whole-year output), so a future registry addition flips them green.
"""
from datetime import timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import span, start

_FIXED = [("нова година", 1, 1), ("бъдни вечер", 12, 24), ("коледа", 12, 25)]
_YEARS = [2018, 2019, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028,
          2029, 2030, 2031, 2032, 2033, 2034, 2035, 2036, 2037, 2038]

_CASES = [(f"{h} {y}", y, m, d) for h, m, d in _FIXED for y in _YEARS]


@pytest.mark.parametrize("text,y,m,d", _CASES, ids=[c[0] for c in _CASES])
def test_fixed_holiday_explicit_year_resweep(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)
    assert span(text).width == timedelta(days=1)


_UNREGISTERED = [
    ("ден на освобождението", 3, 3),
    ("ден на труда", 5, 1),
    ("гергьовден", 5, 6),
    ("ден на българската просвета", 5, 24),
    ("съединение", 9, 6),
    ("ден на независимостта", 9, 22),
]
_XFAIL_YEARS = [2018, 2019, 2021, 2022, 2023]

_XFAIL_CASES = [(f"{h} {y}", y, m, d)
                 for h, m, d in _UNREGISTERED for y in _XFAIL_YEARS]


@pytest.mark.parametrize("text,y,m,d", _XFAIL_CASES,
                         ids=[c[0] for c in _XFAIL_CASES])
def test_national_holiday_not_yet_registered(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)
    assert span(text).width == timedelta(days=1)
