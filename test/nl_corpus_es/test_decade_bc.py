# -*- coding: utf-8 -*-
"""BC decades: "the 300s bc" and friends -- a base-number decade on
the BC axis, hand-derived from the before_christ era registry.

Convention (see Resolver._resolve_decade_bc): "the Ns bc" names the
BC-labelled years N..N+9 (the three-hundreds BC are 309..300 BC).  In
astronomical numbering X BC == year 1-X, so the older edge (start) is the
(N+9)-th BC year == 1-(N+9), the younger edge (end, exclusive) the (N-1)-th
BC year == 1-(N-1); consecutive decades tile with no gap.  "the 300s bc" is
[-308, -298).  This tiles with scoped_bc's century boundaries (both go
through the same registry): a decade-BC span is ten years wide.
"""
import pytest

from ._corpus import AstroDate, parse, span, start_end


@pytest.mark.parametrize("text,n", [
    ('los años 300 ac', 300),
    ('los años 290 ac', 290),
    ('los años 200 ac', 200),
    ('los años 100 ac', 100),
    ('los años 80 ac', 80),
    ('los años 50 ac', 50),
    ('los años 20 ac', 20),
    ('los años 1990 ac', 1990),
    ('los años 300 aec', 300),
    ('los años 290 aec', 290),
])
def test_decade_bc(text, n):
    s, e = start_end(text)
    assert s == AstroDate(1 - (n + 9), 1, 1)
    assert e == AstroDate(1 - (n - 1), 1, 1)
    assert parse(text)[1] == ""            # marker consumed, no remainder


def test_decade_bc_is_ten_years_wide():
    assert span('los años 300 ac').width.days == 3652        # ten years, -308..-298 (two leap days)


def test_consecutive_bc_decades_tile():
    # the 300s (older) end exactly where the 290s (more recent) begin
    _, older_end = start_end('los años 300 ac')
    younger_start, _ = start_end('los años 290 ac')
    assert older_end == younger_start == AstroDate(-298, 1, 1)
