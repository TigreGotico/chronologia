# -*- coding: utf-8 -*-
"""Ranges.  Dash-framed ranges parse language-agnostically; the word-framed
Romance forms ("de junio a agosto", "entre ... y ...") parse too -- the "from"
lead ("de"/"desde") and "to"/"between" connectors ship per-locale, so range
framing is not English-only.  Because Spanish "a" is a hyper-common preposition
("a las tres", "vamos a Madrid"), a bare "A a B" is only trusted as a range when
a "from" lead disambiguates it -- the adversarial cases below pin that down."""
import pytest

from ._corpus import AstroDate, start_end, nomatch


@pytest.mark.parametrize("text,s,e", [
    ("junio - agosto", (2017, 6, 1), (2017, 9, 1)),
    ("enero - marzo", (2017, 1, 1), (2017, 4, 1)),
    ("5 de junio - 12 de junio", (2018, 6, 5), (2018, 6, 13)),
])
def test_dash_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


@pytest.mark.parametrize("text,s,e", [
    ("de junio a agosto", (2017, 6, 1), (2017, 9, 1)),
    ("de junio hasta agosto", (2017, 6, 1), (2017, 9, 1)),
    ("entre junio y agosto", (2017, 6, 1), (2017, 9, 1)),
    ("de 5 de junio a 12 de junio", (2018, 6, 5), (2018, 6, 13)),
])
def test_word_framed_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


# -- adversarial: the "a" trap.  "a" is also the clock preposition ("a las 3"),
# so a bare "<month> a <time>" / "a las tres" must NEVER become a bounded range;
# without a "from" lead the "a"-connector is untrusted and the normal single-span
# path runs (a minute-wide clock span), while a non-temporal endpoint is nomatch.
def test_a_trap_bare_month_plus_time_is_single_span():
    # "junio a las tres" folds month+clock into ONE minute-wide span, not a range
    ss, ee = start_end("junio a las tres")
    assert ss == AstroDate(2017, 6, 1, 3, 0) and ee == AstroDate(2017, 6, 1, 3, 1)


def test_a_trap_clock_sentence_is_single_span():
    ss, ee = start_end("el concierto es a las tres")
    assert ss == AstroDate(2017, 6, 28, 3, 0) and ee == AstroDate(2017, 6, 28, 3, 1)


def test_a_trap_non_temporal_place_is_nomatch():
    nomatch("vamos a Madrid")


from ._corpus import ANCHOR, ad  # noqa: E402


def _d(s):
    return AstroDate(*(int(x) for x in s.split("-")))


@pytest.mark.parametrize("text,s,e", [
    ("20 de junio - 30 de junio", "2017-6-20", "2017-7-1"),   # straddle
    ("10 de julio - 20 de julio", "2017-7-10", "2017-7-21"),  # both ahead
    ("28 de junio - 30 de junio", "2017-6-28", "2017-7-1"),   # both ahead
    ("1 de junio - 10 de junio", "2018-6-1", "2018-6-11"),    # both behind
    ("25 de junio - 5 de julio", "2017-6-25", "2017-7-6"),    # cross-month
    ("10 de agosto - 20 de septiembre", "2017-8-10", "2017-9-21"),
    ("28 de diciembre - 3 de enero", "2017-12-28", "2018-1-4"),  # cross-year
    ("3 de marzo 2001 - 9 de marzo 2001", "2001-3-3", "2001-3-10"),  # years
])
def test_dash_date_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


# -- open-ended ranges: "hasta" (open start) / "desde" (open end) -----------

def test_hasta_open_start():
    s, e = start_end("hasta viernes")
    assert s == ad(ANCHOR)
    assert e == AstroDate(2017, 7, 1)


def test_desde_open_end():
    s, e = start_end("desde 2010")
    assert s == AstroDate(2010, 1, 1)
    assert e == ad(ANCHOR)


@pytest.mark.parametrize("text", ["de manzana a naranja", "de aquí a allí"])
def test_non_temporal_range_is_none(text):
    nomatch(text)
