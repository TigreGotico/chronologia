"""What this locale deliberately does not read, pinned so it stays honest.

Every phrase below names a construction whose Armenian surfaces could not be
attested to a worked example, so no vocabulary ships for it.  The contract is
refusal: the extractor returns nothing, or leaves the unread words in the
remainder, rather than guessing.  Each pin turns into a failing test the day
someone adds the vocabulary, which is exactly when the behaviour should be
revisited.
"""
import pytest

from ._corpus import parse


@pytest.mark.parametrize("text", [
    "երկուշաբթիից ի վեր", "երկուշաբթիից սկսած", "երեկվանից",
])
def test_no_since_marker(text):
    """A dedicated "since <a point in time>" periphrasis (``-ից ի վեր``,
    ``-ից սկսած``) has no fetched worked example, so no open-ended backward
    range is opened.  The bare ablative that this locale does read is the
    forward DURATION offset, a different construction."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "երեք օր շարունակ", "երեք օրվա ընթացքում", "այս շաբաթվա ընթացքում",
])
def test_no_duration_for(text):
    """The "for <duration>" marker has no citation, so a duration phrase must
    not be read as one."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "հունիսի և հուլիսի միջև", "երկու օրվա և երեք օրվա միջև",
])
def test_no_between_and_range(text):
    """միջև is a postposition governing the genitive on BOTH conjuncts -- a
    shape this locale's range grammar has no order for -- so the range is
    refused and the postposition left unread rather than a half-range being
    invented from the first conjunct."""
    r = parse(text)
    assert r is None or "միջև" in r[1]


@pytest.mark.parametrize("text", [
    "ուտելուց առաջ", "երկուշաբթիից առաջ",
])
def test_no_ablative_before_event(text):
    """առաջ takes two patterns: a bare duration ("երեք օր առաջ", which this
    locale reads) and an ABLATIVE-marked event or reference point ("before
    eating"), which is a different construction.  Only the duration one
    ships; the event one is refused rather than read as a duration."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "հունիսին", "հունիս ամսում", "երեք օրում",
])
def test_no_locative_in_period(text):
    """The locative ``-ում`` is reported as a temporal modifier but with no
    temporal worked example, and literary usage drops the definite article
    inside it, so no locative surface is claimed for any unit or month."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", ["հանգստյան օրեր", "հանգստյան օր"])
def test_no_weekend_noun(text):
    """No weekend surface was attested, so the two-day span has no name here."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "ամեն օր առաջ",
])
def test_every_is_a_recurrence_not_a_span(text):
    """ամեն quantifies a repeating period; it is read by the recurrence edge,
    not the span edge, and must not silently disappear from a span parse."""
    r = parse(text)
    assert r is None or "ամեն" in r[1]
