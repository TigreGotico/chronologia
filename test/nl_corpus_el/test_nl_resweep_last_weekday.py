# -*- coding: utf-8 -*-
"""Second-pass sweep: "last <weekday> of <month> <year>" (el), exhaustive
over all 7 weekdays x all 12 months x a fresh batch of years.

``test_nl_last_weekday_of_month.py`` (shipped) pins exactly two hand-picked
combinations. This sweep exercises every weekday name and article/adjective
gender-agreement pair -- feminine "η τελευταία <weekday>" for the six
feminine weekday nouns, neuter "το τελευταίο Σάββατο" for the one neuter
weekday noun -- confirmed by direct probing before the sweep was written.
Gold is an independent calendar walk (``calendar.monthrange`` + backward
scan), never the parser's own output.

The ordinal "first/second/third <weekday> of <month>" construction was
probed and found broken (drops the year, ignores the weekday constraint) --
that is a known engine gap and is intentionally NOT swept here.
"""
import calendar
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, span

# weekday name -> (article, adjective, python weekday index)
WEEKDAYS = [
    ("Δευτέρα", "η", "τελευταία", 0),
    ("Τρίτη", "η", "τελευταία", 1),
    ("Τετάρτη", "η", "τελευταία", 2),
    ("Πέμπτη", "η", "τελευταία", 3),
    ("Παρασκευή", "η", "τελευταία", 4),
    ("Σάββατο", "το", "τελευταίο", 5),
    ("Κυριακή", "η", "τελευταία", 6),
]

GEN = {
    1: "ιανουαρίου", 2: "φεβρουαρίου", 3: "μαρτίου", 4: "απριλίου",
    5: "μαΐου", 6: "ιουνίου", 7: "ιουλίου", 8: "αυγούστου",
    9: "σεπτεμβρίου", 10: "οκτωβρίου", 11: "νοεμβρίου", 12: "δεκεμβρίου",
}

# fresh years, disjoint from the shipped file's 2017/2019
_YEARS = [1993, 2011, 2016, 2027, 2028, 2031]


def _last_weekday(y, m, wd):
    last = calendar.monthrange(y, m)[1]
    for d in range(last, 0, -1):
        if date(y, m, d).weekday() == wd:
            return date(y, m, d)
    raise AssertionError((y, m, wd))


_CASES = [
    (f"{art} {adj} {name} του {GEN[mo]} {y}", y, mo, wd)
    for y in _YEARS for mo in range(1, 13) for name, art, adj, wd in WEEKDAYS
]


@pytest.mark.parametrize("text,y,mo,wd", _CASES,
                          ids=[c[0] for c in _CASES])
def test_last_weekday_of_month_sweep(text, y, mo, wd):
    gold = _last_weekday(y, mo, wd)
    s = span(text)
    assert s.start == AstroDate(gold.year, gold.month, gold.day)
    nxt = gold + timedelta(days=1)
    assert s.end == AstroDate(nxt.year, nxt.month, nxt.day)
