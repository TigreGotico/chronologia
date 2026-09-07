# -*- coding: utf-8 -*-
"""Kabyle spoken clock as a native speaker writes and says it.

Every sentence here is a form given by the native Kabyle speaker
@athmanemokraoui.  Where his judgement disagrees with a surface taken from
CLDR or from the Kabyle sentences on Tatoeba, his judgement is what the
locale follows and what this file pins.

Anchor 2017-06-27 13:04, prefer_future.  Expected instants are worked out
from the anchor, not read back from the parser: an hour already gone by today
lands on 06-28, one still ahead lands on 06-27.
"""
from datetime import datetime

import pytest

from ._corpus import nomatch, parse

A = datetime(2017, 6, 27, 13, 4)


def _at(text, want):
    r = parse(text, A)
    assert r is not None, "%r did not parse" % text
    s = r[0].start
    assert (s.year, s.month, s.day, s.hour, s.minute) == want, \
        "%r read %s, expected %s" % (text, (s.year, s.month, s.day, s.hour,
                                            s.minute), want)
    assert r[1] == "", "%r stranded %r" % (text, r[1])


# The subtractive connective is spelled "ɣir": standard INALCO Kabyle
# orthography puts no underdot on the liquid of this loan.  The underdotted
# "ɣiṛ" the Tatoeba sentences write stays readable, so both spellings must
# reach the same instant.
@pytest.mark.parametrize("text,want", [
    ("d lɛecṛa ɣir xemsa", (2017, 6, 28, 9, 55)),
    ("d lɛecṛa ɣiṛ xemsa", (2017, 6, 28, 9, 55)),
    ("d lɛecṛa ɣir ṛṛbeɛ", (2017, 6, 28, 9, 45)),
    ("d ttmanya ɣir ṛṛbeɛ", (2017, 6, 28, 7, 45)),
])
def test_minus_is_spelled_without_the_underdot(text, want):
    _at(text, want)


# Seven is "ssebɛa", always with the final -a.  The apocopated "ssebɛ" the
# Tatoeba sentence writes stays readable and must reach the same hour.
@pytest.mark.parametrize("text,want", [
    ("d ssebɛa u ṛṛbeɛ", (2017, 6, 28, 7, 15)),
    ("d ssebɛa ɣir ṛṛbeɛ", (2017, 6, 28, 6, 45)),
    ("ɣef ssebɛa d wezgen", (2017, 6, 28, 7, 30)),
    ("d ssebɛa n tṣebḥit", (2017, 6, 28, 7, 0)),
    ("d ssebɛ u ṛṛbeɛ", (2017, 6, 28, 7, 15)),
])
def test_seven_keeps_its_final_a(text, want):
    _at(text, want)


# Noon closes with the genitive "n uzal"; the bare "d ttnac uzal" is the
# informal elision of it and reads the same.
@pytest.mark.parametrize("text,want", [
    ("d ttnac n uzal", (2017, 6, 28, 12, 0)),
    ("d ttnac uzal", (2017, 6, 28, 12, 0)),
])
def test_noon_takes_the_genitive(text, want):
    _at(text, want)


# "gedged" closes a whole-hour reading exactly as "swaswa" does.
@pytest.mark.parametrize("text,want", [
    ("d lweḥda gedged", (2017, 6, 28, 1, 0)),
    ("d lweḥda swaswa", (2017, 6, 28, 1, 0)),
    ("d lɛecṛa gedged", (2017, 6, 28, 10, 0)),
])
def test_exactness_markers_close_the_hour(text, want):
    _at(text, want)


# The everyday morning frame is "n tṣebḥit", colloquially "n ṣṣbeḥ".  The
# formal CLDR surface "n tufat" keeps reading beside them.
@pytest.mark.parametrize("text,want", [
    ("d lɛecṛa n tṣebḥit", (2017, 6, 28, 10, 0)),
    ("d lɛecṛa n ṣṣbeḥ", (2017, 6, 28, 10, 0)),
    ("d lɛecṛa n tufat", (2017, 6, 28, 10, 0)),
])
def test_morning_frames(text, want):
    _at(text, want)


# Two is one cardinal with regional spellings; "ssaɛtin" is its clock form.
@pytest.mark.parametrize("text,want", [
    ("d jjuǧ ɣir ṛṛbeɛ", (2017, 6, 28, 1, 45)),
    ("d jjuj ɣir ṛṛbeɛ", (2017, 6, 28, 1, 45)),
    ("d zzuǧ ɣir ṛṛbeɛ", (2017, 6, 28, 1, 45)),
    ("ɣef jjuǧ n tmeddit", (2017, 6, 27, 14, 0)),
    ("d ssaɛtin n tmeddit", (2017, 6, 27, 14, 0)),
])
def test_two_spellings_and_the_clock_form(text, want):
    _at(text, want)


# A duration of two hours is "snat n sswayeɛ".  The clock hour "ssaɛtin" names
# two o'clock and nothing else, so it is never read as a length of time.
def test_two_hours_is_a_duration():
    from chronologia import extract_duration
    r = extract_duration("snat n sswayeɛ", "kab")
    assert r is not None, "'snat n sswayeɛ' did not parse as a duration"
    assert r[0].total_seconds() == 7200
    assert r[1] == "", "stranded %r" % (r[1],)


def test_the_clock_hour_two_is_not_a_duration():
    from chronologia import extract_duration
    assert extract_duration("ssaɛtin", "kab") is None


# "ɣir" means minus and is incomplete with nothing after it, in either
# spelling: no hour may be read out of a stranded subtractive connective.
@pytest.mark.parametrize("text", [
    "d lɛecṛa ɣir",
    "d lɛecṛa ɣiṛ",
    "d ssebɛa ɣir",
])
def test_a_bare_minus_refuses(text):
    nomatch(text, A)


# "wac" is "-something": "d lɛecṛa u wac" is roughly ten past ten, an
# APPROXIMATE time.  This library has no approximate-clock reading -- its
# fuzzy family narrows named periods (early/mid/late month, season, year), not
# the hour -- so the phrase is refused rather than given an invented span.
def test_approximate_hour_refuses():
    nomatch("d lɛecṛa u wac", A)
