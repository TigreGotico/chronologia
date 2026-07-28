# -*- coding: utf-8 -*-
"""New Year and Orthodox Christmas (ru) -- bare prefer-future + explicit year.

"новый год" is 1 January; "рождество" / "рождество христово" is the Russian
Orthodox Christmas, 7 January (Gregorian civil date used by the engine).

Bare (no year) resolves to the next occurrence on or after the 2017-06-27
anchor -- both fall in the following January, so both bare readings land in
2018.  The explicit-year sweep pins each name to 1 / 7 January of the stated
year.  Gold is the literal calendar date, computed independently.
"""
from datetime import timedelta

import pytest

from ._corpus import AstroDate, span, start


def test_new_year_bare_prefers_future():
    assert start("новый год") == AstroDate(2018, 1, 1)
    assert span("новый год").width == timedelta(days=1)


@pytest.mark.parametrize("name", ["рождество", "рождество христово"])
def test_christmas_bare_prefers_future(name):
    assert start(name) == AstroDate(2018, 1, 7)
    assert span(name).width == timedelta(days=1)


_YEARS = (2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025)


def _cases():
    out = []
    for y in _YEARS:
        out.append((f"новый год {y}", y, 1, 1))
        out.append((f"рождество {y}", y, 1, 7))
        out.append((f"рождество христово {y}", y, 1, 7))
    return out


_CASES = _cases()


@pytest.mark.parametrize("text,y,m,d", _CASES, ids=[c[0] for c in _CASES])
def test_with_explicit_year(text, y, m, d):
    assert start(text) == AstroDate(y, m, d), text
    assert span(text).width == timedelta(days=1)
