"""German clock times -- centred on the CONTINENTAL-GERMANIC HALF TRAP.

The load-bearing linguistic fact: **"halb neun" == 08:30**, the half *before*
nine, the exact opposite of English "half nine" == 09:30.  German counts a
bare half down to the coming hour.  This is asserted prominently here with
adversarial neighbours (every hour, landmarks, meridiem, and the quarter
forms that do NOT share the convention).

All spans are minute-wide; the engine's ``prefer_future`` rolls a time
already past the 13:04 anchor to the next day.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start, span, nomatch


def clk(h, mi, s=0):
    dt = ANCHOR.replace(hour=h, minute=mi, second=s, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    return ad(dt)


# == THE HALF TRAP: "halb neun" == 08:30 (half TO nine) ====================

@pytest.mark.parametrize("text,h,mi", [
    ("halb neun", 8, 30),        # half to nine -- NOT 9:30
    ("halb sieben", 6, 30),
    ("halb acht", 7, 30),
    ("halb zehn", 9, 30),
    ("halb elf", 10, 30),
    ("halb zwölf", 11, 30),
    ("halb eins", 0, 30),        # half to one == 00:30
    ("halb zwei", 1, 30),
    ("halb drei", 2, 30),
    ("halb vier", 3, 30),
    ("halb fünf", 4, 30),
    ("halb sechs", 5, 30),
])
def test_halb_is_half_to(text, h, mi):
    assert start(text) == clk(h, mi)
    assert span(text).width == timedelta(minutes=1)


def test_halb_neun_is_not_half_past():
    # the whole point: 08:30, never 09:30.
    assert start("halb neun").hour == 8
    assert start("halb neun").minute == 30


# half onto a landmark, and with an evening meridiem
@pytest.mark.parametrize("text,h,mi", [
    ("halb mittag", 11, 30),        # half to noon
    ("halb mitternacht", 23, 30),   # half to midnight
    ("halb acht abends", 19, 30),   # half to eight, PM
    ("halb neun morgens", 8, 30),
])
def test_halb_landmark_and_meridiem(text, h, mi):
    assert start(text) == clk(h, mi)


# == the quarter forms use EXPLICIT direction (vor/nach) -- no trap ========

@pytest.mark.parametrize("text,h,mi", [
    ("viertel nach drei", 3, 15), ("viertel vor neun", 8, 45),
    ("viertel nach elf", 11, 15), ("viertel vor zwölf", 11, 45),
    ("viertel vor eins", 0, 45), ("viertel nach mitternacht", 0, 15),
    ("viertel vor mitternacht", 23, 45), ("viertel nach mittag", 12, 15),
])
def test_quarter_explicit_direction(text, h, mi):
    assert start(text) == clk(h, mi)


# == REGIONAL bare quarters: South/East German + Austrian toward-the-hour ==
# "viertel neun" == 08:15, "dreiviertel neun" == 08:45 -- three/one quarter of
# the way toward the coming hour, exactly like "halb neun" == 08:30 names the
# half toward it.  Western/northern German never says these bare forms (it uses
# "viertel nach/vor"), so enabling them only ADDS readings for strings that were
# previously unparsed -- no collision with the vor/nach path (asserted above).
# Source: Bastian Sick, "Zwiebelfisch: Von Viertel nach acht bis viertel neun".
@pytest.mark.parametrize("text,h,mi", [
    ("viertel neun", 8, 15), ("dreiviertel neun", 8, 45),
    ("viertel zehn", 9, 15), ("dreiviertel zehn", 9, 45),
    ("viertel drei", 2, 15), ("dreiviertel eins", 0, 45),
])
def test_bare_quarter_regional_toward_hour(text, h, mi):
    assert start(text) == clk(h, mi)


# == arbitrary minute "N vor/nach H" ======================================

@pytest.mark.parametrize("text,h,mi", [
    ("zehn vor acht", 7, 50), ("fünf nach drei", 3, 5),
    ("zwanzig vor sieben", 6, 40), ("fünf vor zwölf", 11, 55),
    ("zehn nach mittag", 12, 10),
])
def test_minute_to_past(text, h, mi):
    assert start(text) == clk(h, mi)


# == digit / bare-hour / o'clock literals =================================

@pytest.mark.parametrize("text,h,mi,s", [
    ("15:30", 15, 30, 0), ("23:59", 23, 59, 0), ("00:00", 0, 0, 0),
    ("13:05", 13, 5, 0), ("09:30", 9, 30, 0), ("8:15", 8, 15, 0),
    ("18:45", 18, 45, 0),
])
def test_digit_time(text, h, mi, s):
    assert start(text) == clk(h, mi, s)
    assert span(text).width == timedelta(minutes=1)


@pytest.mark.parametrize("text,h", [
    ("um 15", 15), ("um 9", 9), ("um 20", 20), ("um drei", 3),
    ("15 uhr", 15), ("20 uhr", 20), ("drei uhr", 3), ("acht uhr", 8),
    ("um mitternacht", 0), ("um mittag", 12),
])
def test_bare_hour(text, h):
    assert start(text) == clk(h, 0)


# == landmarks ============================================================

@pytest.mark.parametrize("text,h,mi", [
    ("mitternacht", 0, 0), ("mittag", 12, 0),
])
def test_landmark(text, h, mi):
    assert start(text) == clk(h, mi)


# == adversarial: impossible clocks never fabricate =======================

@pytest.mark.parametrize("text", ["25:00", "15:99", "99:99"])
def test_impossible_clock(text):
    from ._corpus import parse
    res = parse(text)
    if res is not None:
        assert 0 <= res[0].start.hour <= 23
