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
# Only the SPELLED "Buddhist Era" surface is wired.  The bare "BE"
# abbreviation is DEFERRED: "be" is an extremely common English verb and the
# tokenizer lower-cases the surface (only first-letter capitalisation
# survives, which cannot tell the "BE" abbreviation from a sentence-initial
# "Be"), so a bare-"be" surface would silently misread ordinary text
# ("in 2020 be ready" -> Buddhist Era 2020).  An honest gap on "2560 BE" is
# strictly better than that regression.
@pytest.mark.parametrize("text, value", [
    ("Buddhist Era 2560", 2560),
    ("in the Buddhist Era 2560", 2560),
    ("Buddhist Era 2483", 2483),          # 1940
    ("Buddhist Era 2500", 2500),
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


def test_bare_be_abbreviation_never_reads_as_buddhist_era():
    # DEFERRED surface: "2560 BE" must NOT resolve to the (wrong) literal-year
    # reading nor to a bogus era value; a clean miss is acceptable.  Crucially
    # it must never yield the 1477 (== 2560 - 543 wired wrong) misread.
    r = parse("2560 BE")
    assert r is None or r[0].start.year != 1477



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
