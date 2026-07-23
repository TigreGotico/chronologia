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
from ._corpus import ANCHOR, nomatch, start


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


# -- adversarial: bare direction/fraction words are not a time --------------
@pytest.mark.parametrize("text", ["buçuk", "geçe", "kala", "beş geçe"])
def test_bare_clock_words_nomatch(text):
    nomatch(text)
