# -*- coding: utf-8 -*-
"""Compound "-feira" weekdays fold into one weekday token.

Portuguese names Monday-Friday as "segunda-feira" ... "sexta-feira"; the
tokenizer splits the hyphen into two tokens, and the multiword-merge glues
them back so the whole compound binds the weekday slot -- the remainder must
be EMPTY, never a stray "feira".  A bare weekday names its next
strictly-future occurrence, a day-wide span, computed independently here.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, parse


CASES = [
    ('segunda-feira', 0),
    ('terça-feira', 1),
    ('quarta-feira', 2),
    ('quinta-feira', 3),
    ('sexta-feira', 4),
]


@pytest.mark.parametrize("text,idx", CASES)
def test_compound_weekday_empty_remainder(text, idx):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    span, remainder = r
    assert remainder == "", f"{text!r} left remainder {remainder!r}"
    ahead = (idx - ANCHOR.weekday()) % 7 or 7
    exp = (ANCHOR + timedelta(days=ahead)).date()
    assert (span.start.year, span.start.month, span.start.day) == \
        (exp.year, exp.month, exp.day)
