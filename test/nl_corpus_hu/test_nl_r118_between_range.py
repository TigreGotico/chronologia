# -*- coding: utf-8 -*-
"""R118 -- the postposed "between X and Y" range construction of Hungarian.

Hungarian frames a closed range with its "between" word placed AFTER the
pair ("március 3. és április 5. között" == "March 3 and April 5 between"),
unlike English "from A to B" / "between A and B" which lead the pair.
Before this fix the engine found "között" via its *lead* scan (matching
"between" wherever it sits in the sentence) but then required an "and"
split to its RIGHT -- which a trailing marker never has -- so the between
branch silently declined and the sentence fell through to whatever single
mention parsed first, e.g. "9 és 17 óra között" picked the WRONG endpoint
(17:00) and stranded "9 és között" (defect R118).

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
    ss, ee = start_end("március 3. és április 5. között")
    assert ss == _d(2018, 3, 3) and ee == _d(2018, 4, 6)


def test_postposed_between_date_range_kozt_variant():
    ss, ee = start_end("március 3. és április 5. közt")
    assert ss == _d(2018, 3, 3) and ee == _d(2018, 4, 6)


def test_postposed_between_date_range_no_remainder():
    assert parse("március 3. és április 5. között")[1] == ""


def test_postposed_between_year_crossing():
    ss, ee = start_end("december 25. és január 5. között")
    assert ss == _d(2017, 12, 25) and ee == _d(2018, 1, 6)


def test_postposed_between_embedded_in_sentence():
    got = span("A találkozó március 3. és április 5. között lesz.")
    assert got.start == _d(2018, 3, 3) and got.end == _d(2018, 4, 6)
    got_full = parse("A találkozó március 3. és április 5. között lesz.")
    assert got_full[1] == "A találkozó lesz"


# -- clock ranges --------------------------------------------------------

def test_postposed_between_clock_range():
    ss, ee = start_end("9 óra és 17 óra között")
    assert ss == _dt(2017, 6, 28, 9, 0)
    assert ee == _dt(2017, 6, 28, 17, 1)


def test_postposed_between_clock_range_bare_left():
    # the left endpoint's own "óra" is optional -- the right one still
    # licenses the bare-hour reading for both sides via the trailing marker.
    ss, ee = start_end("9 és 17 óra között")
    assert ss == _dt(2017, 6, 28, 9, 0)
    assert ee == _dt(2017, 6, 28, 17, 1)


# -- controls: a bare "A és B" (no között/közt) must NOT range-bind ------

def test_bare_es_without_kozott_stays_unbound():
    got = parse("március 3. és április 5.")
    assert got is not None
    s, rem = got
    assert s.start == _d(2018, 3, 3) and s.end == _d(2018, 3, 4)
    assert "és" in rem and "április 5." in rem


# -- single dates are unaffected -----------------------------------------

def test_single_date_unaffected():
    ss, ee = start_end("március 3.")
    assert ss == _d(2018, 3, 3) and ee == _d(2018, 3, 4)
