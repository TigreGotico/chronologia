"""Finnish "N yli/vaille HOUR" clock, the past/to construction.

``yli`` counts minutes PAST the named hour and ``vaille`` counts minutes
LEFT until it, so "varttia yli kaksi" is 2.15 and "varttia vaille kaksi"
is 1.45.  Both directions are pinned here because a reversed clock reads
plausibly in every sentence it appears in.

Kotimaisten kielten keskus (Kotus), Kielitoimiston ohjepankki,
"Ajanilmaukset: kellonajat (viisi vaille tai vailla, viittä vaille tai
vailla)": the minute word stands in the nominative or the partitive
("kymmenen yli" ~ "kymmentä yli", "kaksikymmentä vaille" ~ "kahtakymmentä
vaille") and the hour in the nominative or the genitive ("yli viisi" ~
"yli viiden") -- all four combinations are equal in the standard language.
Wiktionary (en), "yli" and "vaille": "Kello on vartin yli kuusi" = quarter
past six, "Kello on viittä vaille kuusi" = five to six; ``vaille`` governs
the partitive only, ``yli`` the genitive or the partitive.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, nomatch, parse


def _next_time(h, mi):
    cand = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    return ad(cand)


def _assert_clock(text, h, mi):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    span, rem = r
    assert span.start == _next_time(h, mi)
    assert span.end == _next_time(h, mi) + timedelta(minutes=1)
    assert rem == ""


@pytest.mark.parametrize("text,h,mi", [
    ("varttia yli kaksi", 2, 15),
    ("vartin yli kaksi", 2, 15),
    ("varttia yli seitsemän", 7, 15),
    ("kymmenen yli kaksi", 2, 10),
    ("kymmentä yli kaksi", 2, 10),
    ("viisitoista yli kolme", 3, 15),
    ("viittätoista yli kolme", 3, 15),
    ("viisi yli kuusi", 6, 5),
    ("viittä yli kuusi", 6, 5),
    ("varttia yli kahden", 2, 15),
])
def test_yli_is_past_the_hour(text, h, mi):
    _assert_clock(text, h, mi)


@pytest.mark.parametrize("text,h,mi", [
    ("varttia vaille kaksi", 1, 45),
    ("kymmentä vaille kaksi", 1, 50),
    ("kymmenen vaille kaksi", 1, 50),
    ("viittä vaille kuusi", 5, 55),
    ("kaksikymmentä vaille kaksi", 1, 40),
    ("kahtakymmentä vaille kaksi", 1, 40),
    ("kahtakymmentä vaille kahdeksan", 7, 40),
    ("viittä vaille viiden", 4, 55),
    ("varttia vailla kaksi", 1, 45),
])
def test_vaille_is_before_the_hour(text, h, mi):
    _assert_clock(text, h, mi)


def test_the_two_directions_do_not_collapse():
    """The same minute word and the same hour must land 30 minutes apart."""
    past, _ = parse("varttia yli kaksi")
    to, _ = parse("varttia vaille kaksi")
    assert past.start - to.start == timedelta(minutes=30)
    assert past.start == _next_time(2, 15)
    assert to.start == _next_time(1, 45)


def test_yli_without_an_hour_is_not_a_clock():
    nomatch("varttia yli")
