# -*- coding: utf-8 -*-
"""BC decades for ro: "the Ns bc" -> the ten BC years N..N+9."""
import pytest

from ._corpus import AstroDate, parse, span, start_end


@pytest.mark.parametrize("text,n", [
    ('300 i ihr', 300),
    ('290 i ihr', 290),
    ('200 i ihr', 200),
    ('100 i ihr', 100),
    ('80 i ihr', 80),
    ('50 i ihr', 50),
    ('20 i ihr', 20),
    ('1990 i ihr', 1990),
])
def test_decade_bc(text, n):
    s, e = start_end(text)
    assert s == AstroDate(1 - (n + 9), 1, 1)
    assert e == AstroDate(1 - (n - 1), 1, 1)
    assert parse(text)[1] == ""


def test_decade_bc_is_ten_years_wide():
    assert span('300 i ihr').width.days == 3652


def test_consecutive_bc_decades_tile():
    _, older_end = start_end('300 i ihr')
    younger_start, _ = start_end('290 i ihr')
    assert older_end == younger_start == AstroDate(-298, 1, 1)
