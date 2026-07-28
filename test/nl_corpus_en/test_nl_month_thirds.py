"""Fuzzy thirds of a named month: "early july", "mid-march",
"the end of december".

The engine splits a calendar month into three EQUAL parts by total duration
(not by fixed day counts), so the internal boundaries can fall at 08:00 or
16:00 for 31-day months.  The three qualifier families map onto the parts:

    early / beginning-of   -> first third
    mid / middle-of        -> second third
    late / end-of          -> last third

The oracle below re-derives each part by independent arithmetic
(month_start + k * month_duration / 3); the parser never defines the gold.
"""
from datetime import datetime

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ad, start_end


_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5,
    "june": 6, "july": 7, "august": 8, "september": 9, "october": 10,
    "november": 11, "december": 12,
}

# qualifier surface -> (third index, needs "the ... of" framing)
_QUAL = {
    "early": (0, False),
    "the beginning of": (0, True),
    "mid": (1, False),
    "the middle of": (1, True),
    "late": (2, False),
    "the end of": (2, True),
}


def _third(year, month, k):
    s = datetime(year, month, 1)
    dur = (s + relativedelta(months=1) - s) / 3
    return ad(s + dur * k), ad(s + dur * (k + 1))


def _cases():
    out = []
    for name, m in _MONTHS.items():
        for qual, (k, framed) in _QUAL.items():
            phrase = f"{qual} {name}"
            out.append((phrase, m, k))
    return out


@pytest.mark.parametrize("text,month,k", _cases())
def test_month_third(text, month, k):
    assert start_end(text) == _third(2017, month, k)


# the hyphenated "mid-" writing resolves identically to the spaced form
@pytest.mark.parametrize("text,month", [
    ("mid-july", 7), ("mid-march", 3), ("mid-december", 12),
])
def test_hyphenated_mid(text, month):
    assert start_end(text) == _third(2017, month, 1)
