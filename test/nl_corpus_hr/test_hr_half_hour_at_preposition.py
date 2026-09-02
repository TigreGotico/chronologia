"""The "at" preposition in front of the half-hour clock.

"u pola devet" is the ordinary way to say half past eight; "u" is not part
of the answer and must be consumed by the match.  The Croatian clock orders
offered "FRACTION HOUR" without the optional leading preposition, so the
time came out right and the "u" was left stranded in the remainder -- a
match that looks correct until the caller inspects what was not consumed.
"""
from datetime import datetime, timedelta

from ._corpus import ANCHOR, ad, parse, span


def test_u_pola_devet_consumes_the_preposition():
    r = parse("u pola devet")
    assert r is not None
    assert r[1] == ""


def test_u_pola_devet_is_half_past_eight_tomorrow():
    # the anchor is 13:04, so the next 08:30 is the following morning
    r = parse("u pola devet")
    assert r is not None
    assert r[0].start == ad(datetime(ANCHOR.year, ANCHOR.month,
                                     ANCHOR.day, 8, 30) + timedelta(days=1))


def test_the_preposition_does_not_change_the_answer():
    assert span("u pola devet") == span("pola devet")


def test_u_830_consumes_the_preposition():
    # the same preposition in front of a DIGITAL clock: the time was already
    # right, the "u" was the defect
    r = parse("u 8:30")
    assert r is not None
    assert r[1] == ""
    assert r[0].start == ad(datetime(ANCHOR.year, ANCHOR.month,
                                     ANCHOR.day, 8, 30) + timedelta(days=1))


def test_u_2030_consumes_the_preposition():
    r = parse("u 20:30")
    assert r is not None
    assert r[1] == ""
    assert r[0].start == ad(datetime(ANCHOR.year, ANCHOR.month,
                                     ANCHOR.day, 20, 30))


def test_the_preposition_does_not_change_the_digital_answer():
    assert span("u 8:30") == span("8:30")
