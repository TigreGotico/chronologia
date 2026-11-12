"""Russian "в" and "на" before a named day belong to the date.

"в" + accusative takes a weekday with or without a determiner: "в пятницу",
"в следующую пятницу", "в прошлый понедельник".  "на" + accusative names the
day a thing is meant for (Ожегов, s.v. НА, II.1, "употр. при обозначении
срока, промежутка времени"): "на завтра", "на пятницу".  "на" + prepositional
names the span a thing happens in (ru.wiktionary, s.v. на, sense 2.4): "на
выходных".  The preposition is part of the date phrase, so the remainder
keeps only the words around it.

The anchor is Tuesday 27 June 2017.  Friday is 30 June, Monday last week is
26 June, Tuesday next week is 4 July, and the weekend is Saturday 1 July to
Monday 3 July.
"""
from datetime import datetime

import pytest

from ._corpus import ad, parse


@pytest.mark.parametrize("text,start,end,remainder", [
    ("в следующую пятницу", (6, 30), (7, 1), ""),
    ("в прошлый понедельник", (6, 26), (6, 27), ""),
    ("в эту пятницу", (6, 30), (7, 1), ""),
    ("напомни мне в следующий вторник", (7, 4), (7, 5), "напомни мне"),
    ("на завтра", (6, 28), (6, 29), ""),
    ("на послезавтра", (6, 29), (6, 30), ""),
    ("на пятницу", (6, 30), (7, 1), ""),
    ("на следующую пятницу", (6, 30), (7, 1), ""),
    ("поставь будильник на завтра", (6, 28), (6, 29), "поставь будильник"),
    ("встреча перенесена на пятницу", (6, 30), (7, 1),
     "встреча перенесена"),
    ("на выходных", (7, 1), (7, 3), ""),
    ("на этих выходных", (7, 1), (7, 3), ""),
    ("в эти выходные", (7, 1), (7, 3), ""),
    ("в выходные", (7, 1), (7, 3), ""),
])
def test_preposition_joins_the_day(text, start, end, remainder):
    r = parse(text)
    assert r is not None
    assert r.span.start == ad(datetime(2017, *start))
    assert r.span.end == ad(datetime(2017, *end))
    assert r.remainder == remainder


@pytest.mark.parametrize("text,hour,day", [
    ("в следующую пятницу в 9 утра", 9, 30),
    ("на завтра в 7 утра", 7, 28),
])
def test_preposition_before_day_and_clock(text, hour, day):
    r = parse(text)
    assert r is not None
    assert r.span.start == ad(datetime(2017, 6, day, hour, 0))
    assert r.remainder == ""


@pytest.mark.parametrize("text", [
    "положи книгу на стол",
    "на север",
    "на этот раз",
    "в этот раз",
])
def test_preposition_without_a_day_stays_unread(text):
    assert parse(text) is None
