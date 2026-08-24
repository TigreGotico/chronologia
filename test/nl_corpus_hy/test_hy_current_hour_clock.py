"""The Armenian spoken clock, which counts from the hour ALREADY REACHED.

``ութ անց կես`` is 08:30 -- the half belongs to the eighth hour, the
English-shaped reading, not the toward-the-coming-hour reading Icelandic and
several neighbouring languages use.  Geography does not predict this: the
direction is fixed here from Armenian's own worked examples and nothing else.
Every reading is pinned in both directions, so a silent flip to the coming
hour fails a test rather than shifting an answer by an hour.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, parse, start


def _next_time(h, mi):
    cand = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    return ad(cand)


@pytest.mark.parametrize("text,h,mi", [
    ("ութ անց կես", 8, 30),
    ("վեց անց կես", 6, 30),
    ("հինգ անց կես", 5, 30),
    ("ինը անց կես", 9, 30),
    ("ժամը հինգն անց կես", 5, 30),
    ("ժամը վեցն ու կեսը", 6, 30),
    ("ժամը ութն ու կեսը", 8, 30),
])
def test_half_names_the_hour_already_reached(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,forbidden", [
    ("ութ անց կես", 7),
    ("վեց անց կես", 5),
    ("ժամը վեցն ու կեսը", 5),
    ("ժամը հինգն անց կես", 4),
])
def test_half_is_never_the_hour_before(text, forbidden):
    """The toward-the-coming-hour reading ("half of six" == 05:30) must never
    occur: it would move every half-hour answer back by an hour."""
    assert start(text).hour != forbidden


@pytest.mark.parametrize("text,h,mi", [
    ("ժամը յոթը քառորդ անց", 7, 15),
    ("ժամը երեքը քառորդ անց", 3, 15),
    ("տասը քառորդ անց", 10, 15),
])
def test_quarter_past_counts_up_from_the_named_hour(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,forbidden", [
    ("ժամը յոթը քառորդ անց", 6),
    ("տասը քառորդ անց", 9),
])
def test_quarter_past_is_never_quarter_to(text, forbidden):
    assert start(text).hour != forbidden


@pytest.mark.parametrize("text,h", [
    ("ժամը տասը", 10), ("ժամը վեցը", 6), ("ժամը երեքն", 3),
])
def test_bare_hour(text, h):
    assert start(text) == _next_time(h, 0)


@pytest.mark.parametrize("text,h,mi", [
    ("կեսօրին", 12, 0),
    ("կեսգիշերին", 0, 0),
    ("ժամը կեսօրին", 12, 0),
])
def test_landmarks(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text", [
    "ժամը երեքից քառորդ առաջ", "երեքից քառորդ առաջ",
    "ժամը յոթը քառորդ պակաս", "յոթը քառորդ պակաս",
])
def test_no_quarter_to(text):
    """Two mutually irreconcilable "quarter to" constructions are reported --
    one ablative-governed with առաջ, one with պակաս -- and neither could be
    attested with a worked example, so neither ships.  The phrase is refused
    or leaves its quarter unread rather than committing to a guess."""
    r = parse(text)
    assert r is None or "քառորդ" in r[1]
