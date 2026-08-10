"""es: "the next/last <N> quarters/weekends" -- Romance postposed siblings.

PR #632 gave es a postposed "NUM REL_MARKER UNIT" order for the generic
``rel_span`` construction, but its calendar-aligned siblings added by PR #635
(``rel_span_quarter``, ``rel_span_weekend``) never got the same per-locale
override. "los 3 próximos trimestres" and "los 3 próximos fines de semana"
silently dropped the count: they matched the base marker-first order
("REL_MARKER NUM ...") only after the leading NUM was stripped as an
unrelated token, binding a single quarter/weekend and stranding "los 3" in
the remainder. This adds the postposed order (with a leading optional
article, so the article is consumed too -- empty remainder) mirroring the
generic rel_span fix.

Anchor: Saturday 2024-06-15 12:00, matching ``test_nl_rel_span.py``. Golds
are computed by independent calendar arithmetic (quarter boundaries /
Saturday-Sunday pairs), not read back from the parser.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

A = datetime(2024, 6, 15, 12, 0)


def _r(text):
    return extract_timespan(text, "es", A)


def _span(text):
    r = _r(text)
    return None if r is None else (r.span.start, r.span.end)


@pytest.mark.parametrize("text,s,e", [
    # DEFECT: used to drop the count and read as a single (wrong) quarter,
    # stranding "los 3" in the remainder.
    ("los 3 próximos trimestres", AstroDate(2024, 7, 1), AstroDate(2025, 4, 1)),
    ("los 2 últimos trimestres", AstroDate(2023, 10, 1), AstroDate(2024, 4, 1)),
])
def test_rel_span_quarter_es_postposed(text, s, e):
    assert _span(text) == (s, e), text


@pytest.mark.parametrize("text,s,e", [
    # DEFECT: used to drop the count and always return a single weekend.
    ("los 3 próximos fines de semana", AstroDate(2024, 6, 15), AstroDate(2024, 7, 1)),
    ("los 2 últimos fines de semana", AstroDate(2024, 6, 1), AstroDate(2024, 6, 10)),
])
def test_rel_span_weekend_es_postposed(text, s, e):
    assert _span(text) == (s, e), text


def test_rel_span_quarter_weekend_es_postposed_empty_remainder():
    for text in ("los 3 próximos trimestres", "los 3 próximos fines de semana"):
        r = _r(text)
        assert r.remainder == "", (text, r.remainder)


@pytest.mark.parametrize("text,s,e", [
    # marker-first controls -- already worked before this fix.
    ("próximos 3 trimestres", AstroDate(2024, 7, 1), AstroDate(2025, 4, 1)),
    ("próximos 3 fines de semana", AstroDate(2024, 6, 15), AstroDate(2024, 7, 1)),
])
def test_rel_span_quarter_weekend_es_marker_first(text, s, e):
    assert _span(text) == (s, e), text


@pytest.mark.parametrize("text,s,e", [
    # singular calendar-aligned readings stay untouched.
    ("el próximo trimestre", AstroDate(2024, 7, 1), AstroDate(2024, 10, 1)),
    ("el último trimestre", AstroDate(2024, 1, 1), AstroDate(2024, 4, 1)),
])
def test_singular_quarter_es_unchanged(text, s, e):
    assert _span(text) == (s, e), text
