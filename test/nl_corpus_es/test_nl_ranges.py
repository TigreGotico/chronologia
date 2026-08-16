# -*- coding: utf-8 -*-
"""Ranges.  Dash-framed ranges parse language-agnostically; the word-framed
Romance forms ("de junio a agosto", "entre ... y ...") parse too -- the "from"
lead ("de"/"desde") and "to"/"between" connectors ship per-locale, so range
framing is not English-only.  Because Spanish "a" is a hyper-common preposition
("a las tres", "vamos a Madrid"), a bare "A a B" is only trusted as a range when
a "from" lead disambiguates it -- the adversarial cases below pin that down."""
import pytest

from ._corpus import AstroDate, start_end, nomatch, parse


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


# -- the shared-month range: the month named ONCE for the pair ---------------
# Naming the month once is the default written form of a date range in the
# Romance languages (RAE, Ortografia de la lengua espanola 5.2.5.1, and its
# counterparts), and the endpoint carrying only the bare day used to be thrown
# away -- the span collapsed onto the dated endpoint alone.  The bare day is
# read through its partner's own words, so both forms now agree.

@pytest.mark.parametrize("text", [
    "del 5 al 12 de junio",
    "del 5 de junio al 12 de junio",
    "de 5 a 12 de junio",
    "desde el 5 de junio hasta el 12 de junio",
])
def test_shared_month_range_reads_both_days(text):
    ss, ee = start_end(text)
    assert ss == AstroDate(2018, 6, 5) and ee == AstroDate(2018, 6, 13)


@pytest.mark.parametrize("text,s,e", [
    ("del 28 de junio al 3 de julio", (2017, 6, 28), (2017, 7, 4)),
    ("del 28 de diciembre al 3 de enero", (2017, 12, 28), (2018, 1, 4)),
    ("del 5 al 12 de agosto", (2017, 8, 5), (2017, 8, 13)),
])
def test_del_al_crosses_month_and_year(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


def test_del_al_consumes_its_framing_words():
    r = parse("del 5 al 12 de junio")
    assert r.remainder == ""


# -- adversarial: "al" is also the clock preposition, and a reversed or
# nonsensical pair must stay refused rather than fabricate a span.
def test_al_without_a_from_lead_is_not_a_range():
    # no "del" lead, so the "al" connector stays untrusted and the sentence
    # reads as the single clock span it is
    ss, ee = start_end("la cita es al mediodía")
    assert ss == AstroDate(2017, 6, 28, 12, 0)
    assert ee == AstroDate(2017, 6, 28, 12, 1)


def test_del_al_reversed_pinned_dates_fabricate_nothing():
    # both endpoints carry an explicit year, so neither may be rolled and the
    # range refuses; the ordinary single-span path reads the first date and
    # leaves the second in the remainder rather than inventing an interval
    r = parse("del 12 de junio de 2020 al 5 de junio de 2020")
    assert r.span.start == AstroDate(2020, 6, 12)
    assert r.span.end == AstroDate(2020, 6, 13)
    assert "5 de junio de 2020" in r.remainder


@pytest.mark.parametrize("text", ["del al", "del 5 al", "del pan al vino"])
def test_del_al_garbage_never_raises(text):
    parse(text)


# -- the shared-month range with the "día" label on both ends: "día" heads the
# idiom "día N de <mes>" (see marker_day_label.voc) and, written alone, "día
# N" still resolves on its own to the Nth of the ANCHOR month -- so the bare
# "5" borrowing path (test_del_al_crosses_month_and_year, above) used to skip
# it, and "del día 2 al día 5 de septiembre" bound only the dated right end
# ("día 5 de septiembre"), stranding "del día 2 al día" in the remainder
# instead of reading the 2nd of September.  The label noun names no month of
# its own, so a left endpoint that is nothing but "día" plus a day number
# must borrow the right endpoint's month exactly as a bare "5" does.

@pytest.mark.parametrize("text,s,e", [
    ("del día 5 al día 12 de agosto", (2017, 8, 5), (2017, 8, 13)),
    ("del 5 al día 12 de agosto", (2017, 8, 5), (2017, 8, 13)),
    ("del día 5 al 12 de agosto", (2017, 8, 5), (2017, 8, 13)),
])
def test_del_al_dayword_reads_both_days(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


def test_del_al_dayword_crosses_the_year():
    ss, ee = start_end("del día 28 al día 31 de diciembre")
    assert ss == AstroDate(2017, 12, 28) and ee == AstroDate(2018, 1, 1)


def test_del_al_dayword_consumes_its_framing_words():
    r = parse("del día 5 al día 12 de agosto")
    assert r.remainder == ""


def test_dayword_both_months_named_still_works():
    # the control this defect masqueraded as correct: naming the month on
    # BOTH ends, rather than sharing it, always worked and must keep working.
    ss, ee = start_end("del día 2 de septiembre al día 5 de septiembre")
    assert ss == AstroDate(2017, 9, 2) and ee == AstroDate(2017, 9, 6)


def test_dayword_bare_number_start_still_works():
    # the control the fix generalises from: a bare (label-less) numeral start
    # already borrowed the end's month before this fix and must still.
    ss, ee = start_end("del 2 al 5 de septiembre")
    assert ss == AstroDate(2017, 9, 2) and ee == AstroDate(2017, 9, 6)


def test_dayword_single_date_still_folds_the_label():
    # a bare "día N" not paired in a range keeps folding its own label.
    r = parse("día 15 de septiembre")
    assert r.span.start == AstroDate(2017, 9, 15) and r.remainder == ""
