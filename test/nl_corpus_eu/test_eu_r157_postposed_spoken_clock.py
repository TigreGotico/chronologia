"""R157: the spoken "-ak eta erdi/laurden" clock must compose onto a date
that PRECEDES it, not just one that follows it.

The clock grammar's "HOUR CLOCKDIR FRACTION" order and the shared
spelled-number fold used to collide when the hour word directly followed a
just-matched calendar date's own trailing digit: the fold read the two
adjacent number tokens (the date's day digit and the spoken hour) as one
run and silently dropped one of them, so "1999ko martxoaren 15ean hamarrak
eta erdi" resolved to the bare date with "eta erdi" stranded and the hour
word "hamarrak" swallowed entirely (not even left in the remainder).  Gold
below is independently computed: date-first and clock-first must compose
identically.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, start_end, start


@pytest.mark.parametrize("text,y,mo,d,h,mi", [
    ("1999ko martxoaren 15ean hamarrak eta erdi", 1999, 3, 15, 10, 30),
    ("2021eko abenduaren 25ean bostak eta erdi", 2021, 12, 25, 5, 30),
])
def test_date_first_spoken_clock_composes(text, y, mo, d, h, mi):
    s, e = start_end(text)
    assert s == ad(datetime(y, mo, d, h, mi))
    assert e == s + timedelta(minutes=1)


def test_date_first_spoken_clock_composes_year_less():
    s, e = start_end("ekainaren 5ean bostak eta erdi")
    assert (s.month, s.day, s.hour, s.minute) == (6, 5, 5, 30)
    assert e == s + timedelta(minutes=1)


# -- controls: must not regress -----------------------------------------

def test_control_clock_first_unchanged():
    s, e = start_end("bostak eta erdi 2020ko ekainaren 5ean")
    assert s == ad(datetime(2020, 6, 5, 5, 30))
    assert e == s + timedelta(minutes=1)


def test_control_digit_clock_both_orders_unchanged():
    s, e = start_end("2021eko abenduaren 25ean 09:15")
    assert s == ad(datetime(2021, 12, 25, 9, 15))
    assert e == s + timedelta(minutes=1)


def test_control_weekday_plus_spoken_clock_unchanged():
    s, e = start_end("datorren ostirala bostak eta erdi")
    assert (s.year, s.month, s.day) == (2017, 6, 30)
    assert (s.hour, s.minute) == (5, 30)
    assert e == s + timedelta(minutes=1)


# -- recombined variants (attested surfaces only) ------------------------

def test_date_first_quarter_past_composes():
    s, e = start_end("1999ko martxoaren 15ean laurak eta laurden")
    assert s == ad(datetime(1999, 3, 15, 4, 15))
    assert e == s + timedelta(minutes=1)


def test_date_first_spoken_clock_absolutive_day_composes():
    s, e = start_end("2020ko ekainaren 5a hirurak eta erdi")
    assert s == ad(datetime(2020, 6, 5, 3, 30))
    assert e == s + timedelta(minutes=1)
