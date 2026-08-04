"""Spanish "las próximas/últimas <N> <unidades>" -- the rolling N-unit span.

Spanish is marker-first ("próximas 3 semanas"), so the base rel_span order
matches; it only needed the PLURAL marker forms (próximas/próximos,
últimas/últimos, pasados/pasadas) in the vocab, which agree with a plural unit.
The single-unit rel_period reading ("la próxima semana", "el mes pasado") is
unchanged.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

A = datetime(2024, 6, 15, 12, 0)


def _span(text):
    r = extract_timespan(text, "es", A)
    return None if r is None else (r.span.start, r.span.end)


@pytest.mark.parametrize("text,s,e", [
    ("las próximas 3 semanas", AstroDate(2024, 6, 15), AstroDate(2024, 7, 6)),
    ("los próximos 3 meses", AstroDate(2024, 6, 15), AstroDate(2024, 9, 15)),
    ("los últimos 2 meses", AstroDate(2024, 4, 15), AstroDate(2024, 6, 15)),
    ("las últimas 2 semanas", AstroDate(2024, 6, 1), AstroDate(2024, 6, 15)),
])
def test_rel_span_es(text, s, e):
    assert _span(text) == (s, e), text


@pytest.mark.parametrize("text,s,e", [
    ("la próxima semana", AstroDate(2024, 6, 17), AstroDate(2024, 6, 24)),
    ("la semana pasada", AstroDate(2024, 6, 3), AstroDate(2024, 6, 10)),
    ("el mes pasado", AstroDate(2024, 5, 1), AstroDate(2024, 6, 1)),
    ("el próximo año", AstroDate(2025, 1, 1), AstroDate(2026, 1, 1)),
])
def test_single_unit_rel_period_es_unchanged(text, s, e):
    assert _span(text) == (s, e), text
