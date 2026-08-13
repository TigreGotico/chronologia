"""R158: a year-less date followed by a spoken fractional clock ("les N i
quart") must compose, not drop the whole clock.

The matcher's day-of-month/hour disambiguation guard ("June 15 in the
morning" is not "June [hour]15[/hour]") walked back across the Catalan
"les" article/at-marker and, finding the MONTH surface right behind it,
vetoed every "clock_time" candidate whose HOUR sat there -- even one that
also carried CLOCKDIR + FRACTION ("i quart"), which can never be mistaken
for a bare day-of-month digit.  With an explicit year in between ("de
2026") the guard's one-article lookback landed on the YEAR instead of the
MONTH and never fired, so only the (year-less, date-first) cell dropped the
clock -- "25 de desembre les nou i quart" resolved to the bare date with
"les nou i quart" stranded.  Gold below is independently computed.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ad, start_end


def test_yearless_date_first_spoken_clock_composes():
    s, e = start_end("25 de desembre les nou i quart")
    assert s == ad(datetime(2017, 12, 25, 9, 15))
    assert e == s + timedelta(minutes=1)


# -- controls: must not regress -----------------------------------------

def test_control_with_year_unchanged():
    s, e = start_end("25 de desembre de 2026 les nou i quart")
    assert s == ad(datetime(2026, 12, 25, 9, 15))
    assert e == s + timedelta(minutes=1)


def test_control_clock_first_yearless_unchanged():
    s, e = start_end("les nou i quart 25 de desembre")
    assert s == ad(datetime(2017, 12, 25, 9, 15))
    assert e == s + timedelta(minutes=1)


def test_control_digit_clock_yearless_unchanged():
    s, e = start_end("25 de desembre 15:30")
    assert s == ad(datetime(2017, 12, 25, 15, 30))
    assert e == s + timedelta(minutes=1)


# -- recombined variants (attested surfaces only) ------------------------

def test_yearless_date_first_other_spoken_clock_composes():
    s, e = start_end("25 de desembre les tres i quart")
    assert s == ad(datetime(2017, 12, 25, 3, 15))
    assert e == s + timedelta(minutes=1)


def test_yearless_other_date_first_spoken_clock_composes():
    s, e = start_end("5 de juny les nou i quart")
    assert (s.month, s.day, s.hour, s.minute) == (6, 5, 9, 15)
    assert e == s + timedelta(minutes=1)
