"""Bare durations, where a trailing *da* names a fraction of the unit.

"awa daya da rabi" (an hour and a half) is attested on ha.wikipedia.org.  The
fraction trails its unit exactly as it does in Swahili's "saa moja na nusu",
and the two locales share the same quantifier machinery, so the phrase reads
as ninety minutes rather than being truncated to the bare hour with the
fraction left stranded.
"""
from datetime import timedelta

from chronologia import extract_duration

from ._corpus import ANCHOR  # noqa: F401


def dur(text):
    return extract_duration(text, "ha")


def test_the_trailing_fraction_attaches():
    """Truncating to "awa daya" and leaving "da rabi" in the remainder would
    be a wrong length with the missing part visible beside it."""
    r = dur("awa daya da rabi")
    assert r is not None, "'awa daya da rabi' read as no duration at all"
    assert r.duration == timedelta(hours=1, minutes=30)
    assert r.remainder == ""


def test_the_trailing_fraction_attaches_to_a_day_count():
    r = dur("kwanaki uku da rabi")
    assert r is not None, "'kwanaki uku da rabi' read as no duration at all"
    assert r.duration == timedelta(days=3, hours=12)
    assert r.remainder == ""
