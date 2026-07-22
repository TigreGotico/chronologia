# -*- coding: utf-8 -*-
"""BC decades for oc: "the Ns bc" -> the ten BC years N..N+9."""
import pytest

from ._corpus import AstroDate, parse, span, start_end


@pytest.mark.parametrize("text,n", [
    ('los 300s acn', 300),
    ('los 290s acn', 290),
    ('los 200s acn', 200),
    ('los 100s acn', 100),
    ('los 80s acn', 80),
    ('los 50s acn', 50),
    ('los 20s acn', 20),
    ('los 1990s acn', 1990),
])
def test_decade_bc(text, n):
    s, e = start_end(text)
    assert s == AstroDate(1 - (n + 9), 1, 1)
    assert e == AstroDate(1 - (n - 1), 1, 1)
    assert parse(text)[1] == ""


def test_decade_bc_is_ten_years_wide():
    assert span('los 300s acn').width.days == 3652


def test_consecutive_bc_decades_tile():
    _, older_end = start_end('los 300s acn')
    younger_start, _ = start_end('los 290s acn')
    assert older_end == younger_start == AstroDate(-298, 1, 1)
