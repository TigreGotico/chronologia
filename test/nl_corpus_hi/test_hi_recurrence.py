# -*- coding: utf-8 -*-
"""Recurrence in hi: extract_recurrence -> RRULE.

हर opens the recurrence frame and leads its phrase; when the phrase names a
WEEKDAY the ordinary locative को may trail it ("हर सोमवार को"), exactly as it
trails a single date ("सोमवार को" -- on Monday, en.wiktionary's own worked
example under को's "in, at the time of" sense).  Inside the frame हर has
already made the reading recurring, so को adds nothing to the rule and must be
swallowed rather than stranded -- a rule that is right but a remainder that is
not empty is a half-read phrase, and the caller cannot tell which half.

को is shipped as the SINGULAR weekday-word only.  The plural counterpart is
what would license a BARE postposed weekday as recurring, and Hindi has no
such form: "सोमवार को" on its own names one specific Monday, so it must not
read as a recurrence at all.
"""
import pytest

from chronologia.extract import extract_recurrence

LANG = "hi"

_CASES = [
    # weekday recurrences, with and without the trailing locative
    ("हर सोमवार", "FREQ=WEEKLY;BYDAY=MO", ""),
    ("हर सोमवार को", "FREQ=WEEKLY;BYDAY=MO", ""),
    ("हर शुक्रवार", "FREQ=WEEKLY;BYDAY=FR", ""),
    ("हर शुक्रवार को", "FREQ=WEEKLY;BYDAY=FR", ""),
    ("हर मंगलवार को", "FREQ=WEEKLY;BYDAY=TU", ""),
    ("हर रविवार को", "FREQ=WEEKLY;BYDAY=SU", ""),
    ("हर इतवार को", "FREQ=WEEKLY;BYDAY=SU", ""),
    # a listed pair takes the locative once, after the last day
    ("हर सोमवार और शुक्रवार को", "FREQ=WEEKLY;BYDAY=MO,FR", ""),
    # unit recurrences, which carry no weekday and so never take को
    ("हर दिन", "FREQ=DAILY", ""),
    ("हर हफ़्ते", "FREQ=WEEKLY", ""),
    ("हर सप्ताह", "FREQ=WEEKLY", ""),
    ("हर महीने", "FREQ=MONTHLY", ""),
    ("हर साल", "FREQ=YEARLY", ""),
    ("हर वर्ष", "FREQ=YEARLY", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", [
    "हर सोमवार को", "हर शुक्रवार को", "हर रविवार को",
    "हर सोमवार और शुक्रवार को",
])
def test_the_locative_is_swallowed_not_stranded(text):
    """The defect this pins: the rule resolved correctly while को was left in
    the remainder, so the phrase read as only partly understood."""
    assert extract_recurrence(text, LANG)[1] == ""


@pytest.mark.parametrize("text,rrule", [
    ("हर सोमवार", "FREQ=WEEKLY;BYDAY=MO"),
    ("हर शुक्रवार", "FREQ=WEEKLY;BYDAY=FR"),
])
def test_the_locative_changes_nothing_about_the_rule(text, rrule):
    """Adding को must not alter the rule it trails -- it is filler inside an
    already-opened frame, not a modifier."""
    assert extract_recurrence(text, LANG)[0].to_string() == rrule
    assert extract_recurrence(f"{text} को", LANG)[0].to_string() == rrule


@pytest.mark.parametrize("text", [
    "सोमवार को", "शुक्रवार को", "रविवार को",
    "सोमवार", "आज", "15 मार्च 2024 को", "शाम को",
])
def test_a_bare_weekday_with_the_locative_is_not_a_recurrence(text):
    """"सोमवार को" is ONE Monday, not every Monday.  Hindi has no plural
    weekday-word to license the bare postposed recurring reading, so these
    stay single dates for the grammar engine and are refused here."""
    assert extract_recurrence(text, LANG) is None
