"""ca: "the next/last <N> <units>" rolling span + plural relative markers.

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
    r = extract_timespan(text, "ca", A)
    return None if r is None else (r.span.start, r.span.end)


@pytest.mark.parametrize("text,s,e", [
    ("les pròximes 3 setmanes", AstroDate(2024, 6, 15), AstroDate(2024, 7, 6)),
    ("els últims 2 mesos", AstroDate(2024, 4, 15), AstroDate(2024, 6, 15)),
])
def test_rel_span_ca(text, s, e):
    assert _span(text) == (s, e), text


# Article-NUM-marker order ("les 3 properes/pròximes setmanes"), same
# mechanism as fr's postposed marker (R71 fix/r71-fr-rel-span), unioned onto
# the base marker-first order.  "properes" (proper/propera/propers/properes)
# is added to marker_next.voc alongside the existing pròxim/pròxima family --
# both are attested Catalan synonyms for "next".
@pytest.mark.parametrize("text,s,e", [
    ("les 3 properes setmanes", AstroDate(2024, 6, 15), AstroDate(2024, 7, 6)),
    ("les 3 pròximes setmanes", AstroDate(2024, 6, 15), AstroDate(2024, 7, 6)),
    ("els 2 últims mesos", AstroDate(2024, 4, 15), AstroDate(2024, 6, 15)),
])
def test_rel_span_ca_article_num_marker_order(text, s, e):
    assert _span(text) == (s, e), text


@pytest.mark.parametrize("text,s,e", [
    ("la pròxima setmana", AstroDate(2024, 6, 17), AstroDate(2024, 6, 24)),
    ("el mes passat", AstroDate(2024, 5, 1), AstroDate(2024, 6, 1)),
])
def test_single_unit_rel_period_ca(text, s, e):
    assert _span(text) == (s, e), text
