# -*- coding: utf-8 -*-
"""Bare "a" + hour-word must not fabricate a clock time (r186).

Spanish always names a clock hour WITH its agreeing article ("a la una",
"a las tres"): the bare preposition "a" carries no article of its own. "un"/
"una" ("a while", "an agreement") are the everyday indefinite article and
count word, and fold to the numeral 1 like any spelled number -- so "a un
rato" ("in a while") and "de aquí a un rato" ("a little while from now")
must NOT be misread as "a la una" (at one o'clock) just because a bare "a"
happens to sit in front of the folded "1". The same bare-"a" ambiguity
covers any non-temporal "a un"/"a una" object ("llegó a un acuerdo" == "he
reached an agreement"), independent of the specific noun that follows.

The genuine article-bearing forms ("a la una", "a las N") must keep
resolving: the article ("la"/"las"/"al") itself supplies the licensing
evidence a bare "a" lacks.
"""
from datetime import timedelta

from ._corpus import ANCHOR, ad, nomatch, start


def clk(h, mi, s=0):
    dt = ANCHOR.replace(hour=h, minute=mi, second=s, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    return ad(dt)


def test_bare_a_un_rato_no_clock():
    # "in a while" -- no clock, no article, "un" is the indefinite article.
    nomatch("en un rato")
    nomatch("dentro de un rato")
    nomatch("un rato")


def test_bare_a_un_rato_variants_no_clock():
    # the confusable construction the defect fabricated 01:00 from: a bare
    # "a" immediately followed by the folded "un" (=1), with no agreeing
    # article between them.
    nomatch("de aquí a un rato")
    nomatch("a un rato")
    nomatch("a un")


def test_bare_a_una_rato_no_clock():
    nomatch("de aquí a rato")


def test_bare_a_un_non_temporal_object_no_clock():
    # "a un"/"a una" heading an ordinary direct object is never a clock,
    # regardless of which noun follows.
    nomatch("llegó a un acuerdo")
    nomatch("se negó a una entrevista")
    nomatch("llegamos a un punto muerto")


def test_article_bearing_hour_still_resolves():
    # "la"/"las" themselves carry the article; only the bare "a" was ever
    # in question.
    assert start("a la una") == clk(1, 0)
    assert start("a las tres") == clk(3, 0)


def test_article_bearing_digit_hour_still_resolves():
    assert start("a las 3") == clk(3, 0)
    assert start("a las 11") == clk(11, 0)
