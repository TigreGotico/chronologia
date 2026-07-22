# -*- coding: utf-8 -*-
"""BC decades for gl: "the Ns bc" -> the ten BC years N..N+9."""
import pytest

from ._corpus import AstroDate, parse, span, start_end


@pytest.mark.parametrize("text,n", [
    ('os anos 300 ac', 300),
    ('os anos 290 aec', 290),
    ('os anos 200 ac', 200),
    ('os anos 100 aec', 100),
    ('os anos 80 ac', 80),
    ('os anos 50 aec', 50),
    ('os anos 20 ac', 20),
    ('os anos 1990 aec', 1990),
    ('os anos 300 aec', 300),
    ('os anos 290 aec', 290),
])
def test_decade_bc(text, n):
    s, e = start_end(text)
    assert s == AstroDate(1 - (n + 9), 1, 1)
    assert e == AstroDate(1 - (n - 1), 1, 1)
    assert parse(text)[1] == ""


def test_decade_bc_is_ten_years_wide():
    assert span('os anos 300 ac').width.days == 3652


def test_consecutive_bc_decades_tile():
    _, older_end = start_end('os anos 300 ac')
    younger_start, _ = start_end('os anos 290 ac')
    assert older_end == younger_start == AstroDate(-298, 1, 1)
