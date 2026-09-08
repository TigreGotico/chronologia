"""Swedish lengths counted with a bare fraction ("om en halvtimme", "om en
kvart"), the offset counted from now ("5 dagar från nu") and from a weekday
("2 dagar från fredag"), and the noun "morgondagen".

Wiktionary: halvtimme "half an hour, a half-hour"; kvart "a quarter of an
hour, 15 minutes"; morgondag / morgondagen "tomorrow".  sv.wikipedia running
text: "nyhetsblock om en halvtimme" (Canal 24 Horas), "Efter en kvart hade
han redan gjort tre mål" (Zlatan Ibrahimović), "Morgondagens väder" (Bigert
& Bergström), the album title "Från nu till evighet".

Anchor: Tuesday 2017-06-27 13:04.  Every value is anchor arithmetic; the
weekday offset counts from the next Friday, 2017-06-30.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, parse

D = timedelta(days=1)


def _offset(text, delta, grain, rem=""):
    res = parse(text)
    assert res is not None, f"{text!r} did not parse"
    assert res.remainder == rem, f"{text!r} left {res.remainder!r}"
    assert res[0].start == ad(ANCHOR + delta)
    assert res[0].end == ad(ANCHOR + delta + grain)


@pytest.mark.parametrize("text,delta", [
    ("om en halvtimme", timedelta(minutes=30)),
    ("om en halv timme", timedelta(minutes=30)),
    ("för en halvtimme sedan", timedelta(minutes=-30)),
    ("om en kvart", timedelta(minutes=15)),
    ("för en kvart sedan", timedelta(minutes=-15)),
])
def test_fraction_of_an_hour_length(text, delta):
    res = parse(text)
    assert res is not None and res.remainder == ""
    assert res[0].start == ad(ANCHOR + delta)


def test_half_and_quarter_do_not_collapse():
    assert parse("om en halvtimme")[0].start - parse("om en kvart")[0].start \
        == timedelta(minutes=15)


@pytest.mark.parametrize("text,h,m", [("halv tre", 2, 30), ("kvart över tre", 3, 15),
                                      ("kvart i tre", 2, 45)])
def test_the_clock_fraction_is_untouched(text, h, m):
    res = parse(text)
    assert res[0].start == ad(ANCHOR.replace(hour=h, minute=m) + D)


@pytest.mark.parametrize("text,rem", [
    ("5 dagar från nu", ""),
    ("planera bakhållet 5 dagar från nu", "planera bakhållet"),
])
def test_from_now(text, rem):
    _offset(text, 5 * D, D, rem)


@pytest.mark.parametrize("text,rem", [
    ("2 dagar från fredag", ""),
    ("spela kurt olssons musik 2 dagar från fredag", "spela kurt olssons musik"),
])
def test_days_from_a_weekday(text, rem):
    res = parse(text)
    assert res is not None and res.remainder == rem
    friday = ANCHOR.replace(hour=0, minute=0) + 3 * D          # 2017-06-30
    assert res[0].start == ad(friday + 2 * D)
    assert res[0].end == ad(friday + 3 * D)


@pytest.mark.parametrize("text,rem", [
    ("morgondagen", ""),
    ("vad blir morgondagens väder", "vad blir väder"),
])
def test_morgondagen_is_tomorrow(text, rem):
    res = parse(text)
    assert res is not None and res.remainder == rem
    assert res[0].start == ad(ANCHOR.replace(hour=0, minute=0) + D)
    assert res[0].end == ad(ANCHOR.replace(hour=0, minute=0) + 2 * D)
