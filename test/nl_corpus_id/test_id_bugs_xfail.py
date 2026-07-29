# -*- coding: utf-8 -*-
"""Native-review BUG log for the Indonesian locale, pinned as strict xfails.

Each case is idiomatic Indonesian whose correct reading is certain; the parser
on ``dev`` mis-resolves or strands part of the phrase. Strict xfail means the
day one of these starts passing, CI flips red and the pin must be removed.
Anchor: mission Tuesday 2017-06-27 13:04.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import AstroDate, parse, span

A = datetime(2017, 6, 27, 13, 4)


# -- wrong resolution: the resolved instant itself is incorrect ---------------
_WRONG = [
    # NOTE: "kemarin dulu"/"kemarin dahulu" (day before yesterday, -2) was fixed
    # and is now pinned green in test_nl_relative.py::test_named_days.
    # "tadi malam" = last night = YESTERDAY evening; parser gives tonight.
    ("tadi malam", AstroDate(2017, 6, 26, 18, 0)),
    # ordinal-weekday-of-month: "Senin ketiga Maret 2019" = the third Monday of
    # March 2019 = 2019-03-18; parser folds the bare weekday and strands the
    # ordinal + month (homograph handling tracked in #228/#237).
    ("Senin ketiga Maret 2019", AstroDate(2019, 3, 18)),
]


@pytest.mark.xfail(strict=True, reason="id: mis-resolved deictic / ordinal-weekday")
@pytest.mark.parametrize("text,gold_start", _WRONG)
def test_wrong_resolution(text, gold_start):
    assert span(text, A).start == gold_start


# -- stranded residue: span is right but part of the idiom is left unconsumed -
_RESIDUE = ["pagi ini", "tadi pagi", "nanti malam"]


@pytest.mark.xfail(strict=True, reason="id: daypart deictic strands a modifier word")
@pytest.mark.parametrize("text", _RESIDUE)
def test_daypart_deictic_fully_consumed(text):
    r = parse(text, A)
    assert r is not None and r[1].strip() == "", f"stranded residue {r[1]!r}"
