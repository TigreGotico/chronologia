# -*- coding: utf-8 -*-
"""The definite article in front of a date.

French writes a date with an article as often as without: "le 15 juin". The
article had nowhere to go, so it landed in the leftover text.

It cannot go in the ordinary article slot. That vocabulary also carries the
contracted prepositions "du", "des", "au" and "aux", and a slot wide enough
to take those swallows the "du" of "la semaine du 20 juillet" -- the week OF
the twentieth, which is a different phrase and loses its week. The narrow
slot admits the plain article only.
"""
import pytest

from ._corpus import parse


@pytest.mark.parametrize("text,y,m,d", [
    ("le 15 juin", 2018, 6, 15),
    ("le 1er janvier", 2018, 1, 1),
    ("le 25 décembre", 2017, 12, 25),
    ("le 3 octobre 1990", 1990, 10, 3),
])
def test_the_article_belongs_to_the_date(text, y, m, d):
    got = parse(text)
    assert got is not None, text
    s = got[0].start
    assert (s.year, s.month, s.day) == (y, m, d)
    assert got[1] == ""


@pytest.mark.parametrize("text,y,m,d", [
    ("15 juin", 2018, 6, 15),
    ("1er janvier", 2018, 1, 1),
])
def test_the_date_without_an_article_is_unchanged(text, y, m, d):
    got = parse(text)
    s = got[0].start
    assert (s.year, s.month, s.day) == (y, m, d)
    assert got[1] == ""


def test_a_contracted_preposition_is_not_an_article():
    """"la semaine du 20 juillet" is the week of the twentieth.

    Reading "du" as an article leaves the week behind and answers the day.
    """
    got = parse("la semaine du 20 juillet")
    assert got is not None
    s = got[0].start
    assert (s.year, s.month, s.day) == (2017, 7, 17)
    assert got[0].end - s == __import__("datetime").timedelta(days=7)
    assert got[1] == ""
