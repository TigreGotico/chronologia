# -*- coding: utf-8 -*-
"""BC decades for ast: "the Ns bc" -> the ten BC years N..N+9."""
import pytest

from ._corpus import AstroDate, parse, span, start_end


@pytest.mark.parametrize("text,n", [
    ('los 300s adc', 300),
    ('los 290s adc', 290),
    ('los 200s adc', 200),
    ('los 100s adc', 100),
    ('los 80s adc', 80),
    ('los 50s adc', 50),
    ('los 20s adc', 20),
    ('los 1990s adc', 1990),
])
def test_decade_bc(text, n):
    s, e = start_end(text)
    assert s == AstroDate(1 - (n + 9), 1, 1)
    assert e == AstroDate(1 - (n - 1), 1, 1)
    assert parse(text)[1] == ""


def test_decade_bc_is_ten_years_wide():
    assert span('los 300s adc').width.days == 3652


def test_consecutive_bc_decades_tile():
    _, older_end = start_end('los 300s adc')
    younger_start, _ = start_end('los 290s adc')
    assert older_end == younger_start == AstroDate(-298, 1, 1)
