"""Era-qualified years composing with day-of-month, weekend-of-month and
quarter constructions.

Three verified silent-wrongs (chronologia dev f73cca4a, anchor 2026-08-10):

1. ``calendar_date`` ("1st january 500 BC", "the 1st of january 500 BC") --
   an explicit day ordinal ahead of the month broke era application: "500"
   read as the bare (common-era) Gregorian year AD 500 and "BC" stranded in
   the remainder, a silent ~1000-year error. The MONTH-only form ("january
   500 BC", no day) already worked correctly through the dedicated
   ``era_bc``/``_narrow_to_month`` path.
2. ``weekend_of_month`` ("the last weekend of june 500 BC", PR #639's
   construction) -- same bug: the year composed as bare AD 500, "BC"
   stranded.
3. ``quarter_ref`` ("the first quarter of 500 BC") -- same bug again.

The fix routes the YEAR slot of all three constructions through the same
era registry (:mod:`chronologia.eras`) the standalone ``era_bc``/``era_ad``
constructions already use, via a new optional ``ERA`` slot that binds
BC/AD markers.

**Deliberately BC/AD only** (a scope decision, not an oversight):

* calendar-backed eras (Hijri, Solar Hijri) number a DIFFERENT calendar's
  own months, so mixing them with a Gregorian MONTH/quarter slot would be
  incoherent -- they keep resolving only through their own dedicated
  era_hijri/era_solar_hijri constructions, unaffected by this fix.
* the Buddhist Era's "be" marker was tried and REVERTED: it collides with
  the common English verb "be" ("will june be there"), and unlike the
  dedicated ``era_buddhist_be`` construction (guarded to fire only at
  end-of-clause), this composed ``ERA`` slot has no such position guard --
  and because the matcher tries the longest candidate span first and does
  NOT fall back to a shorter match when the resolver declines, a
  speculative "be" bind broke ordinary sentences that used to parse fine.
  Buddhist-Era composition with day/weekend/quarter constructions stays
  unsupported: the resolvers explicitly refuse (``None``) rather than
  guess when an ``ERA``-shaped token appears without a bound ``YEAR``
  (see the small-year adversarial tests below) -- see below for the
  test that caught the regression.

Expected values are independent hand arithmetic against ASTRONOMICAL year
numbering (500 BC == astronomical year -499, 1 BC == year 0, 1 AD == year 1)
-- never read back from the parser.
"""
import pytest

from ._corpus import ANCHOR, AstroDate, parse, span, start_end


# -- 1. calendar_date: day ordinal + era-qualified year --------------------

@pytest.mark.parametrize("text, year, month, day", [
    ("1st january 500 BC", -499, 1, 1),
    ("the 1st of january 500 BC", -499, 1, 1),
    ("15th march 44 BC", -43, 3, 15),
    ("the 15th of march 44 BC", -43, 3, 15),
    ("1st january 44 AD", 44, 1, 1),
    ("25th december 44 AD", 44, 12, 25),
])
def test_day_of_month_with_era_year(text, year, month, day):
    s, e = start_end(text)
    assert s == AstroDate(year, month, day)
    assert e == AstroDate(year, month, day) + (e - s)
    assert (e - s).days == 1


def test_1st_january_500_bc_exact():
    s, e = start_end("1st january 500 BC")
    assert s == AstroDate(-499, 1, 1)
    assert e == AstroDate(-499, 1, 2)


def test_the_1st_of_january_500_bc_exact():
    s, e = start_end("the 1st of january 500 BC")
    assert s == AstroDate(-499, 1, 1)
    assert e == AstroDate(-499, 1, 2)


def test_the_15th_of_march_44_bc_adversarial():
    # the Ides of March, 44 BC -- a real, well-known historical date; a
    # famous adversarial case for an off-by-one in BC year arithmetic
    # (44 BC == astronomical -43, NOT -44).
    s, e = start_end("the 15th of march 44 BC")
    assert s == AstroDate(-43, 3, 15)
    assert e == AstroDate(-43, 3, 16)


# -- 2. weekend_of_month: era-qualified year (PR #639 construction) --------

def test_last_weekend_of_june_500_bc():
    s, e = start_end("the last weekend of june 500 BC")
    assert s.year == -499
    assert s.month == 6
    assert (e - s).days == 2
    # Saturday-opens-the-weekend convention (default locale weekend_start);
    # independently verified via the proleptic Gregorian weekday of 500 BC
    # (astronomical year -499) June -- Zeller's-congruence-equivalent JDN
    # weekday computation, cross-checked against AstroDate.weekday().
    assert s.weekday() == 5            # Saturday


def test_last_weekend_of_june_1999_still_works():
    # adversarial control: an ordinary (non-era) year must be completely
    # unaffected by the ERA-slot addition.
    s, e = start_end("the last weekend of june 1999")
    assert s == AstroDate(1999, 6, 26)
    assert e == AstroDate(1999, 6, 28)
    assert parse("the last weekend of june 1999")[1] == ""


def test_last_weekend_of_june_500_bc_remainder_fully_consumed():
    assert parse("the last weekend of june 500 BC")[1] == ""


# -- 3. quarter_ref: era-qualified year ------------------------------------

def test_first_quarter_of_500_bc():
    s, e = start_end("the first quarter of 500 BC")
    assert s == AstroDate(-499, 1, 1)
    assert e == AstroDate(-499, 4, 1)


def test_first_quarter_of_500_bc_remainder_fully_consumed():
    assert parse("the first quarter of 500 BC")[1] == ""


def test_third_quarter_of_44_bc():
    s, e = start_end("the third quarter of 44 BC")
    assert s == AstroDate(-43, 7, 1)
    assert e == AstroDate(-43, 10, 1)


def test_first_quarter_of_2026_still_works():
    # adversarial control: an ordinary (non-era) year unaffected.
    s, e = start_end("the first quarter of 2026")
    assert s == AstroDate(2026, 1, 1)
    assert e == AstroDate(2026, 4, 1)


# -- AD/CE controls: the era-qualified path must also handle the *positive*
#    (no year-shift) era correctly, not just BC ------------------------

def test_1st_january_44_ad():
    s, e = start_end("1st january 44 AD")
    assert s == AstroDate(44, 1, 1)
    assert e == AstroDate(44, 1, 2)


def test_last_weekend_of_june_44_ad():
    s, e = start_end("the last weekend of june 44 AD")
    assert s.year == 44
    assert s.month == 6
    assert (e - s).days == 2


def test_first_quarter_of_44_ad():
    s, e = start_end("the first quarter of 44 AD")
    assert s == AstroDate(44, 1, 1)
    assert e == AstroDate(44, 4, 1)


# -- Buddhist Era (BE): deliberately NOT wired into these constructions ---
# (see the module docstring -- "be" collides with the English verb and a
# resolver decline here does not fall back to a shorter match, so wiring it
# broke unrelated sentences and was reverted). ``era_buddhist_be`` itself is
# untouched and still resolves "2560 BE" correctly on its own -- only
# COMPOSING it with a day/weekend/quarter is unsupported.

def test_1st_january_2560_be_stays_unsupported_not_wrong():
    # must NOT silently misread as AD 2560 (or any other wrong year) with
    # "BE" stranded -- either it declines outright, or (as here, since
    # calendar_date's MONTH DAY? YEAR? order still binds "2560" as a bare
    # YEAR on its own) it falls back to the same behavior era-composition
    # never touched: a plain AD reading with "BE" left in the remainder.
    # Either is an acceptable, VISIBLE non-composition; a wrong year with a
    # vanished marker is not.
    r = parse("1st january 2560 BE")
    if r is not None:
        assert r[0].start.year == 2560   # bare AD reading, not BE-shifted
        assert "be" in r[1].lower()      # marker visibly stranded, not lost


def test_buddhist_era_bc_itself_unaffected():
    # the dedicated era_buddhist_be construction, untouched by this fix,
    # still resolves correctly on its own.
    s, e = start_end("2560 BE")
    assert s == AstroDate(2017, 1, 1)
    assert e == AstroDate(2018, 1, 1)


# -- existing-behavior controls: pin what already worked, unchanged --------

def test_january_500_bc_still_correct():
    # the MONTH-only (no day ordinal) form: the year was already correct
    # before this fix (via the dedicated era_bc + _narrow_to_month path),
    # though the MONTH word was left stranded in the remainder there
    # (era_bc's own order is bare "NUM bc", with no MONTH slot -- the month
    # narrowing came from a same-span-length tie-break quirk, not from
    # "january" actually being consumed). With calendar_date's own YEAR
    # slot now era-aware, this text's longest match is calendar_date's
    # "MONTH DAY? YEAR? ERA?" order instead, which correctly consumes and
    # narrows by "january" too -- same (correct) year, and now with full
    # remainder consumption as a bonus, not a regression.
    s, e = start_end("january 500 BC")
    assert s == AstroDate(-499, 1, 1)
    assert e == AstroDate(-499, 2, 1)
    assert parse("january 500 BC")[1] == ""


def test_the_year_500_bc_still_correct():
    s, e = start_end("the year 500 BC")
    assert s == AstroDate(-499, 1, 1)
    assert e == AstroDate(-498, 1, 1)


def test_2000_years_before_500_bc_still_correct():
    # anchored-offset composition ("N years before <era date>"): astronomical
    # year -499 minus 2000 == -2499.
    s, e = start_end("2000 years before 500 BC")
    assert s == AstroDate(-2499, 1, 1)
    assert e == AstroDate(-2499, 1, 2)


# -- adversarial: a small (<32, <4-digit) era-marked year refuses rather ---
#    than silently substituting the anchor's year --------------------------
#
# The generic YEAR slot only binds a number that is itself unambiguously a
# year (>=32, or >=4 digits, or apostrophe-cued); "5 BC" or "1 AD" is too
# small to bind there, so a day-of-month construction like "5th january 5
# BC" ends up with DAY consuming the trailing "5" and the era marker left
# dangling with NO year bound at all. Composing that would silently
# substitute the anchor's own year for the (unreadable) named one -- the
# exact silent-wrong failure mode this fix exists to close -- so these must
# refuse (``None``), not guess.

def test_small_era_year_refuses_not_guesses():
    assert parse("5th january 5 BC") is None


def test_small_era_year_never_silently_swallows_the_marker():
    # weekend_of_month has no competing numeric slot to steal the small
    # number, so "5 BC" simply never binds YEAR at all: it correctly falls
    # back to the (visible, non-empty) remainder -- "5 BC" stays stranded in
    # the returned remainder text -- rather than being silently CONSUMED
    # while still reading as the anchor's year. That "visible decline" is
    # the pre-existing, acceptable behavior this fix must not regress: the
    # marker must never disappear from the remainder while the date is
    # wrong.
    r = parse("the last weekend of june 5 BC")
    assert r is not None
    assert "bc" in r[1].lower()


# -- R90: "the" article stranded on era-qualified day-of-month dates -------
#
# calendar_date's "DAY of MONTH YEAR? ERA?" order (and its non-era-marked
# sibling used by the plain form below) never carried a leading ``article?``,
# unlike the sibling orders gated behind "on"/"by". "the 1st of january 500
# BC" resolved the correct (era-shifted) span but stranded "the" in the
# remainder -- and the SAME order strands "the" on an ordinary (non-era)
# date too ("the 1st of january 1999"), so this is not era-specific: the
# base order itself was missing the article, fixed once for both.

def test_the_1st_of_january_500_bc_remainder_fully_consumed():
    assert parse("the 1st of january 500 BC")[1] == ""


def test_the_15th_of_march_44_bc_remainder_fully_consumed():
    assert parse("the 15th of march 44 BC")[1] == ""


def test_the_1st_of_january_1999_remainder_fully_consumed():
    # non-era control: the same calendar_date order strands "the" here too,
    # proving the defect is in the order itself, not the ERA slot.
    s, e = start_end("the 1st of january 1999")
    assert s == AstroDate(1999, 1, 1)
    assert e == AstroDate(1999, 1, 2)
    assert parse("the 1st of january 1999")[1] == ""


def test_the_1st_of_january_1999_ad_shares_the_defect():
    # explicit AD marker, same order, same fix.
    s, e = start_end("the 1st of january 1999 AD")
    assert s == AstroDate(1999, 1, 1)
    assert e == AstroDate(1999, 1, 2)
    assert parse("the 1st of january 1999 AD")[1] == ""
