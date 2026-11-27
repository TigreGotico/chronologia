# -*- coding: utf-8 -*-
"""fr "moins le quart" takes a quarter of an hour off a count of hours.

"une heure moins le quart" is 45 minutes.  Anchors: Friday 2026-01-30 10:00
for the event and Sunday 2026-11-22 09:00 for the length; "avant minuit" ends
the length at 2026-11-23 00:00, so the span runs from 23:15.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_duration, extract_event, extract_timespan

ISSUE = "https://github.com/TigreGotico/chronologia/issues/1028"
ANCHOR = datetime(2026, 11, 22, 9, 0)


@pytest.mark.xfail(raises=AssertionError, strict=True, reason=ISSUE)
def test_event_summary_keeps_no_moins_le_quart():
    event = extract_event(
        "réunion de deux heures moins le quart le matin demain", "fr",
        anchor=datetime(2026, 1, 30, 10, 0))
    assert event.summary == "réunion"


@pytest.mark.xfail(raises=AssertionError, strict=True, reason=ISSUE)
def test_une_heure_moins_le_quart_is_45_minutes():
    found = extract_duration(
        "une heure moins le quart avant minuit", "fr", anchor=ANCHOR)
    assert found.duration == timedelta(minutes=45)


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=ISSUE)
def test_une_heure_moins_le_quart_avant_minuit_ends_at_midnight():
    found = extract_timespan(
        "une heure moins le quart avant minuit", "fr", ANCHOR)
    assert found is not None, "no reading for 'une heure moins le quart avant minuit'"
    assert (found.span.start.datetime(), found.span.end.datetime()) == (
        datetime(2026, 11, 22, 23, 15), datetime(2026, 11, 23, 0, 0))
