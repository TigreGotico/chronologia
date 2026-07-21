"""Matcher stage: slot binding, both marker positions, precedence and
longest-span overlap resolution."""
from engine_helpers import zz_engine

from chronologia.extract.matcher import Candidate, ConstructionMatcher
from chronologia.extract.model import Match


def _match(text):
    eng = zz_engine()
    return eng.matcher.match(eng.tokenize(text))


def test_relative_offset_suffix_marker():
    (m,) = _match("3 zdays zhence")
    assert m.construction == "relative_offset" and m.span == (0, 3)
    assert m.slots["NUM"].value == 3 and m.slots["MARKER"].text == "zhence"


def test_relative_offset_prefix_marker():
    (m,) = _match("zago 2 zweeks")
    assert m.construction == "relative_offset" and m.span == (0, 3)
    assert m.slots["MARKER"].text == "zago"


def test_named_day():
    (m,) = _match("zmorrow")
    assert m.construction == "named_day" and m.slots["DAY_WORD"].text == "zmorrow"


def test_weekday_ref():
    (m,) = _match("znext zfri")
    assert m.construction == "weekday_ref"
    assert m.slots["REL_MARKER"].text == "znext"


def test_calendar_mdy_full():
    (m,) = _match("zjun 5 2027")
    assert m.construction == "calendar_date" and m.span == (0, 3)
    assert m.slots["DAY"].value == 5 and m.slots["YEAR"].value == 2027


def test_calendar_month_bare_year_binds_year_not_day():
    (m,) = _match("zjun 2027")
    assert "YEAR" in m.slots and "DAY" not in m.slots
    assert m.slots["YEAR"].value == 2027


def test_calendar_dmy_with_connector():
    (m,) = _match("5 zof zjun 2027")
    assert m.construction == "calendar_date" and m.span == (0, 4)
    assert m.slots["DAY"].value == 5 and m.slots["YEAR"].value == 2027


def test_longest_span_wins_single_match():
    # "MONTH DAY? YEAR?" also matches the shorter MONTH-only and MONTH+DAY
    # spans; only the longest survives selection.
    matches = _match("zjun 5 2027")
    assert len(matches) == 1 and matches[0].span == (0, 3)


def test_empty_and_garbage_never_raise():
    assert _match("") == ()
    assert _match("zzz qux 999 ...") == ()


def _cand(name, span, prec):
    return Candidate(Match(name, span, {}), prec)


def test_select_longer_span_wins():
    longer = _cand("calendar_date", (0, 3), 4)
    shorter = _cand("relative_offset", (1, 3), 7)
    chosen = ConstructionMatcher._select([shorter, longer])
    assert [c.match.construction for c in chosen] == ["calendar_date"]


def test_select_precedence_breaks_equal_length():
    era = _cand("era_date", (0, 2), 0)
    cal = _cand("calendar_date", (0, 2), 4)
    chosen = ConstructionMatcher._select([cal, era])
    assert [c.match.construction for c in chosen] == ["era_date"]


def test_select_keeps_disjoint_matches():
    a = _cand("named_day", (0, 1), 8)
    b = _cand("named_day", (2, 3), 8)
    chosen = ConstructionMatcher._select([a, b])
    assert len(chosen) == 2
