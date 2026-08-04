"""French "les <N> prochaines/dernières <unités>" -- the rolling N-unit span.

French POSTPOSES the relative marker between the count and the unit ("les 3
prochaines semaines", not "les prochaines 3 semaines"), so it carries its own
rel_span order "NUM REL_MARKER UNIT" (unioned with the base marker-first order),
plus the PLURAL marker forms (prochains/prochaines, derniers/dernières).  The
single-unit rel_period reading ("la semaine prochaine", "le mois dernier") is
unchanged.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

A = datetime(2024, 6, 15, 12, 0)


def _span(text):
    r = extract_timespan(text, "fr", A)
    return None if r is None else (r.span.start, r.span.end)


@pytest.mark.parametrize("text,s,e", [
    ("les 3 prochaines semaines", AstroDate(2024, 6, 15), AstroDate(2024, 7, 6)),
    ("les 3 prochains mois", AstroDate(2024, 6, 15), AstroDate(2024, 9, 15)),
    ("les 2 derniers mois", AstroDate(2024, 4, 15), AstroDate(2024, 6, 15)),
    ("les 2 dernières semaines", AstroDate(2024, 6, 1), AstroDate(2024, 6, 15)),
])
def test_rel_span_fr(text, s, e):
    assert _span(text) == (s, e), text


@pytest.mark.parametrize("text,s,e", [
    ("la semaine prochaine", AstroDate(2024, 6, 17), AstroDate(2024, 6, 24)),
    ("la semaine dernière", AstroDate(2024, 6, 3), AstroDate(2024, 6, 10)),
    ("le mois dernier", AstroDate(2024, 5, 1), AstroDate(2024, 6, 1)),
])
def test_single_unit_rel_period_fr_unchanged(text, s, e):
    assert _span(text) == (s, e), text
