# -*- coding: utf-8 -*-
"""Oracle sweep: a bare four-digit year -> the whole civil year.

Gold: [Y-01-01 00:00, (Y+1)-01-01 00:00). Anchor-independent.
"""
import pytest

from ._corpus import AstroDate, start_end


@pytest.mark.parametrize("y", list(range(1950, 2031)))
def test_bare_year_whole_year(y):
    assert start_end(str(y)) == (AstroDate(y, 1, 1), AstroDate(y + 1, 1, 1))
