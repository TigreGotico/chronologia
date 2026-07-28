# -*- coding: utf-8 -*-
"""Oracle sweep: DAY + bare MONTH (no year) -> the next strictly-non-past
occurrence of that civil day.  With no year given, the anchor year is kept when
that day still lies on or after the anchor date, else rolled forward one year::

    y = anchor.year;  if date(y, m, d) < anchor.date():  y += 1

The construction is exercised across all twelve months in both the Gulf/Egyptian
(يناير…ديسمبر) and Levantine (كانون الثاني…كانون الأول) naming systems, with the
bare ``D MONTH`` and the ``D من MONTH`` ("D of MONTH") phrasings, and in both
Western and Arabic-Indic (٠-٩) digits -- including digits of one script mixed
into a month name of the other, which the script-agnostic tokenizer handles the
same.  Gold is one civil day [Y-M-D, Y-M-D+1) by independent arithmetic, never
the parser.  Days are capped at 28 so every month is valid."""
from datetime import date, timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, start_end
from .test_nl_full_date_sweep import MONTHS, _arabic_indic as _ai

DAYS = [1, 3, 5, 8, 12, 15, 18, 20, 22, 25, 28]


def _next_occ(m, d):
    y = ANCHOR.year
    if date(y, m, d) < ANCHOR.date():
        y += 1
    return date(y, m, d)


def _cases():
    out = []
    for m, (gulf, lev) in MONTHS.items():
        for d in DAYS:
            s = _next_occ(m, d)
            e = s + timedelta(days=1)
            ad = _ai(d)
            for text in (
                f"{d} {gulf}",
                f"{d} {lev}",
                f"{d} من {gulf}",
                f"{ad} {gulf}",
                f"{ad} من {lev}",
                f"{ad} {lev}",
            ):
                out.append((text, s, e))
    return out


@pytest.mark.parametrize("text,s,e", _cases())
def test_day_month_next_occurrence(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(s.year, s.month, s.day)
    assert ee == AstroDate(e.year, e.month, e.day)
