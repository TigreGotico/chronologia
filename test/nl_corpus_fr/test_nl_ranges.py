"""French ranges: "de A à B" / "du A au B" / "entre A et B", plus the
scoped century that reads as a 100-year span.

Endpoints are two independent sub-parses; the span runs from the start of
the left to the end of the right.
"""
from datetime import timedelta

import pytest

from ._corpus import span, start_end, AstroDate


@pytest.mark.parametrize("text,s,e", [
    ("de juin à août", AstroDate(2017, 6, 1), AstroDate(2017, 9, 1)),
    ("du 5 juillet au 8 août", AstroDate(2017, 7, 5), AstroDate(2017, 8, 9)),
    ("entre juillet et septembre", AstroDate(2017, 7, 1), AstroDate(2017, 10, 1)),
    ("de 2018 à 2020", AstroDate(2018, 1, 1), AstroDate(2021, 1, 1)),
    ("du 1er juillet au 5 juillet", AstroDate(2017, 7, 1), AstroDate(2017, 7, 6)),
])
def test_range(text, s, e):
    gs, ge = start_end(text)
    assert (gs, ge) == (s, e)


def test_weekday_range():
    # a bare weekday is a range endpoint only: Monday..Friday of the week ahead
    s, e = start_end("de lundi à vendredi")
    assert e - s == timedelta(days=5)


def test_clock_range():
    s, e = start_end("du 10h au 12h")
    assert s == AstroDate(2017, 6, 28, 10, 0)
    assert e == AstroDate(2017, 6, 28, 12, 1)


# -- scoped century reads as a 100-year span ------------------------------

def test_century_span():
    s, e = start_end("le 20e siècle")
    assert s == AstroDate(1900, 1, 1)
    assert e == AstroDate(2000, 1, 1)


from ._corpus import nomatch, ANCHOR, ad  # noqa: E402


def _d(s):
    return AstroDate(*(int(x) for x in s.split("-")))


# -- prefer-future frame stays consistent across both endpoints, dash and
# word framings alike, even when the range straddles "now" (2017-06-27) ------

@pytest.mark.parametrize("text,s,e", [
    ("20 juin - 30 juin", "2017-6-20", "2017-7-1"),          # straddle, dash
    ("10 juillet - 20 juillet", "2017-7-10", "2017-7-21"),   # both ahead
    ("du 20 juin au 30 juin", "2017-6-20", "2017-7-1"),      # straddle, word
    ("1 juin - 10 juin", "2018-6-1", "2018-6-11"),           # both behind
    ("25 juin - 5 juillet", "2017-6-25", "2017-7-6"),        # cross-month
    ("10 août - 20 septembre", "2017-8-10", "2017-9-21"),
    ("28 décembre - 3 janvier", "2017-12-28", "2018-1-4"),   # cross-year
    ("3 mars 2001 - 9 mars 2001", "2001-3-3", "2001-3-10"),  # explicit years
])
def test_dash_and_word_date_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


# -- open-ended ranges: "jusqu'à" (open start) / "depuis" (open end) --------

def test_jusqua_open_start():
    s, e = start_end("jusqu'à vendredi")
    assert s == ad(ANCHOR)
    assert e == AstroDate(2017, 7, 1)


def test_depuis_open_end():
    s, e = start_end("depuis 2010")
    assert s == AstroDate(2010, 1, 1)
    assert e == ad(ANCHOR)


@pytest.mark.parametrize("text", ["de pomme à orange", "d'ici à là"])
def test_non_temporal_range_is_none(text):
    nomatch(text)


# -- the shared-month range: the month named ONCE for the pair ---------------
# Naming the month once is the default written form of a date range in the
# Romance languages (RAE, Ortografia de la lengua espanola 5.2.5.1, and its
# counterparts), and the endpoint carrying only the bare day used to be thrown
# away -- the span collapsed onto the dated endpoint alone.  The bare day is
# read through its partner's own words, so both forms now agree.

@pytest.mark.parametrize("text", [
    "du 5 au 12 juin",
    "du 5 juin au 12 juin",
    "de 5 à 12 juin",
])
def test_shared_month_range_reads_both_days(text):
    ss, ee = start_end(text)
    assert ss == AstroDate(2018, 6, 5) and ee == AstroDate(2018, 6, 13)


def test_shared_month_range_crosses_the_year():
    ss, ee = start_end("du 28 décembre au 3 janvier")
    assert ss == AstroDate(2017, 12, 28) and ee == AstroDate(2018, 1, 4)


def test_a_without_a_from_lead_is_not_a_range():
    from ._corpus import start_end as se
    ss, ee = se("le concert est à trois heures")
    assert ss == AstroDate(2017, 6, 28, 3, 0)
    assert ee == AstroDate(2017, 6, 28, 3, 1)


@pytest.mark.parametrize("text", ["du au", "du 5 au", "du pain au vin"])
def test_du_au_garbage_never_raises(text):
    from ._corpus import parse
    parse(text)
