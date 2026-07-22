# -*- coding: utf-8 -*-
"""Open-ended ranges (hu): Hungarian frames the closed end with markers the
engine reaches through their POSITIONALITY, not the leading order it assumes by
default.

* ``until`` is the CASE SUFFIX ``-ig`` fused onto the date's final token
  ("péntekig" = "péntek" + "ig" = until Friday; "2026-ig"), declared
  ``positions.until = "affix"``.  The affix is split off only when the stripped
  host parses as a date, so a common word ending in the same letters
  ("nadrágig" = "trousers-until") never misfires.
* ``since`` is the **postposed** word ``óta`` ("2010 óta" = since 2010),
  declared ``positions.since = "post"``.

Endpoints hand-derived against the mission anchor (2017-06-27, a Tuesday):
the next Friday is 2017-06-30, the next Monday 2017-07-03."""
from datetime import datetime

from chronologia.extract import extract_timespan
from chronologia.astrodate import AstroDate

A = datetime(2017, 6, 27, 13, 4)
NOW = AstroDate.from_datetime(A)


def _span(text):
    r = extract_timespan(text, "hu", anchor=A)
    assert r is not None, f"{text!r} did not parse"
    return r[0]


# -- affix "-ig" (until, open start bounded above by the endpoint) -------------

def test_ig_affix_open_start_weekday():
    # "péntekig" = "péntek" (Friday) + "ig": until the next Friday, inclusive
    s = _span("péntekig")
    assert s.start == NOW and s.end == AstroDate(2017, 7, 1)


def test_ig_affix_open_start_monday():
    # "hétfőig" = "hétfő" (Monday) + "ig": until the next Monday
    s = _span("hétfőig")
    assert s.start == NOW and s.end == AstroDate(2017, 7, 4)


def test_ig_affix_open_start_year_hyphenated():
    # "2026-ig": the hyphen splits the token, so "ig" trails as a bound word --
    # the postposed reading of the same affix marker; until the end of 2026
    s = _span("2026-ig")
    assert s.start == NOW and s.end == AstroDate(2027, 1, 1)


# -- postposed "óta" (since, open end anchored to "now") -----------------------

def test_ota_postposed_open_end_year():
    # "2010 óta" = since 2010: [2010-01-01, now)
    s = _span("2010 óta")
    assert s.start == AstroDate(2010, 1, 1) and s.end == NOW


# -- false-split / homograph guards -------------------------------------------

def test_ig_affix_does_not_bind_a_non_date_host():
    # "nadrágig" = "nadrág" (trousers) + "ig"; the host is not a date, so the
    # affix must NOT be split -- no range
    assert extract_timespan("nadrágig", "hu", anchor=A) is None


def test_bare_ig_is_not_a_range():
    # the bare affix with no host token is not an open range
    assert extract_timespan("ig", "hu", anchor=A) is None


def test_bare_ota_is_not_a_range():
    # a lone postposed marker with no date endpoint is not an open range
    assert extract_timespan("óta", "hu", anchor=A) is None
