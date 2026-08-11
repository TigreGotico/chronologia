# -*- coding: utf-8 -*-
"""R118 -- the postposed "between X and Y" range construction of Finnish.

Finnish frames a closed range with its "between" word placed AFTER the
pair ("maaliskuun 3. ja huhtikuun 5. välillä" == "of-March 3rd and
of-April 5th between"), unlike English "from A to B" / "between A and B"
which lead the pair.  Before this fix the engine only recognised a LEADING
range marker, so a postposed "välillä" range collapsed to its left endpoint
alone and stranded "ja <right> välillä" in the remainder (defect R118).

Gold values are computed by hand: ``prefer_future`` places each bare
month/day endpoint on its next occurrence on/after ``ANCHOR`` (2017-06-27
13:04, a Tuesday), a date range's end is EXCLUSIVE (the day after the named
end date), and a bare clock endpoint is minute-wide (mirrors English "from
9 to 5" -> ...17:01, see test_nl_range_endpoints.py in the en corpus).
"""
from ._corpus import ANCHOR, AstroDate, nomatch, parse, span, start_end  # noqa: F401


def _d(y, m, d):
    return AstroDate(y, m, d)


def _dt(y, m, d, h, mi=0):
    return AstroDate(y, m, d, h, mi)


# -- date ranges -------------------------------------------------------

def test_postposed_between_date_range():
    ss, ee = start_end("maaliskuun 3. ja huhtikuun 5. välillä")
    assert ss == _d(2018, 3, 3) and ee == _d(2018, 4, 6)


def test_postposed_between_date_range_valisena_aikana_variant():
    ss, ee = start_end("maaliskuun 3. ja huhtikuun 5. välisenä aikana")
    assert ss == _d(2018, 3, 3) and ee == _d(2018, 4, 6)


def test_postposed_between_date_range_no_remainder():
    assert parse("maaliskuun 3. ja huhtikuun 5. välillä")[1] == ""


def test_postposed_between_year_crossing():
    ss, ee = start_end("joulukuun 25. ja tammikuun 5. välillä")
    assert ss == _d(2017, 12, 25) and ee == _d(2018, 1, 6)


def test_postposed_between_embedded_in_sentence():
    got = span("Tapaaminen on maaliskuun 3. ja huhtikuun 5. välillä.")
    assert got.start == _d(2018, 3, 3) and got.end == _d(2018, 4, 6)
    got_full = parse("Tapaaminen on maaliskuun 3. ja huhtikuun 5. välillä.")
    assert got_full[1] == "Tapaaminen on"


# -- clock ranges --------------------------------------------------------

def test_postposed_between_clock_range():
    ss, ee = start_end("kello 9 ja 17 välillä")
    assert ss == _dt(2017, 6, 28, 9, 0)
    assert ee == _dt(2017, 6, 28, 17, 1)


# -- controls: a bare "A ja B" (no välillä) must NOT range-bind ----------

def test_bare_ja_without_valilla_stays_unbound():
    got = parse("maaliskuun 3. ja huhtikuun 5.")
    assert got is not None
    s, rem = got
    assert s.start == _d(2018, 3, 3) and s.end == _d(2018, 3, 4)
    assert "ja" in rem and "huhtikuun 5." in rem


# -- single dates are unaffected -----------------------------------------

def test_single_date_unaffected():
    ss, ee = start_end("maaliskuun 3.")
    assert ss == _d(2018, 3, 3) and ee == _d(2018, 3, 4)
