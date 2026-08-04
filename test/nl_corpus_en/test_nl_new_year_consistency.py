"""Bare "new year" resolves consistently across the public APIs.

The whole-utterance fast path resolved a lone "new year" to New Year's Day,
but ``extract_candidates("new year")`` returned 0 and "new year party" failed
to compose -- the two public edges disagreed and phrase composition broke.
Wiring "new year" as a proper construction (``new_year_ref``, keeping "new"
and "year" as SEPARATE tokens so it never shadows the ``hebrew_new_year``
construction) makes ``extract_timespan``, ``extract_candidates`` and phrase
composition all agree on New Year's Day (Jan 1).

The DEFINITE-article form ("the new year", "in the new year") is the ambiguous
"coming year" period, NOT the holiday, and must stay unresolved.

Reference: New Year's Day is Jan 1 by definition; no parser output is pinned.
"""
from datetime import datetime

from chronologia import extract_candidates, extract_timespan

from ._corpus import AstroDate, ANCHOR, parse

# guard anchor from the task brief: 1 March 2026, noon.
_A = datetime(2026, 3, 1, 12, 0)


def _ts(text, anchor=_A):
    return extract_timespan(text, "en", anchor)


def _nc(text, anchor=_A):
    return len(extract_candidates(text, "en", anchor))


def test_new_year_apis_agree():
    # extract_timespan resolves it AND extract_candidates surfaces >= 1 reading
    r = _ts("new year")
    assert r is not None
    assert r[0].start == AstroDate(2027, 1, 1)          # prefer-future Jan 1
    assert _nc("new year") >= 1


def test_new_years_variant_agrees():
    r = _ts("new years")
    assert r is not None and r[0].start == AstroDate(2027, 1, 1)
    assert _nc("new years") >= 1


def test_new_year_party_composes_with_remainder():
    # phrase composition: "new year" binds Jan 1, "party" strands as remainder
    r = _ts("new year party")
    assert r is not None
    assert r[0].start == AstroDate(2027, 1, 1)
    assert r[1] == "party"


# -- guards: the definite-article period form must NOT become the holiday --
def test_definite_article_new_year_stays_unresolved():
    assert _ts("the new year") is None
    assert _nc("the new year") == 0


def test_in_the_new_year_stays_unresolved():
    assert _ts("in the new year") is None
    assert _nc("in the new year") == 0


def test_definite_article_new_year_party_stays_unresolved():
    assert _ts("the new year party") is None


# -- guards: the year-period readings are untouched ------------------------
def test_next_last_this_year_unchanged():
    assert _ts("next year")[0].start == AstroDate(2027, 1, 1)
    assert _ts("next year")[0].end == AstroDate(2028, 1, 1)
    assert _ts("last year")[0].start == AstroDate(2025, 1, 1)
    assert _ts("this year")[0].start == AstroDate(2026, 1, 1)


def test_hebrew_new_year_still_resolves():
    # the separate-token construction must not have shadowed hebrew_new_year
    r = _ts("the hebrew new year 5786")
    assert r is not None
    assert r[0].start.month == 9        # Rosh Hashanah, Tishrei 1


def test_happy_new_year_resolves_the_holiday():
    # noted acceptable behavior: "happy new year" -> Jan 1, "happy" strands
    r = _ts("happy new year")
    assert r is not None and r[0].start == AstroDate(2027, 1, 1)
    assert r[1] == "happy"


# -- an explicit year names THAT New Year's Day, not the prefer-future one --
def test_new_year_with_explicit_year():
    # used to silently drop the year to the remainder and return the
    # prefer-future Jan 1; now binds the named year (day-wide New Year's Day).
    for text, y in [("new year 2030", 2030), ("new year 2027", 2027),
                    ("new year in 2027", 2027), ("new year of 2030", 2030)]:
        r = _ts(text)
        assert r is not None and r[1] == "", text
        assert r[0].start == AstroDate(y, 1, 1)
        assert r[0].end == AstroDate(y, 1, 2)          # day-wide, like the bare form
        assert _nc(text) >= 1                           # candidates agree


def test_new_year_apostrophe_year_pivots():
    r = _ts("new year '29")
    assert r is not None and r[0].start == AstroDate(2029, 1, 1)
