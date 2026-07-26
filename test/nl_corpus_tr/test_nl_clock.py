# -*- coding: utf-8 -*-
"""Clock readings in Turkish.

Spoken-clock construction grounded on Türk Dil Kurumu (TDK), Güncel Türkçe
Sözlük.  Turkish is HOUR-first, with the direction word carrying the sign and
the hour taking the case it agrees with:

* "buçuk" (=30) -- additive half-past on the named hour: "üç buçuk" = 3:30.
* "geçe" (past, additive) -- hour in the ACCUSATIVE: "saat dokuzu beş geçe"
  = 9:05, "üçü çeyrek geçe" = 3:15 (çeyrek=15).
* "kala" (to, subtractive from the named hour) -- hour in the DATIVE:
  "yediye çeyrek kala" = 6:45, "dörde yirmi kala" = 3:40 (20 min before 4:00).
"""
import pytest
from ._corpus import ANCHOR, nomatch, parse, start


@pytest.mark.parametrize("text,h,m", [
    ("15:30", 15, 30), ("09:00", 9, 0), ("23:59", 23, 59),
    ("06:15", 6, 15), ("00:00", 0, 0), ("12:00", 12, 0)])
def test_iso_clock(text, h, m):
    s = start(text)
    assert (s.hour, s.minute) == (h, m)


@pytest.mark.parametrize("text,h", [
    ("saat 3", 3), ("saat 9", 9), ("saat 7", 7), ("saat 11", 11),
    ("saat 8", 8)])
def test_at_hour(text, h):
    assert start(text).hour == h


# -- "buçuk": additive half past the named hour (TDK s.v. "buçuk") ----------
@pytest.mark.parametrize("text,h,m", [
    ("üç buçuk", 3, 30), ("yedi buçuk", 7, 30), ("on iki buçuk", 12, 30),
    ("dokuz buçuk", 9, 30)])
def test_bucuk_half_past(text, h, m):
    s = start(text)
    assert (s.hour, s.minute) == (h, m)


# The hour-introducing noun "saat" frames the whole clock reading, and TDK
# makes "buçuk" an adjective joined to the cardinal before it, so adding
# "saat" must not split the numeral and lose the thirty minutes.
@pytest.mark.parametrize("text,h,m", [
    ("saat üç buçuk", 3, 30),
    ("saat 3 buçuk", 3, 30),
    ("saat yedi buçuk", 7, 30),
    ("toplantı saat dokuz buçuk", 9, 30),
    ("saat on iki buçuk", 12, 30)])
def test_saat_bucuk_half_past(text, h, m):
    s = start(text)
    assert (s.hour, s.minute) == (h, m)
    assert parse(text).remainder in ("", "toplantı")


# The framing word alone still names the whole hour: "saat üç" is 3:00, and
# reading half past into it would be the mirror of the bug above.
@pytest.mark.parametrize("text,h", [
    ("saat üç", 3), ("saat dokuz", 9), ("saat on iki", 12)])
def test_saat_without_bucuk_is_the_whole_hour(text, h):
    s = start(text)
    assert (s.hour, s.minute) == (h, 0)


# -- "geçe": accusative hour + minute/fraction past (TDK s.v. "geçe") -------
@pytest.mark.parametrize("text,h,m", [
    ("dokuzu beş geçe", 9, 5),
    ("saat dokuzu beş geçe", 9, 5),
    ("üçü çeyrek geçe", 3, 15),
    ("üçü yirmi geçe", 3, 20),
    ("onu on geçe", 10, 10)])
def test_gece_past(text, h, m):
    s = start(text)
    assert (s.hour, s.minute) == (h, m)


# -- "kala": dative hour + minute/fraction to (TDK s.v. "kala") -------------
@pytest.mark.parametrize("text,h,m", [
    ("yediye çeyrek kala", 6, 45),
    ("dörde yirmi kala", 3, 40),
    ("saat üçe on kala", 2, 50)])
def test_kala_to(text, h, m):
    s = start(text)
    assert (s.hour, s.minute) == (h, m)


# "saat" frames the geçe/kala readings too, so it belongs to the time phrase
# and never survives into the leftover text.
@pytest.mark.parametrize("text", [
    "saat dokuzu beş geçe", "saat üçe on kala", "saat üçe çeyrek kala",
    "saat üç buçuk"])
def test_saat_is_part_of_the_clock_phrase(text):
    assert parse(text).remainder == ""


# -- the daypart adverbial, which Turkish puts before the time phrase -------
# "öğleden sonra saat üç" is the plain order; the postposed one is the marked
# variant.  Both must read the same afternoon hour, because dropping the
# marker is not a missed parse but a twelve-hour error.
@pytest.mark.parametrize("text,h", [
    ("öğleden sonra saat üç", 15),
    ("saat üç öğleden sonra", 15),
    ("akşam saat sekiz", 20),
    ("saat sekiz akşam", 20),
    ("öğleden sonra 3", 15),
    ("öğleden sonra saat 3", 15),
    ("sabah saat dokuz", 9),
    ("saat dokuz sabah", 9)])
def test_daypart_marker_either_side(text, h):
    s = start(text)
    assert (s.hour, s.minute) == (h, 0)
    assert parse(text).remainder == ""


@pytest.mark.parametrize("text,h,m", [
    ("öğleden sonra saat üç buçuk", 15, 30),
    ("saat üç buçuk öğleden sonra", 15, 30),
    ("akşam saat sekize on kala", 19, 50),
    ("öğleden sonra 15:30", 15, 30)])
def test_daypart_marker_over_a_full_reading(text, h, m):
    s = start(text)
    assert (s.hour, s.minute) == (h, m)


def test_bare_hour_without_daypart_stays_on_the_named_hour():
    # No marker, no twelve-hour shift: the hour is read exactly as named.
    s = start("saat üç")
    assert (s.hour, s.minute) == (3, 0)


# -- adversarial: bare direction/fraction words are not a time --------------
@pytest.mark.parametrize("text", [
    "buçuk", "geçe", "kala", "beş geçe",
    # the multi-word afternoon marker licenses a bare hour but names no time
    # by itself.  "sabah"/"akşam" are NOT here: they now name a CLDR daypart
    # band (see test_nl_daypart.py), so they parse -- just not as a clock time.
    "öğleden sonra", "öğleden sonra saat"])
def test_bare_clock_words_nomatch(text):
    nomatch(text)
