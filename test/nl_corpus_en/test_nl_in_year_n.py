# -*- coding: utf-8 -*-
"""R102: "in year N" grammar-collision defects.

Three verified silent-wrongs, all English, anchor 2026-08-10 (live-tested)
and reproduced here against the corpus's own fixed ANCHOR (2017-06-27):

A) For small N (1..31), "in year N" was silently read through the
   relative-offset grammar ("in a year", +1y from the anchor) while the
   digit N was stranded, unconsumed, in the remainder -- e.g. "in year 5"
   resolved to a span one year out from the anchor with remainder "5".  The
   relative "in a year" reading must NEVER win while stranding an adjacent
   digit; the chosen policy here is that an explicit "year" word licenses a
   below-GYEAR-window (< 1000) bare number as the ABSOLUTE year N.

B) "year 1 BC" / "in 1 BC" resolved to None while "year 2 BC" / "in 2 BC"
   and bare "1 BC" all resolved -- the "1" was swallowed by the same
   stranding path as (A), which left a non-empty remainder that then tripped
   the malformed-None-start-span guard (year 0's start has no ``datetime``
   equivalent). Both must resolve to astronomical year 0, exactly like bare
   "1 BC".

C) Cosmetic stranding in the otherwise-correct cases: "in year 2030" left
   "in" in the remainder and "year 2 BC" left "year" -- the leading "in" /
   "year_word" must be consumed as part of the construction, not just the
   trailing number/era.

Independent arithmetic: astronomical year = 1 - CE_year for a "N BC" surface
(1 BC == year 0, 2 BC == year -1, ...); an absolute "year N" is the plain
Gregorian year N, Jan 1 .. Jan 1 (N+1), with no arithmetic beyond that.
"""
import pytest

from ._corpus import AstroDate, ANCHOR, nomatch, parse, span, start_end


# -- (A) small N binds the absolute year, never the stranded relative -----
@pytest.mark.parametrize("text,year", [
    ("in year 5", 5),
    ("in year 10", 10),
    ("in year 17", 17),
    ("in year 31", 31),
    ("the year 5", 5),
])
def test_small_n_binds_absolute_year_not_stranded_relative(text, year):
    got_s, got_e = start_end(text)
    assert (got_s, got_e) == (AstroDate(year, 1, 1), AstroDate(year + 1, 1, 1))
    assert parse(text)[1] == ""
    # the relative-offset reading (+1y from the 2017 anchor) is what the
    # stranded-digit bug used to produce -- assert we are NOT that.
    assert got_s.year != ANCHOR.year + 1


def test_in_year_n_never_strands_the_digit():
    # whatever the policy, "in year N" may not silently resolve as the bare
    # relative "in a year" (+1y) while leaving N unconsumed.
    result = parse("in year 5")
    assert result is not None
    span_, remainder = result
    if span_.start == AstroDate(ANCHOR.year + 1, ANCHOR.month, ANCHOR.day,
                                ANCHOR.hour, ANCHOR.minute):
        assert remainder == "", (
            "'in year 5' resolved as the relative +1y reading with the "
            "digit stranded in the remainder")


# -- (B) "1 BC" resolves through a year_word/"in" prefix, not just bare ---
@pytest.mark.parametrize("text", [
    "year 1 BC",
    "in 1 BC",
    "in the year 1 BC",
])
def test_year_one_bc_resolves_to_astronomical_year_zero(text):
    got_s, got_e = start_end(text)
    assert (got_s, got_e) == (AstroDate(0, 1, 1), AstroDate(1, 1, 1))
    assert parse(text)[1] == ""


# -- (C) the leading "in" / "year_word" is consumed, not stranded ---------
@pytest.mark.parametrize("text,s,e", [
    ("in year 2030", AstroDate(2030, 1, 1), AstroDate(2031, 1, 1)),
    ("year 2 BC", AstroDate(-1, 1, 1), AstroDate(0, 1, 1)),
])
def test_working_cases_leave_no_cosmetic_remainder(text, s, e):
    got_s, got_e = start_end(text)
    assert (got_s, got_e) == (s, e)
    assert parse(text)[1] == ""


# -- controls: must NOT change ---------------------------------------------
def test_control_in_a_year_stays_relative_plus_one():
    got_s, got_e = start_end("in a year")
    assert (got_s, got_e) == (
        AstroDate(ANCHOR.year + 1, ANCHOR.month, ANCHOR.day,
                  ANCHOR.hour, ANCHOR.minute),
        AstroDate(ANCHOR.year + 2, ANCHOR.month, ANCHOR.day,
                  ANCHOR.hour, ANCHOR.minute))
    assert parse("in a year")[1] == ""


def test_control_in_2_years_stays_relative():
    got_s, got_e = start_end("in 2 years")
    assert got_s.year == ANCHOR.year + 2


def test_control_the_year_2030():
    got_s, got_e = start_end("the year 2030")
    assert (got_s, got_e) == (AstroDate(2030, 1, 1), AstroDate(2031, 1, 1))


def test_control_bare_1_bc():
    got_s, got_e = start_end("1 BC")
    assert (got_s, got_e) == (AstroDate(0, 1, 1), AstroDate(1, 1, 1))


def test_control_bare_2_bc():
    got_s, got_e = start_end("2 BC")
    assert (got_s, got_e) == (AstroDate(-1, 1, 1), AstroDate(0, 1, 1))


def test_control_in_2_bc_span():
    got_s, got_e = start_end("in 2 BC")
    assert (got_s, got_e) == (AstroDate(-1, 1, 1), AstroDate(0, 1, 1))


def test_control_next_year():
    got_s, got_e = start_end("next year")
    assert (got_s, got_e) == (AstroDate(ANCHOR.year + 1, 1, 1),
                              AstroDate(ANCHOR.year + 2, 1, 1))


def test_control_bare_2030():
    got_s, got_e = start_end("2030")
    assert (got_s, got_e) == (AstroDate(2030, 1, 1), AstroDate(2031, 1, 1))


# -- R105: three sibling gaps of R102/#663, all one-token-away -------------

# (A) "in year 0": SMALLYEAR explicitly refuses "0" (bare "year 0" already
# resolves to None -- there is no astronomical-year-0 binding for a bare
# small-year surface), so the R102 fix does not cover N=0: it fell through
# to the "in a year" relative-offset reading with "0" stranded. Chosen
# policy: refuse "in year 0" too, matching bare "year 0"'s pinned None,
# rather than inventing a binding the bare surface doesn't have.
def test_in_year_zero_refuses_not_stranded_relative():
    nomatch("in year 0")


def test_control_bare_year_zero_stays_none():
    # pinned unchanged: bare "year 0" (no "in") already declines.
    nomatch("year 0")


# (B) "in year 5 AD": era_bc's order was widened by #663 to
# "in? article? year_word? NUM bc" but era_ad ("NUM ad" / "ad NUM") was
# never given the same prefix treatment, so "in year 5 AD" resolved via the
# SMALLYEAR year_ref reading (bug A's fix) with "AD" stranded.
def test_in_year_n_ad_no_stranded_suffix():
    got_s, got_e = start_end("in year 5 AD")
    assert (got_s, got_e) == (AstroDate(5, 1, 1), AstroDate(6, 1, 1))
    assert parse("in year 5 AD")[1] == ""


def test_control_bare_5_ad():
    got_s, got_e = start_end("5 AD")
    assert (got_s, got_e) == (AstroDate(5, 1, 1), AstroDate(6, 1, 1))
    assert parse("5 AD")[1] == ""


def test_control_in_year_5_bc_still_empty_remainder():
    got_s, got_e = start_end("in year 5 BC")
    assert (got_s, got_e) == (AstroDate(-4, 1, 1), AstroDate(-3, 1, 1))
    assert parse("in year 5 BC")[1] == ""


# (C) era constructions with an "article? year_word NUM <era>" order never
# got the leading "in?" that era_bc/most other eras already carry, so
# "in the year 30 AH" / "in year 1 BE" resolve to the correct span but
# strand the leading "in".
def test_in_the_year_n_ah_no_stranded_in():
    got_s, got_e = start_end("in the year 30 AH")
    assert (got_s, got_e) == (AstroDate(650, 9, 7), AstroDate(651, 8, 27))
    assert parse("in the year 30 AH")[1] == ""


def test_control_the_year_n_ah_unchanged():
    got_s, got_e = start_end("the year 30 AH")
    assert (got_s, got_e) == (AstroDate(650, 9, 7), AstroDate(651, 8, 27))
    assert parse("the year 30 AH")[1] == ""


def test_in_year_n_be_no_stranded_in():
    got_s, got_e = start_end("in year 1 BE")
    assert (got_s, got_e) == (AstroDate(-542, 1, 1), AstroDate(-541, 1, 1))
    assert parse("in year 1 BE")[1] == ""


def test_control_year_n_be_unchanged():
    got_s, got_e = start_end("year 1 BE")
    assert (got_s, got_e) == (AstroDate(-542, 1, 1), AstroDate(-541, 1, 1))
    assert parse("year 1 BE")[1] == ""


# -- controls: must stay exactly as pinned, including the BE/AM ambiguity
# vetoes from #644 (reverted BE) and #663 (AM veto) -------------------------
def test_control_in_the_year_5780_am_remainder_pinned():
    # long-standing pinned behaviour: a GYEAR (>=1000) match stranding a
    # trailing "AM" is NOT touched by this fix -- only the SMALLYEAR/era
    # "in?" prefix gaps are.
    got_s, got_e = start_end("in the year 5780 AM")
    assert (got_s, got_e) == (AstroDate(5780, 1, 1), AstroDate(5781, 1, 1))
    assert parse("in the year 5780 AM")[1] == "AM"


def test_control_in_the_year_1_am_stays_none():
    nomatch("in the year 1 AM")
