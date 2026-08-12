"""R140 -- Greek 'πριν από' (formal two-word "ago") / 'μετά από' (formal
two-word "in/after") compound direction markers.

Standard written Greek prefers the "από" preposition after πριν/μετά at
least as often as the bare form ("πριν από 3 ημέρες" == "πριν 3 ημέρες"),
yet the compound used to refuse entirely because the ``MARKER`` slot of the
``relative_offset`` construction binds a single token against
``spec.directions`` (built from ``marker_past.voc``/``marker_future.voc``)
-- "πριν από" was never one of those surfaces, so the tokenizer's two
separate tokens never bound.  Oracles are independent date arithmetic,
never the engine's own output.
"""
import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, nomatch, start_end

UNIT = {
    "μέρα": relativedelta(days=1), "μέρες": relativedelta(days=1),
    "ημέρες": relativedelta(days=1),
    "εβδομάδες": relativedelta(weeks=1),
    "μήνες": relativedelta(months=1),
    "χρόνια": relativedelta(years=1),
    "ώρες": relativedelta(hours=1),
}


def past(n, unit):
    d = UNIT[unit]
    return ad(ANCHOR - n * d), ad(ANCHOR - (n - 1) * d)


def future(n, unit):
    d = UNIT[unit]
    return ad(ANCHOR + n * d), ad(ANCHOR + (n + 1) * d)


# -- ago: "πριν από N UNIT" (the formal/standard compound) -----------------

@pytest.mark.parametrize("text,n,unit", [
    ("πριν από 3 ημέρες", 3, "ημέρες"),
    ("πριν από τρεις μέρες", 3, "μέρες"),
    ("πριν από 2 εβδομάδες", 2, "εβδομάδες"),
    ("πριν από 5 μήνες", 5, "μήνες"),
    ("πριν από 10 χρόνια", 10, "χρόνια"),
    ("πριν από 3 ώρες", 3, "ώρες"),
])
def test_prin_apo_ago(text, n, unit):
    assert start_end(text) == past(n, unit)


# -- in/after: "μετά από N UNIT" (the formal/standard compound) -----------

@pytest.mark.parametrize("text,n,unit", [
    ("μετά από 3 ημέρες", 3, "ημέρες"),
    ("μετά από 2 εβδομάδες", 2, "εβδομάδες"),
    ("μετά από 5 μήνες", 5, "μήνες"),
    ("μετά από 10 χρόνια", 10, "χρόνια"),
])
def test_meta_apo_future(text, n, unit):
    assert start_end(text) == future(n, unit)


# -- bare-form controls: unchanged by the compound addition ---------------

@pytest.mark.parametrize("text,n,unit", [
    ("πριν 3 ημέρες", 3, "ημέρες"),
    ("πριν 2 εβδομάδες", 2, "εβδομάδες"),
    ("3 μέρες πριν", 3, "μέρες"),
])
def test_bare_prin_still_ago(text, n, unit):
    assert start_end(text) == past(n, unit)


@pytest.mark.parametrize("text,n,unit", [
    ("μετά 3 ημέρες", 3, "ημέρες"),
    ("σε 3 μέρες", 3, "μέρες"),
])
def test_bare_meta_still_future(text, n, unit):
    assert start_end(text) == future(n, unit)


# -- non-temporal 'από' control: must NOT bind as a direction marker ------

@pytest.mark.parametrize("text", [
    "είμαι από την Αθήνα",
    "ήρθα από το σχολείο",
])
def test_non_temporal_apo_does_not_bind(text):
    nomatch(text)
