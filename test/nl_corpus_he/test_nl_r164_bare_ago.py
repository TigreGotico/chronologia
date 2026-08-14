# -*- coding: utf-8 -*-
"""R164: Hebrew bare-unit "ago" ("לפני שעה" = an hour ago).

Numbered offsets ("לפני 3 שעות") already worked; the bare, implicit-one
form did not, unlike its English sibling "an hour ago". Gold by independent
:mod:`datetime` arithmetic against the shared ANCHOR (Tuesday 2017-06-27
13:04), converted through ``ad()`` to compare against the returned
``AstroDate``.
"""
from datetime import timedelta

from ._corpus import ANCHOR, ad, start_end


def test_bare_hour_ago():
    assert start_end("לפני שעה") == (ad(ANCHOR - timedelta(hours=1)), ad(ANCHOR))


def test_bare_minute_ago():
    assert start_end("לפני דקה") == (ad(ANCHOR - timedelta(minutes=1)),
                                       ad(ANCHOR))


def test_bare_day_ago():
    assert start_end("לפני יום") == (ad(ANCHOR - timedelta(days=1)),
                                       ad(ANCHOR))


def test_control_numbered_offset_still_works():
    """Numbered offsets were never broken; guards against a regression.

    A relative-offset span is ``[value, value + 1*unit)`` -- one unit wide --
    so only the implicit-1 bare form ("לפני שעה") happens to close exactly on
    the anchor; "3 hours ago" closes one hour after its own start.
    """
    offset_start = ANCHOR - timedelta(hours=3)
    assert start_end("לפני 3 שעות") == (ad(offset_start),
                                          ad(offset_start + timedelta(hours=1)))


def test_control_english_an_hour_ago():
    """English sibling this Hebrew form now mirrors."""
    from chronologia import extract_timespan
    r = extract_timespan("an hour ago", "en", ANCHOR)
    assert r is not None
    assert (r[0].start, r[0].end) == (ad(ANCHOR - timedelta(hours=1)),
                                        ad(ANCHOR))
