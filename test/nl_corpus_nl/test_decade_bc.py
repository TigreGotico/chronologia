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
    ('de jaren 300 voor christus', 300),
    ('de jaren 290 voor christus', 290),
    ('de jaren 200 voor christus', 200),
    ('de jaren 100 voor christus', 100),
    ('de jaren 80 voor christus', 80),
    ('de jaren 50 voor christus', 50),
    ('de jaren 20 voor christus', 20),
    ('de jaren 1990 voor christus', 1990),
    ('de jaren 300 v.chr.', 300),
    ('de jaren 290 v.chr.', 290),
])
def test_decade_bc(text, n):
    s, e = start_end(text)
    assert s == AstroDate(1 - (n + 9), 1, 1)
    assert e == AstroDate(1 - (n - 1), 1, 1)
    assert parse(text)[1] == ""            # marker consumed, no remainder


def test_decade_bc_is_ten_years_wide():
    assert span('de jaren 300 voor christus').width.days == 3652        # ten years, -308..-298 (two leap days)


def test_consecutive_bc_decades_tile():
    # the 300s (older) end exactly where the 290s (more recent) begin
    _, older_end = start_end('de jaren 300 voor christus')
    younger_start, _ = start_end('de jaren 290 voor christus')
    assert older_end == younger_start == AstroDate(-298, 1, 1)
