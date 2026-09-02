"""The "last" determiner in front of a neuter season noun.

Croatian season nouns are neuter ("ljeto", "proljeće"), so "last summer"
is "prošlo ljeto" -- the neuter nominative/accusative of the determiner.
"marker_last.voc" listed only the masculine and feminine paradigms, so the
determiner could not bind: the season resolved on its own and the stranded
"prošlo" came back in the remainder, turning "last summer" into *this*
summer with no signal that anything had been dropped.

Meteorological seasons: spring is 1 March .. 1 June, summer 1 June ..
1 September.  The anchor (27 June) sits inside summer, so the previous
summer is the year before and the previous spring is earlier the same year.
"""
from datetime import datetime

from ._corpus import ANCHOR, ad, parse, span


def test_proslo_ljeto_is_the_previous_summer():
    r = parse("prošlo ljeto")
    assert r is not None
    assert r[1] == ""
    assert r[0].start == ad(datetime(ANCHOR.year - 1, 6, 1))
    assert r[0].end == ad(datetime(ANCHOR.year - 1, 9, 1))


def test_prethodno_ljeto_is_the_previous_summer():
    r = parse("prethodno ljeto")
    assert r is not None
    assert r[1] == ""
    assert r[0] == span("prošlo ljeto")


def test_proslo_proljece_is_the_spring_just_gone():
    r = parse("prošlo proljeće")
    assert r is not None
    assert r[1] == ""
    assert r[0].start == ad(datetime(ANCHOR.year, 3, 1))
    assert r[0].end == ad(datetime(ANCHOR.year, 6, 1))


def test_last_summer_is_not_this_summer():
    """The defect exactly: the wrong year, with the determiner stranded."""
    assert span("prošlo ljeto") != span("ljeto")


def test_next_summer_still_works():
    r = parse("sljedeće ljeto")
    assert r is not None
    assert r[1] == ""
    assert r[0].start == ad(datetime(ANCHOR.year + 1, 6, 1))
    assert r[0].end == ad(datetime(ANCHOR.year + 1, 9, 1))
