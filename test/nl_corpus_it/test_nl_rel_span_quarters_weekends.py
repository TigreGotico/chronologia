"""it: "the next/last <N> quarters/weekends" -- Romance postposed siblings.

See the es sibling test for the full defect writeup: PR #632's postposed
"NUM REL_MARKER UNIT" override for the generic ``rel_span`` never reached the
``rel_span_quarter`` / ``rel_span_weekend`` siblings added by PR #635, so
"i 3 prossimi trimestri" / "i 3 prossimi weekend" silently dropped the count.
Fixed by adding the same postposed order (with a leading optional article,
consumed for an empty remainder) to those two constructions.

Anchor: Saturday 2024-06-15 12:00, matching ``test_nl_rel_span.py``. Golds
are computed by independent calendar arithmetic, not read back from the
parser.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

A = datetime(2024, 6, 15, 12, 0)


def _r(text):
    return extract_timespan(text, "it", A)


def _span(text):
    r = _r(text)
    return None if r is None else (r.span.start, r.span.end)


@pytest.mark.parametrize("text,s,e", [
    ("i 3 prossimi trimestri", AstroDate(2024, 7, 1), AstroDate(2025, 4, 1)),
    ("i 2 ultimi trimestri", AstroDate(2023, 10, 1), AstroDate(2024, 4, 1)),
])
def test_rel_span_quarter_it_postposed(text, s, e):
    assert _span(text) == (s, e), text


@pytest.mark.parametrize("text,s,e", [
    ("i 3 prossimi weekend", AstroDate(2024, 6, 15), AstroDate(2024, 7, 1)),
    ("i 2 ultimi weekend", AstroDate(2024, 6, 1), AstroDate(2024, 6, 10)),
])
def test_rel_span_weekend_it_postposed(text, s, e):
    assert _span(text) == (s, e), text


def test_rel_span_quarter_weekend_it_postposed_empty_remainder():
    for text in ("i 3 prossimi trimestri", "i 3 prossimi weekend"):
        r = _r(text)
        assert r.remainder == "", (text, r.remainder)


@pytest.mark.parametrize("text,s,e", [
    ("prossimi 3 trimestri", AstroDate(2024, 7, 1), AstroDate(2025, 4, 1)),
    ("prossimi 3 weekend", AstroDate(2024, 6, 15), AstroDate(2024, 7, 1)),
])
def test_rel_span_quarter_weekend_it_marker_first(text, s, e):
    assert _span(text) == (s, e), text


@pytest.mark.parametrize("text,s,e", [
    ("il prossimo trimestre", AstroDate(2024, 7, 1), AstroDate(2024, 10, 1)),
    ("l'ultimo trimestre", AstroDate(2024, 1, 1), AstroDate(2024, 4, 1)),
])
def test_singular_quarter_it_unchanged(text, s, e):
    assert _span(text) == (s, e), text
