"""Hungarian case suffixes written after a hyphen, and "este fél kilenc".

AkH. 12, rule 298, joins a suffix to a day number with a hyphen: "1848. márc.
15-én", "2014. febr. 28-a", "1-je", "1-jén".  Rule 300 does the same for a
digit clock: "10:35-kor".  The sublative "-ra"/"-re" names the same point as
a target.  The suffix belongs to the date or the clock, so it does not stay in
the remainder.  An article after a space is a separate word.

"este" is the evening, 6 to 10 p.m., and "fél 8" is 7:30 (Wikipedia, "Date and
time notation in Hungary"), so "este fél kilenc" is 20:30.  At the Tuesday 27
June 2017 13:04 anchor that time is still ahead today.  The next 29 February is
in 2020, and 15 March has passed, so it is the 2018 date.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ad, parse


def _day(y, m, d):
    return ad(datetime(y, m, d))


def _next_day(y, m, d):
    return ad(datetime(y, m, d) + timedelta(days=1))


@pytest.mark.parametrize("text,y,m,d", [
    ("augusztus 3-án", 2017, 8, 3),
    ("március 15-én", 2018, 3, 15),
    ("május 1-jén", 2018, 5, 1),
    ("május 1-je", 2018, 5, 1),
    ("augusztus 20-a", 2017, 8, 20),
    ("február 29-én 2024", 2024, 2, 29),
    ("2024. február 29-én", 2024, 2, 29),
])
def test_day_suffix_is_part_of_the_date(text, y, m, d):
    r = parse(text)
    assert r is not None
    assert r.span.start == _day(y, m, d)
    assert r.span.end == _next_day(y, m, d)
    assert r.remainder == ""


@pytest.mark.parametrize("text,when", [
    ("17:30-kor", datetime(2017, 6, 27, 17, 30)),
    ("holnap 17:30-kor", datetime(2017, 6, 28, 17, 30)),
    ("17:30-ra", datetime(2017, 6, 27, 17, 30)),
    ("reggel 7-re", datetime(2017, 6, 28, 7, 0)),
    ("február 29-én 8 órakor", datetime(2020, 2, 29, 8, 0)),
    ("március 15-én 10:35-kor", datetime(2018, 3, 15, 10, 35)),
    ("este fél kilenc", datetime(2017, 6, 27, 20, 30)),
    ("holnap este fél kilenc", datetime(2017, 6, 28, 20, 30)),
])
def test_clock_suffix_and_evening_half(text, when):
    r = parse(text)
    assert r is not None
    assert r.span.start == ad(when)
    assert r.remainder == ""


def test_article_after_a_space_stays_a_word():
    r = parse("május 3 a legjobb nap")
    assert r is not None
    assert r.span.start == _day(2018, 5, 3)
    assert r.remainder == "a legjobb nap"


def test_until_suffix_keeps_its_meaning():
    r = parse("július 6-ig")
    assert r is not None
    assert r.span.end == _day(2017, 7, 7)
    assert r.remainder == ""
