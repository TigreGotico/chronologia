# -*- coding: utf-8 -*-
"""Three ru and uk reading gaps.

A year number is no hour: ru "в 1 году" names a year, so the clock reading
of the bare number is dropped.  uk "минулої ночі" is "last night" as ru
"прошлой ночью" is: "ночі" is the genitive singular of "ніч" (Wiktionary,
ніч, declension table).  The accusative "страсну п'ятницю" and ru "страстную
пятницю" name Good Friday of the Orthodox calendar, whose date follows
Orthodox Easter.

Anchor: Tuesday 2017-06-27 13:04.  Orthodox Easter 2018 is Sunday 8 April
(the Julian-calendar computus, 2018-04-08 Gregorian), so Good Friday is
2018-04-06.  "минулої ночі" is the night band of the same day as ru
"прошлой ночью", 00:00 to 04:00 (CLDR night band 00:00 to 04:00 in
``chronologia/dayparts.py``).
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)
GOOD_FRIDAY = datetime(2018, 4, 6)


@pytest.mark.parametrize("text", ["в 0 году", "в 1 году", "в 3 году"])
def test_a_year_number_is_no_hour(text):
    assert extract_timespan(text, "ru", ANCHOR) is None


@pytest.mark.parametrize("text,instant", [
    ("в 3 часа", datetime(2017, 6, 27, 15)),
    ("в 5 часов утра", datetime(2017, 6, 28, 5)),
])
def test_a_clock_with_a_unit_stays_a_clock(text, instant):
    assert extract_timespan(text, "ru", ANCHOR).span.start.datetime() == instant


@pytest.mark.parametrize("text", ["минулої ночі"])
def test_uk_last_night_reads_as_ru_does(text):
    found = extract_timespan(text, "uk", ANCHOR)
    ru = extract_timespan("прошлой ночью", "ru", ANCHOR)
    assert found.span.start.datetime() == datetime(2017, 6, 27, 0)
    assert found.span.end.datetime() == datetime(2017, 6, 27, 4)
    assert (found.span.start, found.span.end) == (ru.span.start, ru.span.end)
    assert found.remainder == ""


@pytest.mark.parametrize("lang,text", [
    ("uk", "в страсну п'ятницю"),
    ("uk", "у велику п'ятницю"),
    ("uk", "страсна п'ятниця"),
    ("ru", "в страстную пятницу"),
    ("ru", "страстная пятница"),
])
def test_orthodox_good_friday(lang, text):
    found = extract_timespan(text, lang, ANCHOR)
    assert found.span.start.datetime() == GOOD_FRIDAY
    assert found.span.end.datetime() == datetime(2018, 4, 7)
    assert found.remainder == ""


def test_uk_night_clock_suffix_is_unchanged():
    found = extract_timespan("о 2 ночі", "uk", ANCHOR)
    assert found.span.start.datetime() == datetime(2017, 6, 28, 2)
