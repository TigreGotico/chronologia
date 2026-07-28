# -*- coding: utf-8 -*-
"""Named Russian civil holidays with an explicit year (round 2, deeper sweep).

Round 1 (``test_nl_national_holidays_2``) pinned the *bare* prefer-future
reading of each name plus two explicit-year spot checks.  This file sweeps the
explicit-year reading of every name that binds, across many years, so the
name+year composition is exercised broadly rather than sampled.

Each name resolves to its fixed civil date in the stated year -- a one-day span
[date, date+1).  Gold is the literal statutory date (hand-verified, see
``chronologia/civil_holidays/well_known.py``), never the parser.  Anchor
2017-06-27.

Note (Russian gender/case): the surfaces are the canonical nominative
multiword names ("День защитника Отечества", "Международный женский день");
the trailing bare year does not inflect them.  "Праздник весны и труда"
(1 May) is deliberately excluded -- its name is not bound by the engine and a
trailing year is read as a whole-year span (see the prep-month bug file for the
same silent-year failure mode).
"""
import pytest

from ._corpus import AstroDate, span, start

# name surface -> (fixed month, fixed day)
_NAMED = {
    "день победы": (5, 9),
    "день россии": (6, 12),
    "день защитника отечества": (2, 23),
    "день защитника": (2, 23),
    "международный женский день": (3, 8),
    "женский день": (3, 8),
    "день народного единства": (11, 4),
}

_YEARS = (2018, 2019, 2020, 2021, 2022, 2023, 2024)


def _cases():
    out = []
    for name, (m, d) in _NAMED.items():
        for y in _YEARS:
            out.append((f"{name} {y}", y, m, d))
    return out


_CASES = _cases()


@pytest.mark.parametrize("text,y,m,d", _CASES, ids=[c[0] for c in _CASES])
def test_named_holiday_with_year(text, y, m, d):
    from datetime import timedelta
    assert start(text) == AstroDate(y, m, d), text
    assert span(text).width == timedelta(days=1)
