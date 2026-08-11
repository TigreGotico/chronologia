# -*- coding: utf-8 -*-
"""R118 -- the postposed "between X and Y" range construction of Turkish.

Turkish frames a closed range with its "between" word placed AFTER the pair
("3 Mart ile 5 Nisan arasında" == "3 March and 5 April between"), unlike
English "from A to B" / "between A and B" which lead the pair.  Before this
fix the engine only recognised a LEADING range marker, so a postposed
"arasında"/"arası" range collapsed to its left endpoint alone and stranded
"ile <right> arasında" in the remainder (defect R118).

Gold values are computed by hand: ``prefer_future`` places each bare
month/day endpoint on its next occurrence on/after ``ANCHOR`` (2026-07-15
12:00, a Wednesday), a date range's end is EXCLUSIVE (the day after the
named end date, mirroring English "from March 3 to April 5"), and a bare
clock endpoint is minute-wide (mirrors English "from 9 to 5" -> ...17:01,
see test_nl_range_endpoints.py in the en corpus).
"""
from datetime import datetime

from ._corpus import ANCHOR, AstroDate, nomatch, parse, span, start_end  # noqa: F401


def _d(y, m, d):
    return AstroDate(y, m, d)


def _dt(y, m, d, h, mi=0):
    return AstroDate(y, m, d, h, mi)


# -- date ranges -------------------------------------------------------

def test_postposed_between_date_range():
    ss, ee = start_end("3 Mart ile 5 Nisan arasında")
    assert ss == _d(2027, 3, 3) and ee == _d(2027, 4, 6)


def test_postposed_between_date_range_ari_variant():
    ss, ee = start_end("5 Mart ile 10 Mart arası")
    assert ss == _d(2027, 3, 5) and ee == _d(2027, 3, 11)


def test_postposed_between_date_range_no_remainder():
    assert parse("3 Mart ile 5 Nisan arasında")[1] == ""


def test_postposed_between_year_crossing():
    # December -> January: the right endpoint's own prefer_future resolution
    # already lands a year later than the left, no extra roll needed.
    ss, ee = start_end("25 Aralık ile 5 Ocak arasında")
    assert ss == _d(2026, 12, 25) and ee == _d(2027, 1, 6)


def test_postposed_between_embedded_in_sentence():
    got = span("Toplantı 3 Mart ile 5 Nisan arasında olacak")
    assert got.start == _d(2027, 3, 3) and got.end == _d(2027, 4, 6)
    assert parse("Toplantı 3 Mart ile 5 Nisan arasında olacak")[1] \
        == "Toplantı olacak"


# -- clock ranges --------------------------------------------------------

def test_postposed_between_clock_range():
    ss, ee = start_end("saat 9 ile 17 arasında")
    assert ss == _dt(2026, 7, 16, 9, 0)
    assert ee == _dt(2026, 7, 16, 17, 1)


# -- controls: bare "A ile B" (no arasında/arası) must NOT range-bind ----

def test_bare_ile_without_arasinda_stays_unbound():
    # no trailing marker -> the postposed mechanism must not fire; the
    # sentence stays a single left-endpoint mention with the rest stranded,
    # exactly as it did before #675 -- this is NOT the two-endpoint range.
    got = parse("3 Mart ile 5 Nisan")
    assert got is not None
    s, rem = got
    assert s.start == _d(2027, 3, 3) and s.end == _d(2027, 3, 4)
    assert "ile" in rem and "5 Nisan" in rem


def test_bare_ile_clock_stays_unbound():
    got = parse("saat 9 ile 17")
    assert got is not None
    s, rem = got
    assert (s.end - s.start).total_seconds() <= 60
    assert "ile" in rem


# -- single dates are unaffected -----------------------------------------

def test_single_date_unaffected():
    ss, ee = start_end("3 Mart")
    assert ss == _d(2027, 3, 3) and ee == _d(2027, 3, 4)
