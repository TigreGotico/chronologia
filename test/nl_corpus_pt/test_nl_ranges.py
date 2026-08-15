# -*- coding: utf-8 -*-
"""Ranges.  Dash-framed ranges parse language-agnostically; the word-framed
Romance forms ("de junho a agosto", "entre ... e ...") parse too -- the "from"
lead ("de"/"desde") and "to"/"between" connectors ship per-locale, so range
framing is not English-only.  Because Portuguese "a" is a hyper-common
preposition ("às três", "vamos a Lisboa"), a bare "A a B" is only trusted as a
range when a "from" lead disambiguates it -- the adversarial cases pin that down."""
import pytest

from ._corpus import AstroDate, start_end, nomatch


@pytest.mark.parametrize("text,s,e", [
    ("junho - agosto", (2017, 6, 1), (2017, 9, 1)),
    ("janeiro - março", (2017, 1, 1), (2017, 4, 1)),
    ("5 de junho - 12 de junho", (2018, 6, 5), (2018, 6, 13)),
])
def test_dash_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


@pytest.mark.parametrize("text,s,e", [
    ("de junho a agosto", (2017, 6, 1), (2017, 9, 1)),
    ("de junho até agosto", (2017, 6, 1), (2017, 9, 1)),
    ("entre junho e agosto", (2017, 6, 1), (2017, 9, 1)),
    ("de 5 de junho a 12 de junho", (2018, 6, 5), (2018, 6, 13)),
])
def test_word_framed_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


# -- adversarial: the "a" trap.  "a" is also the clock preposition ("às três"),
# so a bare "<month> a <time>" / "às três" must NEVER become a bounded range;
# without a "from" lead the "a"-connector is untrusted and the normal single-span
# path runs (a minute-wide clock span), while a non-temporal endpoint is nomatch.
def test_a_trap_bare_month_plus_time_is_single_span():
    ss, ee = start_end("junho às três")
    assert ss == AstroDate(2017, 6, 1, 3, 0) and ee == AstroDate(2017, 6, 1, 3, 1)


def test_a_trap_clock_sentence_is_single_span():
    ss, ee = start_end("o concerto é às três")
    assert ss == AstroDate(2017, 6, 28, 3, 0) and ee == AstroDate(2017, 6, 28, 3, 1)


def test_a_trap_non_temporal_place_is_nomatch():
    nomatch("vamos a Lisboa")


from ._corpus import ANCHOR, ad  # noqa: E402


def _d(s):
    return AstroDate(*(int(x) for x in s.split("-")))


# -- dash-framed date ranges: the prefer-future frame stays consistent across
# both endpoints even when the range straddles "now" (anchor 2017-06-27) -----

@pytest.mark.parametrize("text,s,e", [
    ("20 de junho - 30 de junho", "2017-6-20", "2017-7-1"),   # straddle
    ("10 de julho - 20 de julho", "2017-7-10", "2017-7-21"),  # both ahead
    ("28 de junho - 30 de junho", "2017-6-28", "2017-7-1"),   # both ahead
    ("1 de junho - 10 de junho", "2018-6-1", "2018-6-11"),    # both behind
    ("25 de junho - 5 de julho", "2017-6-25", "2017-7-6"),    # cross-month
    ("10 de agosto - 20 de setembro", "2017-8-10", "2017-9-21"),
    ("28 de dezembro - 3 de janeiro", "2017-12-28", "2018-1-4"),  # cross-year
    ("3 de março 2001 - 9 de março 2001", "2001-3-3", "2001-3-10"),  # years
])
def test_dash_date_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


# -- open-ended ranges: "até" (open start) / "desde" (open end) -------------

def test_ate_open_start():
    s, e = start_end("até sexta-feira")
    assert s == ad(ANCHOR)
    assert e == AstroDate(2017, 7, 1)


def test_desde_open_end():
    s, e = start_end("desde 2010")
    assert s == AstroDate(2010, 1, 1)
    assert e == ad(ANCHOR)


# -- negatives: non-temporal endpoints never fabricate a range --------------

@pytest.mark.parametrize("text", ["de maçã a laranja", "de aqui a ali"])
def test_non_temporal_range_is_none(text):
    nomatch(text)


# -- the shared-month range: the month named ONCE for the pair ---------------
# Naming the month once is the default written form of a date range in the
# Romance languages (RAE, Ortografia de la lengua espanola 5.2.5.1, and its
# counterparts), and the endpoint carrying only the bare day used to be thrown
# away -- the span collapsed onto the dated endpoint alone.  The bare day is
# read through its partner's own words, so both forms now agree.

@pytest.mark.parametrize("text", [
    "de 5 a 12 de junho",
    "de 5 de junho a 12 de junho",
    "do 5 ao 12 de junho",
])
def test_shared_month_range_reads_both_days(text):
    ss, ee = start_end(text)
    assert ss == AstroDate(2018, 6, 5) and ee == AstroDate(2018, 6, 13)


def test_shared_month_range_crosses_the_year():
    ss, ee = start_end("de 28 a 31 de dezembro")
    assert ss == AstroDate(2017, 12, 28) and ee == AstroDate(2018, 1, 1)


def test_a_without_a_from_lead_is_not_a_range():
    ss, ee = start_end("o concerto é às três")
    assert ss == AstroDate(2017, 6, 28, 3, 0)
    assert ee == AstroDate(2017, 6, 28, 3, 1)


@pytest.mark.parametrize("text", ["do ao", "de 5 a", "vamos do pão ao vinho"])
def test_shared_month_garbage_never_raises(text):
    from ._corpus import parse
    parse(text)


# -- the shared-month range with the "dia" label on both ends: "dia" heads the
# idiom "dia N de <mes>" (see marker_day_label.voc) and, written alone, "dia
# N" still resolves on its own to the Nth of the ANCHOR month -- so the bare
# "5" borrowing path (test_shared_month_range_reads_both_days, above) used to
# skip it, and "do dia 2 ao dia 5 de setembro" bound only the dated right end
# ("dia 5 de setembro"), stranding "do dia 2 ao" in the remainder instead of
# reading the 2nd of September.  The label noun names no month of its own, so
# a left endpoint that is nothing but "dia" plus a day number must borrow the
# right endpoint's month exactly as a bare "5" does.

@pytest.mark.parametrize("text", [
    "do dia 5 ao dia 12 de junho",
    "de 5 ao dia 12 de junho",
    "do dia 5 a 12 de junho",
])
def test_shared_month_range_with_dayword_reads_both_days(text):
    ss, ee = start_end(text)
    assert ss == AstroDate(2018, 6, 5) and ee == AstroDate(2018, 6, 13)


def test_shared_month_range_with_dayword_crosses_the_year():
    ss, ee = start_end("do dia 28 ao dia 31 de dezembro")
    assert ss == AstroDate(2017, 12, 28) and ee == AstroDate(2018, 1, 1)


def test_shared_month_range_with_dayword_consumes_the_label():
    from ._corpus import parse
    r = parse("do dia 5 ao dia 12 de junho")
    assert r.remainder == ""


def test_dayword_both_months_named_still_works():
    # the control this defect masqueraded as correct: naming the month on
    # BOTH ends, rather than sharing it, always worked and must keep working.
    ss, ee = start_end("do dia 2 de setembro ao dia 5 de setembro")
    assert ss == AstroDate(2017, 9, 2) and ee == AstroDate(2017, 9, 6)


def test_dayword_bare_number_start_still_works():
    # the control the fix generalises from: a bare (label-less) numeral start
    # already borrowed the end's month before this fix and must still.
    ss, ee = start_end("de 2 a 5 de setembro")
    assert ss == AstroDate(2017, 9, 2) and ee == AstroDate(2017, 9, 6)


def test_dayword_single_date_still_folds_the_label():
    # a bare "dia N" not paired in a range keeps folding its own label.
    from ._corpus import parse
    r = parse("dia 15 de setembro")
    assert r.span.start == AstroDate(2017, 9, 15) and r.remainder == ""


def test_weekday_range_still_works():
    # anchor is Tuesday 2017-06-27; the next Monday-to-Friday span is 07-03..07-08
    ss, ee = start_end("de segunda a sexta")
    assert ss == AstroDate(2017, 7, 3) and ee == AstroDate(2017, 7, 8)
