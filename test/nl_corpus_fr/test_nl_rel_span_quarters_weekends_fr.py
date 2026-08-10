"""French "les <N> prochains/derniers trimestres/week-ends" -- the calendar-
quarter and weekend siblings of ``rel_span`` (R86).

PR #632 gave French its own ``rel_span`` order ("NUM REL_MARKER UNIT") because
French postposes the relative marker between the count and the unit ("les 3
prochaines semaines", not "les prochaines 3 semaines"). PR #635 later added
``rel_span_quarter``/``rel_span_weekend`` as siblings of ``rel_span`` in
``base_grammar.py``, but shipped ONLY the marker-first default order
("REL_MARKER NUM quarter_word"/"REL_MARKER NUM WEEKEND"). French never
overrode that pair, so postposed French text silently mis-parsed:

* "les 2 prochains trimestres" -- the leading "les 2" could not bind the
  marker-first order at all, so NOTHING matched through the quarter path;
  the sentence fell through to some other (wrong) reading, stranding "les 2"
  and reporting only a partial/incorrect span.
* "les 3 prochains week-end" -- same failure mode for the weekend sibling.

Fixed by adding French ``article? NUM REL_MARKER quarter_word`` /
``article? NUM REL_MARKER WEEKEND`` order overrides (unioned with the base
marker-first order, mirroring ``rel_span``), plus the leading ``article?``
these two get that ``rel_span`` itself does not -- so "les" is consumed
instead of stranded. Also adds the missing French plural surface
"week-ends" (Larousse) to the weekend vocab -- previously only the
invariant "weekend"/"week-end" were recognized.

Anchor: Monday 2026-08-10 (Q3 2026). Golds are computed by independent
calendar arithmetic (matching the documented algorithm in
``resolver.py``'s ``_resolve_rel_span_quarter``/``_resolve_rel_span_weekend``
docstrings), not read back from the parser.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

A = datetime(2026, 8, 10, 12, 0)


def _result(text):
    return extract_timespan(text, "fr", A)


def _span(text):
    r = _result(text)
    return None if r is None else (r.span.start, r.span.end)


@pytest.mark.parametrize("text,s,e", [
    # DEFECT: used to strand "les 2" and return a wrong/partial reading.
    ("les 2 prochains trimestres", AstroDate(2026, 10, 1), AstroDate(2027, 4, 1)),
    ("les 2 derniers trimestres", AstroDate(2026, 1, 1), AstroDate(2026, 7, 1)),
])
def test_rel_span_quarter_fr(text, s, e):
    assert _span(text) == (s, e), text


@pytest.mark.parametrize("text", [
    "les 2 prochains trimestres",
    "les 2 derniers trimestres",
])
def test_rel_span_quarter_fr_empty_remainder(text):
    r = _result(text)
    assert r is not None, text
    assert r.remainder == "", (text, r.remainder)


@pytest.mark.parametrize("text,s,e", [
    # DEFECT: used to strand "les 3" and drop the count entirely.
    ("les 3 prochains week-ends", AstroDate(2026, 8, 15), AstroDate(2026, 8, 31)),
    ("les 2 derniers week-ends", AstroDate(2026, 8, 1), AstroDate(2026, 8, 10)),
])
def test_rel_span_weekend_fr(text, s, e):
    assert _span(text) == (s, e), text


@pytest.mark.parametrize("text", [
    "les 3 prochains week-ends",
    "les 2 derniers week-ends",
])
def test_rel_span_weekend_fr_empty_remainder(text):
    r = _result(text)
    assert r is not None, text
    assert r.remainder == "", (text, r.remainder)


def test_rel_span_weekend_fr_singular_plural_surface():
    # the singular "week-end" surface (already shipped) still binds through
    # the same new order.
    r = _result("les 3 prochains week-end")
    assert r is not None
    assert (r.span.start, r.span.end) == (AstroDate(2026, 8, 15), AstroDate(2026, 8, 31))


@pytest.mark.parametrize("text,s,e", [
    # controls: the pre-existing rel_span UNIT family (R67/#632) is untouched.
    ("les 2 prochaines semaines", AstroDate(2026, 8, 10), AstroDate(2026, 8, 24)),
])
def test_rel_span_unit_fr_unchanged(text, s, e):
    assert _span(text) == (s, e), text


def test_rel_span_quarters_weekends_en_unaffected():
    # French-only fix -- English marker-first siblings are untouched.
    r = extract_timespan("the next 2 quarters", "en", A)
    assert r is not None
    assert (r.span.start, r.span.end) == (AstroDate(2026, 10, 1), AstroDate(2027, 4, 1))
    r2 = extract_timespan("the next 2 weekends", "en", A)
    assert r2 is not None
    assert (r2.span.start, r2.span.end) == (AstroDate(2026, 8, 15), AstroDate(2026, 8, 24))
