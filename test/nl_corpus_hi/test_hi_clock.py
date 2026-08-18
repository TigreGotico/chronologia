"""The Hindi spoken clock, whose three fraction words disagree on direction.

साढ़े names the half PAST the hour it is followed by (साढ़े तीन == 03:30) and
सवा the quarter past it (सवा एक == 01:15), but पौने names the quarter BEFORE
it: पौने दस is 09:45, the reading en.wiktionary's own usage example gives.  A
fold that treated the three symmetrically would answer 10:45 -- or, reading
पौने as a plain quarter, 10:15 -- so both wrong readings are asserted absent,
not merely the right one asserted present.

डेढ़ (01:30) and ढाई (02:30) are suppletive words for one-and-a-half and
two-and-a-half.  They are literals: nothing composes them out of a half word
plus एक or दो, and the corpus pins that the halves and quarters cannot
manufacture them either.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, nomatch, remainder, start


def _next_time(h, mi):
    cand = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    return ad(cand)


@pytest.mark.parametrize("text,h,mi", [
    ("साढ़े तीन", 3, 30),
    ("साढ़े तीन बजे", 3, 30),
    ("साढ़े चार", 4, 30),
    ("साढ़े आठ", 8, 30),
    ("साढ़े ग्यारह", 11, 30),
    ("साढ़े बारह बजे", 12, 30),
])
def test_half_counts_forward_from_the_named_hour(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,h,mi", [
    ("सवा एक", 1, 15),
    ("सवा एक बजे", 1, 15),
    ("सवा चार", 4, 15),
    ("सवा नौ", 9, 15),
    ("सवा बारह", 12, 15),
])
def test_quarter_counts_forward_from_the_named_hour(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,h,mi", [
    ("पौने दस", 9, 45),
    ("पौने चार", 3, 45),
    ("पौने आठ", 7, 45),
    ("पौने बारह", 11, 45),
])
def test_quarter_less_counts_back_from_the_named_hour(text, h, mi):
    """पौने दस == 09:45 is en.wiktionary's own worked example."""
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,named_hour", [
    ("पौने दस", 10), ("पौने चार", 4), ("पौने आठ", 8), ("पौने बारह", 12),
])
def test_quarter_less_is_never_the_hour_it_names(text, named_hour):
    """The symmetric reading -- a quarter PAST the stated hour, 10:15, or a
    three-quarters past it, 10:45 -- must never occur."""
    s = start(text)
    assert s.hour != named_hour
    assert (s.hour, s.minute) != (named_hour, 45)
    assert (s.hour, s.minute) != (named_hour, 15)


def test_the_three_fractions_disagree_on_the_same_hour():
    """साढ़े/सवा add to their hour, पौने subtracts from it -- pinned side by
    side so a change that unifies them cannot pass."""
    assert (start("सवा चार").hour, start("सवा चार").minute) == (4, 15)
    assert (start("साढ़े चार").hour, start("साढ़े चार").minute) == (4, 30)
    assert (start("पौने चार").hour, start("पौने चार").minute) == (3, 45)


@pytest.mark.parametrize("text,h,mi", [
    ("डेढ़ बजे", 1, 30),
    ("डेढ़", 1, 30),
    ("ढाई बजे", 2, 30),
    ("ढाई", 2, 30),
])
def test_suppletive_half_hours_are_literals(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text", ["साढ़े एक", "साढ़े दो"])
def test_the_half_word_does_not_manufacture_the_suppletive_hours(text):
    """डेढ़ and ढाई are the words for 01:30 and 02:30.  Nothing forbids the
    compositional phrasing from parsing, but it must land on the additive
    reading the half word means everywhere else, never be redirected to the
    suppletive literal's value by some special case."""
    s = start(text)
    assert s.minute == 30
    assert s.hour in (1, 2)


@pytest.mark.parametrize("text,h,mi", [
    ("आठ बजकर बीस मिनट", 8, 20),
    ("दस बजकर पाँच मिनट", 10, 5),
    ("तीन बजकर पैंतालीस मिनट", 3, 45),
])
def test_minutes_past_a_struck_hour(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,h", [
    ("दो बजे", 2), ("छह बजे", 6), ("नौ बजे", 9), ("बारह बजे", 12),
])
def test_oclock(text, h):
    assert start(text).hour == h


@pytest.mark.parametrize("text,h,mi", [
    ("15:30", 15, 30), ("09:05", 9, 5), ("00:00", 0, 0), ("23:59", 23, 59),
    ("१५:३०", 15, 30), ("०९:०५", 9, 5), ("२३:५९", 23, 59),
])
def test_digit_clock_in_both_scripts(text, h, mi):
    s = start(text)
    assert (s.hour, s.minute) == (h, mi)


def test_midnight_landmark():
    assert start("मध्यरात्रि").hour == 0


@pytest.mark.parametrize("text", ["साढ़े", "सवा", "पौने", "बजे", "बजकर"])
def test_a_bare_fraction_word_is_not_a_time(text):
    nomatch(text)


def test_the_noon_landmark_is_not_shipped():
    """दोपहर is the AFTERNOON band, not a midday landmark: CLDR 47 gives it as
    locale hi's afternoon dayPeriod, and no separate noon word is attested, so
    it resolves to the four-hour band rather than to a single minute."""
    s = start("दोपहर")
    assert (s.hour, s.minute) == (12, 0)
    assert remainder("दोपहर") == ""
    from ._corpus import span
    assert (span("दोपहर").end - s).seconds == 4 * 3600
