# -*- coding: utf-8 -*-
"""Known Polish parsing gaps, pinned as strict xfails.

Each case asserts the linguistically CORRECT span with parser-independent gold.
They currently fail on ``dev``; ``xfail(strict=True)`` turns any future fix into
a green tripwire (the suite goes red the moment the behaviour is corrected, so
the assertion can be promoted to a normal test).  No wrong gold is ever
committed -- the asserted value is what a Polish speaker means.

Gaps captured (anchor Tuesday 2017-06-27 13:04):

* Major Polish PUBLIC holidays absent from the registry -- Święto Pracy
  (1 maja), Wniebowzięcie NMP (15 sierpnia), Święto Niepodległości
  (11 listopada), Boże Ciało (movable, Easter + 60), and the named feast
  "Konstytucji 3 Maja" (the numeric "3 maja" parses but the feast name is
  stranded).
(Explicit-year intra-month day ranges and "ostatni <weekday> <month> <year>"
now both bind -- see ``test_nl_day_range_year.py`` and
``test_pl_last_weekday_of_month.py``.)
"""
from datetime import date, timedelta

import pytest
from dateutil.easter import easter

from ._corpus import AstroDate, parse, start

_E2021 = easter(2021)  # 2021-04-04


# (phrase, correct start date, expected-clean-residue?)
_FIXED_GAPS = [
    ("święto pracy 2021", date(2021, 5, 1)),
    ("wniebowzięcie 2021", date(2021, 8, 15)),
    ("święto niepodległości 2021", date(2021, 11, 11)),
    ("boże ciało 2021", _E2021 + timedelta(days=60)),  # 2021-06-03
    ("konstytucji 3 maja 2021", date(2021, 5, 3)),
]


@pytest.mark.xfail(strict=True, reason="known pl gap: see module docstring")
@pytest.mark.parametrize("phrase,gold", _FIXED_GAPS, ids=[c[0] for c in _FIXED_GAPS])
def test_known_gap(phrase, gold):
    r = parse(phrase)
    assert r is not None
    assert r[0].start == AstroDate(gold.year, gold.month, gold.day)
    assert r[1] == ""


def test_explicit_year_intra_month_day_range_binds_both_endpoints():
    # "od 5 do 12 czerwca 2019": the trailing month AND year are named once for
    # the pair and now lend to BOTH day endpoints -- the year no longer binds
    # only to "12" and "5 do" no longer strands in the residue.
    r = parse("od 5 do 12 czerwca 2019")
    assert r is not None
    assert r[0].start == AstroDate(2019, 6, 5)
    assert r[0].end == AstroDate(2019, 6, 13)
    assert r[1] == ""
