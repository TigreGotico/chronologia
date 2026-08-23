"""The Esperanto spoken clock, which counts FORWARD from the hour it names --
the ENGLISH past-the-hour shape, not the Baltic/Germanic toward-the-hour one.

"la sesa kaj duono" (the sixth [hour] and a half) is 6:30, never 5:30; "la
sesa kaj kvarono" is 6:15.  The alternate fraction-first "post" connector
names the same forward direction ("duono post la sepa" = 7:30).  Only
"antaŭ" (before) counts backward, toward the coming hour ("kvarono antaŭ la
sepa" = a quarter short of seven, 6:45).  Two independent sources agree:
esperanto.lingolia.com "Time"; corroborating aggregate search on
languagedrops.com/omniglot.com "Telling the time in Esperanto".

Every "past" reading is pinned ADVERSARIALLY: the toward-hour reading a
reader familiar with lt/is might expect is asserted ABSENT, not merely the
right hour asserted present.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, nomatch, start


def _next_time(h, mi):
    cand = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    return cand


@pytest.mark.parametrize("text,h,mi", [
    ("la sesa kaj duono", 6, 30),
    ("la sesa kaj kvarono", 6, 15),
    ("la naŭa kaj duono", 9, 30),
    ("je la sesa kaj duono", 6, 30),
])
def test_half_and_quarter_name_the_stated_hour(text, h, mi):
    """"kaj" is the FORWARD connector: the named hour is the one just
    started, exactly as English "six thirty" names six, not seven."""
    got = start(text)
    assert (got.hour, got.minute) == (h, mi)


@pytest.mark.parametrize("text,wrong_hour,wrong_minute", [
    ("la sesa kaj duono", 5, 30),
    ("la sesa kaj kvarono", 5, 15),
])
def test_half_past_never_reads_toward_the_hour(text, wrong_hour, wrong_minute):
    """Adversarial pin: the Baltic/Germanic toward-hour reading ("la sesa kaj
    duono" as 5:30, one hour EARLIER) must never occur."""
    got = start(text)
    assert (got.hour, got.minute) != (wrong_hour, wrong_minute)


@pytest.mark.parametrize("text,h,mi", [
    ("duono post la sepa", 7, 30),
    ("kvarono post la sepa", 7, 15),
])
def test_post_connector_is_the_same_forward_direction(text, h, mi):
    got = start(text)
    assert (got.hour, got.minute) == (h, mi)


@pytest.mark.parametrize("text,h,mi", [
    ("kvarono antaŭ la sepa", 6, 45),
])
def test_antaŭ_counts_backward_toward_the_named_hour(text, h, mi):
    """"antaŭ" is the ASYMMETRIC member of the set: it counts back from the
    hour it names, unlike "kaj"/"post"."""
    got = start(text)
    assert (got.hour, got.minute) == (h, mi)


@pytest.mark.parametrize("text,wrong_hour", [
    ("kvarono antaŭ la sepa", 7),
])
def test_antaŭ_is_not_the_stated_hour_plus_the_fraction(text, wrong_hour):
    assert start(text).hour != wrong_hour


@pytest.mark.parametrize("text,h", [
    ("la sesa", 6), ("je la sesa", 6), ("la sesa horo", 6),
])
def test_bare_oclock(text, h):
    assert start(text).hour == h
    assert start(text).minute == 0


@pytest.mark.parametrize("text,h", [
    ("noktomezo", 0), ("tagmezo", 12),
])
def test_clock_landmarks(text, h):
    assert start(text).hour == h


@pytest.mark.parametrize("text", [
    "kaj duono",          # a bare fraction with no hour at all
    "duono",              # a bare fraction, standalone
    "dek du",              # a bare number, no clock frame around it
    "je dek du",           # "at" with no article and no clock frame
])
def test_incomplete_clock_is_not_a_time(text):
    nomatch(text)
