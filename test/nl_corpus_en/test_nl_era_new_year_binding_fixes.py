"""Three verified silent-wrongs in era-year / new-year YEAR binding (R74).

1. bare-BE trailing veto over-fired: an explicit year-word cue ("the year
   2560 BE or so") was vetoed anyway and fell back to the confidently WRONG
   plain literal year 2560 (should be 2017, BE 2560 - 543); the truly bare
   form ("2560 BE or so", no year-word cue) must decline to a clean None
   rather than bind the same wrong literal year, while the ordinary verb
   collision ("2020 be ready") must keep declining the era and binding the
   plain year as before.
2. two-digit-year pivot inconsistency in ``new_year_ref``: "new year 99"
   correctly pivoted (1999) but "new year 27" did not (the YEAR slot's >=32
   day-of-month gate silently rejected values <32, stranding "27" in the
   remainder and defaulting to the prefer-future bare reading).
3. the definite-article veto on ``new_year_ref`` ("the new year" is the
   ambiguous "coming year" period, not the holiday) blanket-fired even when
   an explicit year was bound ("the new year 2027"), discarding the
   unambiguous day-wide New Year's Day reading.

Reference values are independent of the parser: BE/AH come from
:func:`chronologia.resolve_era` (the epoch-correct registry resolver); the
two-digit pivot and explicit years are plain arithmetic.
"""
from datetime import datetime

from chronologia import extract_timespan, resolve_era

from ._corpus import AstroDate

# guard anchor from the task brief: 5 Aug 2026.
_TODAY = datetime(2026, 8, 5)
# the new-year-consistency corpus's own anchor (1 Mar 2026, noon).
_NY_ANCHOR = datetime(2026, 3, 1, 12, 0)


def _ts(text, anchor=_TODAY):
    return extract_timespan(text, "en", anchor)


# -- defect 1: bare-BE trailing veto ---------------------------------------
def test_year_word_cued_be_or_so_resolves_era():
    # "the year N BE" cannot be the verb collision -- the veto must not fire
    # just because something trails.
    r = _ts("the year 2560 BE or so")
    expected = resolve_era("buddhist", 2560)
    assert r is not None and r[1] == "or so"
    assert (r[0].start.year, r[0].start.month, r[0].start.day) == \
        (expected.year, expected.month, expected.day)


def test_year_word_cued_be_comma_or_so_resolves_era():
    r = _ts("the year 2560 BE, or so")
    expected = resolve_era("buddhist", 2560)
    assert r is not None
    assert r[0].start.year == expected.year


def test_year_word_cued_be_roughly_resolves_era():
    r = _ts("the year 2560 BE roughly")
    expected = resolve_era("buddhist", 2560)
    assert r is not None
    assert r[0].start.year == expected.year


def test_bare_be_trailing_declines_to_clean_none():
    # no year-word cue: the veto fires, and the number must NOT then bind as
    # a confident-but-543-years-wrong plain year with "BE" stranded.
    assert _ts("2560 BE or so") is None
    assert _ts("2560 BE, or so") is None
    assert _ts("2560 BE roughly") is None


# -- negative controls: unrelated behavior stays byte-identical ------------
def test_year_word_cued_be_alone_unchanged():
    r = _ts("the year 2560 BE")
    expected = resolve_era("buddhist", 2560)
    assert r is not None and r[1] == ""
    assert r[0].start.year == expected.year


def test_verb_collision_still_declines_era():
    # "2020 be ready": lower-case "be" is the ordinary verb, not the
    # abbreviation -- still declines the era and binds the plain year.
    r = _ts("2020 be ready")
    assert r is not None and r[1] == "be ready"
    assert r[0].start == AstroDate(2020, 1, 1)


def test_year_word_cued_ah_or_so_resolves_era():
    # other eras were already fine; must stay fine.
    r = _ts("the year 1447 AH or so")
    expected = resolve_era("hijri", 1447)
    assert r is not None and r[1] == "or so"
    assert (r[0].start.year, r[0].start.month, r[0].start.day) == \
        (expected.year, expected.month, expected.day)


def test_year_word_cued_ah_alone_unchanged():
    r = _ts("the year 1447 AH")
    expected = resolve_era("hijri", 1447)
    assert r is not None and r[1] == ""
    assert r[0].start.year == expected.year


# -- defect 2: two-digit-year pivot in new_year_ref -------------------------
def test_new_year_two_digit_below_32_pivots():
    anchor = datetime(2020, 1, 1)
    r = extract_timespan("new year 27", "en", anchor)
    assert r is not None and r[1] == ""
    assert r[0].start == AstroDate(2027, 1, 1)
    assert r[0].end == AstroDate(2027, 1, 2)


def test_new_year_two_digit_at_or_above_32_still_pivots():
    # negative control: this already worked, must stay unchanged.
    anchor = datetime(2020, 1, 1)
    r = extract_timespan("new year 99", "en", anchor)
    assert r is not None and r[1] == ""
    assert r[0].start == AstroDate(1999, 1, 1)


def test_new_year_four_digit_year_still_dayweide():
    # negative control: explicit 4-digit year already worked.
    anchor = datetime(2020, 1, 1)
    r = extract_timespan("new year 2027", "en", anchor)
    assert r is not None and r[1] == ""
    assert r[0].start == AstroDate(2027, 1, 1)
    assert r[0].end == AstroDate(2027, 1, 2)


# -- defect 3: definite-article veto must not discard a bound year ---------
def test_the_new_year_with_explicit_year_binds_day_wide():
    r = extract_timespan("the new year 2027", "en", _NY_ANCHOR)
    assert r is not None
    assert r[0].start == AstroDate(2027, 1, 1)
    assert r[0].end == AstroDate(2027, 1, 2)


def test_new_years_day_with_explicit_year_unchanged():
    # negative control: already correct.
    r = extract_timespan("new year's day 2027", "en", _NY_ANCHOR)
    assert r is not None
    assert r[0].start == AstroDate(2027, 1, 1)
    assert r[0].end == AstroDate(2027, 1, 2)


def test_bare_the_new_year_stays_ambiguous_none():
    # bare "the new year" (no year number) must be UNCHANGED from dev: the
    # ambiguous "coming year" period, not the holiday -- still None.
    assert extract_timespan("the new year", "en", _NY_ANCHOR) is None
    assert extract_timespan("in the new year", "en", _NY_ANCHOR) is None


def test_hebrew_new_year_with_the_still_day_wide():
    # negative control: "the hebrew new year 5786" already correct despite
    # the leading "the" (separate construction, no such veto).
    r = extract_timespan("the hebrew new year 5786", "en", _NY_ANCHOR)
    assert r is not None
    assert r[0].start.month == 9        # Rosh Hashanah, Tishrei 1
