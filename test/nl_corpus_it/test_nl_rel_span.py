"""it: "the next/last <N> <units>" rolling span + plural relative markers.

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
    r = extract_timespan(text, "it", A)
    return None if r is None else (r.span.start, r.span.end)


@pytest.mark.parametrize("text,s,e", [
    ("le prossime 3 settimane", AstroDate(2024, 6, 15), AstroDate(2024, 7, 6)),
    ("gli ultimi 2 mesi", AstroDate(2024, 4, 15), AstroDate(2024, 6, 15)),
])
def test_rel_span_it(text, s, e):
    assert _span(text) == (s, e), text


# Article-NUM-marker order ("le 3 prossime settimane"), same mechanism as
# fr's postposed marker (R71 fix/r71-fr-rel-span), unioned onto the base
# marker-first order.  "mesi" is masculine and starts with a plain consonant
# ('m'), so its plural article is "i" (not "gli" -- "gli" is reserved for
# vowel-initial or s+consonant/z/gn/pn/ps/x/y words, as in "gli ultimi mesi"
# is likewise WRONG and "gli anni" above is correct only because "anni"
# starts with a vowel); "i 2 ultimi mesi" is the grammatically correct
# control for this order.
@pytest.mark.parametrize("text,s,e", [
    ("le 3 prossime settimane", AstroDate(2024, 6, 15), AstroDate(2024, 7, 6)),
    ("i 2 ultimi mesi", AstroDate(2024, 4, 15), AstroDate(2024, 6, 15)),
])
def test_rel_span_it_article_num_marker_order(text, s, e):
    assert _span(text) == (s, e), text


@pytest.mark.parametrize("text,s,e", [
    ("la prossima settimana", AstroDate(2024, 6, 17), AstroDate(2024, 6, 24)),
    ("il mese scorso", AstroDate(2024, 5, 1), AstroDate(2024, 6, 1)),
])
def test_single_unit_rel_period_it(text, s, e):
    assert _span(text) == (s, e), text
