"""pt: "the next/last <N> <units>" rolling span + plural relative markers.

Marker-first Romance, so the rel_span base order matched; it needed the PLURAL
marker forms (agreeing with a plural unit) added to the vocab.  Single-unit
rel_period is unchanged.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

A = datetime(2024, 6, 15, 12, 0)


def _span(text):
    r = extract_timespan(text, "pt", A)
    return None if r is None else (r.span.start, r.span.end)


@pytest.mark.parametrize("text,s,e", [
    ("as próximas 3 semanas", AstroDate(2024, 6, 15), AstroDate(2024, 7, 6)),
    ("os últimos 2 meses", AstroDate(2024, 4, 15), AstroDate(2024, 6, 15)),
])
def test_rel_span_pt(text, s, e):
    assert _span(text) == (s, e), text


@pytest.mark.parametrize("text,s,e", [
    ("a próxima semana", AstroDate(2024, 6, 17), AstroDate(2024, 6, 24)),
    ("o mês passado", AstroDate(2024, 5, 1), AstroDate(2024, 6, 1)),
])
def test_single_unit_rel_period_pt(text, s, e):
    assert _span(text) == (s, e), text
