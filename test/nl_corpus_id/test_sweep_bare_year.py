# -*- coding: utf-8 -*-
"""Oracle sweep: a bare four-digit year -> a whole civil year candidate.

A lone numeral is a candidate, not a reading (ruling 34).  Gold:
[Y-01-01 00:00, (Y+1)-01-01 00:00). Anchor-independent.
"""
import pytest

from ruling34 import candidate_spans

from ._corpus import ANCHOR, AstroDate


@pytest.mark.parametrize("y", list(range(1950, 2031)))
def test_bare_year_whole_year(y):
    want = (AstroDate(y, 1, 1), AstroDate(y + 1, 1, 1))
    assert want in candidate_spans(str(y), "id", ANCHOR)
