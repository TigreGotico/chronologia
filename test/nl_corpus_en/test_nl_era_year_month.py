"""Buddhist Era vocab + era-anchored year narrowed by a calendar month.

Two verified silent-wrongs:

1. the Buddhist Era ("Buddhist Era 2560", "2560 BE") was defined in the era
   registry (BE == CE + 543) but no English surface routed to it, so the BE
   number was read literally as a Gregorian year and the era name stranded;

2. an era-anchored year that already resolved correctly (a Japanese nengo
   like "Reiwa 2" -> 2020, or a Buddhist-Era year) could not be narrowed by
   an adjacent calendar month ("Reiwa 2 May"): the month stranded and the
   span stayed the whole year.

Reference values are independent of the parser -- BE years come from
:func:`chronologia.resolve_era`, month spans from hand arithmetic.
"""
import pytest

from chronologia import resolve_era

from ._corpus import ANCHOR, AstroDate, parse, span, start_end


# -- Buddhist Era: BE == CE + 543, epoch-correct + name consumed ----------
# Both the SPELLED "Buddhist Era" surface and the bare "BE" abbreviation are
# wired.  "be" is an extremely common English verb, so the bare abbreviation
# fires ONLY at end-of-clause (nothing trailing) -- "2560 BE" resolves, but
# the verb collision "in 2020 be ready" is refused (see the guard test below).
# This used to be a DELIBERATE GAP ("2560 BE" was left unresolved) because a
# naive bare-"be" surface silently misread ordinary text; the end-of-clause
# guard is what makes the feature safe to wire.
@pytest.mark.parametrize("text, value", [
    ("Buddhist Era 2560", 2560),
    ("in the Buddhist Era 2560", 2560),
    ("Buddhist Era 2483", 2483),          # 1940
    ("Buddhist Era 2500", 2500),
    ("2560 BE", 2560),                    # bare abbreviation, now wired
    ("2540 BE", 2540),                    # 1997
    ("2560 B.E.", 2560),                  # dotted abbreviation
])
def test_buddhist_era_resolves_through_epoch(text, value):
    s = span(text)
    expected = resolve_era("buddhist", value)
    assert s.start.year == expected.year
    assert s.start == AstroDate(expected.year, 1, 1)
    assert parse(text)[1] == ""          # era name fully consumed


def test_buddhist_2560_is_2017():
    s, e = start_end("Buddhist Era 2560")
    assert s == AstroDate(2017, 1, 1)
    assert e == AstroDate(2018, 1, 1)


def test_bare_be_2540_is_1997():
    # bare "BE" now wired (used to be a deliberate gap): BE 2540 == 1997 CE
    s, e = start_end("2540 BE")
    assert s == AstroDate(1997, 1, 1)
    assert e == AstroDate(1998, 1, 1)
    assert parse("2540 BE")[1] == ""      # abbreviation fully consumed


def test_bare_be_verb_collision_is_refused():
    # "be" is a common English verb; the bare abbreviation fires ONLY at
    # end-of-clause.  Ordinary text with a trailing continuation must NOT
    # misread the year as a Buddhist-Era value (the 1477 == 2020 - 543 misread
    # the original deferral guarded against): the year reads as the plain
    # Gregorian 2020 with "be ready" stranded, never Buddhist Era 2020.
    s, e = start_end("in 2020 be ready")
    assert s == AstroDate(2020, 1, 1)
    assert parse("in 2020 be ready")[1] == "be ready"


def test_the_year_2560_be_is_gregorian_2017():
    # BE aligns with Gregorian year boundaries, so "the year 2560 BE" is the
    # whole Gregorian year 2017 -- it used to lose the parse to the longer bare
    # year_ref ("the year 2560") and read 2560 as a literal Gregorian year.
    s, e = start_end("the year 2560 BE")
    assert s == AstroDate(2017, 1, 1) and e == AstroDate(2018, 1, 1)
    assert start_end("year 2560 BE")[0] == AstroDate(2017, 1, 1)


@pytest.mark.parametrize("prefixed, bare", [
    ("the year 2560 BE", "2560 BE"),
    ("the year 1447 AH", "1447 AH"),
    ("the year 1404 solar hijri", "1404 solar hijri"),
])
def test_the_year_prefix_matches_the_bare_abbreviation_era(prefixed, bare):
    # the "the year <N>" prefix must not change the era resolution: the single-
    # token abbreviation (BE/AH/SH) used to lose the parse to the bare year_ref,
    # stranding the marker; now it resolves identically to the bare form (AH/SH
    # years do NOT start on Jan 1, so parity -- not a Jan-1 span -- is the pin).
    assert start_end(prefixed) == start_end(bare)



# -- era-anchored year narrowed by an adjacent named month ----------------
@pytest.mark.parametrize("text, year, month", [
    ("Reiwa 2 May", 2020, 5),
    ("Showa 63 May", 1988, 5),
    ("Buddhist Era 2560 May", 2017, 5),
    ("Reiwa 2 March", 2020, 3),
])
def test_era_year_narrowed_by_month(text, year, month):
    s, e = start_end(text)
    assert s == AstroDate(year, month, 1)
    nyear, nmonth = (year + 1, 1) if month == 12 else (year, month + 1)
    assert e == AstroDate(nyear, nmonth, 1)
    assert parse(text)[1] == ""          # month fully consumed


# -- regression: bare era-years keep their whole-year span ----------------
@pytest.mark.parametrize("text, year", [
    ("Reiwa 2", 2020),
    ("Showa 63", 1988),
])
def test_bare_era_year_stays_whole_year(text, year):
    s, e = start_end(text)
    assert s == AstroDate(year, 1, 1)
    assert e == AstroDate(year + 1, 1, 1)


@pytest.mark.parametrize("text, year", [
    ("100 AD", 100), ("500 CE", 500),
])
def test_plain_ad_era_years_unchanged(text, year):
    assert start_end(text)[0] == AstroDate(year, 1, 1)


def test_bce_year_unchanged():
    # BC years correctly have start_datetime=None but a valid .start AstroDate
    assert start_end("500 BCE")[0] == AstroDate(1 - 500, 1, 1)


# -- regression: the common verb "be" after a year is NEVER an era --------
@pytest.mark.parametrize("text, year", [
    ("in 2020 be ready", 2020),
    ("by 1999 be there", 1999),
    ("2020 be there", 2020),
    ("it will be 2020", 2020),
])
def test_be_verb_after_year_stays_plain_year(text, year):
    # "<year> be ..." must read the bare Gregorian year, never Buddhist Era
    # (which would give year - 543: 2020 -> 1477, 1999 -> 1456).
    assert start_end(text)[0] == AstroDate(year, 1, 1)
