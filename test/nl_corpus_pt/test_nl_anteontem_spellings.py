# -*- coding: utf-8 -*-
"""The day before yesterday with the compound written apart, pt.

Priberam s.v. "anteontem": "No dia que precedeu o dia de ontem. = ANTES DE
ONTEM [...] Origem: ante- + ontem."  "ante ontem" is the compound written
apart (attested in ovos-date-parser's pt test corpus), and "antes de ontem"
is the synonym Priberam gives.  Read as "ontem" with
"ante" left over, the split form answered yesterday -- a wrong day, not a refusal.  Anchor 2017-06-27.
"""
import pytest

from ._corpus import parse, start_end, AstroDate


@pytest.mark.parametrize("text", ["anteontem", "ante ontem", "antes de ontem"])
def test_day_before_yesterday(text):
    s, e = start_end(text)
    assert s == AstroDate(2017, 6, 25)
    assert (e - s).days == 1
    assert parse(text)[1] == ""
