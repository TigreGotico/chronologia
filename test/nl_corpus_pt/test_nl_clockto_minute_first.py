# -*- coding: utf-8 -*-
"""The pt minute-first clock orders ("MINUTE CLOCKTO article? HOUR") take only
the "to the hour" words ("para", "menos").  The past word "e" follows the hour
("três e dez" is ten past three), so it can never start a minute-first
reading that fabricates minute 3 of hour 10.

Gold is by hand: ten past three is 3:10, read as 15:10 against a 10:00 anchor
(prefer_future); a quarter to three is 2:45, read as 14:45.
"""
from datetime import datetime

import pytest

from chronologia import extract_candidates, extract_timespan

ANCHOR = datetime(2026, 11, 25, 10, 0)


def starts(text):
    return [c.span.start.strftime("%H:%M")
            for c in extract_candidates(text, "pt-PT", ANCHOR)]


def top(text):
    cands = extract_candidates(text, "pt-PT", ANCHOR)
    return [c.span.start.strftime("%H:%M") for c in cands
            if c.confidence == cands[0].confidence]


@pytest.mark.parametrize("text,wrong", [
    ("três e dez", "10:03"),
    ("às três e dez", "10:03"),
    ("três e dez da tarde", "22:03"),
    ("às três e dez da tarde", "22:03"),
    ("cinco e dez da tarde", "22:05"),
    ("cinco e dez da tarde", "10:05"),
])
def test_past_word_never_reads_minute_first(text, wrong):
    assert wrong not in starts(text)


@pytest.mark.parametrize("text,right", [
    ("três e dez", "15:10"),
    ("às três e dez", "15:10"),
    ("três e dez da tarde", "15:10"),
    ("às três e dez da tarde", "15:10"),
    ("cinco e dez da tarde", "17:10"),
])
def test_past_clock_is_the_only_top_reading(text, right):
    assert top(text) == [right]


def test_past_word_between_hours_reads_no_minutes():
    res = extract_timespan("três e as quatro da tarde", "pt-PT", ANCHOR)
    assert (res.span.start.hour, res.span.start.minute) == (16, 0)


@pytest.mark.parametrize("text,hm", [
    ("um quarto para as três", "14:45"),
    ("três menos um quarto", "14:45"),
    ("três e um quarto", "15:15"),
    ("dez para as três", "14:50"),
])
def test_to_and_past_controls(text, hm):
    assert top(text) == [hm]
