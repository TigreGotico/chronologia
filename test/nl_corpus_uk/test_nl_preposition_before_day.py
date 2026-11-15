"""Ukrainian "в", "у" and "на" before a named day belong to the date.

"в"/"у" + accusative takes a weekday with or without a determiner: "в
п'ятницю", "у наступний понеділок".  "на" + accusative names the time a
thing happens (uk.wiktionary, s.v. на, sense 9, "Уживається для позначення
часу, коли відбувається якась дія"): "на завтра", "на п'ятницю".  "на" +
locative names the span a thing happens in (the same entry, sense 10): "на
вихідних", "на наступному тижні".  The preposition is part of the date
phrase, so the remainder keeps only the words around it.

The anchor is Tuesday 27 June 2017.  Friday is 30 June, Monday next week is
3 July, the weekend is Saturday 1 July to Monday 3 July, and next week runs
from Monday 3 July to Monday 10 July.
"""
from datetime import datetime

import pytest

from ._corpus import ad, parse


@pytest.mark.parametrize("text,start,end,remainder", [
    ("в наступний понеділок", (7, 3), (7, 4), ""),
    ("у наступний понеділок", (7, 3), (7, 4), ""),
    ("на завтра", (6, 28), (6, 29), ""),
    ("на п'ятницю", (6, 30), (7, 1), ""),
    ("нагадай мені на завтра", (6, 28), (6, 29), "нагадай мені"),
    ("на вихідних", (7, 1), (7, 3), ""),
    ("на цих вихідних", (7, 1), (7, 3), ""),
    ("у вихідні", (7, 1), (7, 3), ""),
    ("на наступному тижні", (7, 3), (7, 10), ""),
    ("на минулому тижні", (6, 19), (6, 26), ""),
])
def test_preposition_joins_the_day(text, start, end, remainder):
    r = parse(text)
    assert r is not None
    assert r.span.start == ad(datetime(2017, *start))
    assert r.span.end == ad(datetime(2017, *end))
    assert r.remainder == remainder


@pytest.mark.parametrize("text,day,hour", [
    ("в наступний понеділок о 9 ранку", (7, 3), 9),
    ("на завтра о сьомій", (6, 28), 7),
])
def test_preposition_before_day_and_clock(text, day, hour):
    r = parse(text)
    assert r is not None
    assert r.span.start == ad(datetime(2017, *day, hour, 0))
    assert r.remainder == ""


@pytest.mark.parametrize("text", [
    "на столі",
    "на цей раз",
    "на два тижні",
])
def test_preposition_without_a_day_stays_unread(text):
    assert parse(text) is None
