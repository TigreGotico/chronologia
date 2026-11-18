# -*- coding: utf-8 -*-
"""The bare word "می" and the weekday names written with a space.

"می" before a verb is the durative prefix ("می‌خواهم" I want), and the OVOS
utterance normalizer writes the joiner as a space.  Wiktionary "می" lists the
month May only as Dari and Indo-Persian usage, so the word is a month beside a
day, a year or "ماه" and at the end of a clause, and the prefix otherwise.

"سه شنبه" is Tuesday (Wiktionary "سه‌شنبه": "three (days after) Saturday"),
and "شنبه" alone is Saturday.  The anchor is Tuesday 2017-06-27 13:04.  Gold
dates come from calendar arithmetic: the next Tuesday after the anchor's own
Tuesday is 2017-07-04, the next Monday is 2017-07-03, and the next May is the
May of 2018 (ruling 1).
"""
import pytest

from ._corpus import ad, nomatch, parse, span
from datetime import datetime


@pytest.mark.parametrize("text", [
    "این سرمای شدید هوا ادامه پیدا می کند",
    "بیرون باد می وزد یا هوا آرام است",
])
def test_verb_prefix_is_no_month(text):
    nomatch(text)


def test_verb_prefix_beside_a_real_date():
    r = parse("می خواهم بدانم هوای فردا قرار است چطور باشد")
    assert r[0].start == ad(datetime(2017, 6, 28))
    assert r[0].end == ad(datetime(2017, 6, 29))
    assert "می خواهم" in r[1]


def test_verb_prefix_after_a_weekday_and_daypart():
    r = parse("دمای هوا صبح دوشنبه چند درجه می شود")
    assert r[0].start == ad(datetime(2017, 7, 3, 1))
    assert r[0].end == ad(datetime(2017, 7, 3, 12))
    assert r[1] == "دمای هوا چند درجه می شود"


@pytest.mark.parametrize("text,start,end", [
    ("می", datetime(2018, 5, 1), datetime(2018, 6, 1)),
    ("ماه می", datetime(2018, 5, 1), datetime(2018, 6, 1)),
    ("می ۲۰۲۰", datetime(2020, 5, 1), datetime(2020, 6, 1)),
    ("هوا در ماه می چطور است", datetime(2018, 5, 1), datetime(2018, 6, 1)),
    ("۱۵ می چطور است", datetime(2018, 5, 15), datetime(2018, 5, 16)),
    ("۱۵ می", datetime(2018, 5, 15), datetime(2018, 5, 16)),
    ("15 می", datetime(2018, 5, 15), datetime(2018, 5, 16)),
])
def test_may_month_keeps_its_cues(text, start, end):
    s = span(text)
    assert (s.start, s.end) == (ad(start), ad(end))


@pytest.mark.parametrize("text,start,end,rest", [
    ("هوا سه شنبه ساعت یک بامداد چطور خواهد بود",
     datetime(2017, 7, 4, 1), datetime(2017, 7, 4, 1, 1),
     "هوا بامداد چطور خواهد بود"),
    ("دمای پایین روز سه شنبه صبح چیست",
     datetime(2017, 7, 4, 1), datetime(2017, 7, 4, 12), "دمای پایین روز چیست"),
    ("دو شنبه صبح", datetime(2017, 7, 3, 1), datetime(2017, 7, 3, 12), ""),
    ("چهار شنبه", datetime(2017, 6, 28), datetime(2017, 6, 29), ""),
    ("پنج شنبه", datetime(2017, 6, 29), datetime(2017, 6, 30), ""),
    ("یک شنبه", datetime(2017, 7, 2), datetime(2017, 7, 3), ""),
])
def test_spaced_weekday_names(text, start, end, rest):
    r = parse(text)
    assert (r[0].start, r[0].end) == (ad(start), ad(end))
    assert r[1] == rest


def test_saturday_alone_is_unchanged():
    s = span("شنبه")
    assert s.start == ad(datetime(2017, 7, 1))
    assert s.end == ad(datetime(2017, 7, 2))
