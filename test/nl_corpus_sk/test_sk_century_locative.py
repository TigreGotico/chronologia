"""A century named after the "v" preposition, which puts the noun in the
locative.

"v 20. storočí" is the ordinary Slovak for "in the 20th century".
"scope_unit_century.voc" listed only the nominative "storočie", so the
locative "storočí" was not a century word at all: the ordinal-dotted 20 was
claimed as a clock hour and the century noun was stranded, and "in the 20th
century" came back as eight o'clock this evening.

The locative is spelled exactly like the genitive plural, the form Slovak
counts centuries with from five up, so behind the preposition the century
reading and a bare count of centuries are the same two words.  The ordinal
dot is what tells them apart, and it survives into the token's ``raw``: the
order requires it, so "v 20 storočí" and "v päť storočí" refuse while
"v 20. storočí" resolves.

Centuries are the engine's floor-division buckets, so the Nth century runs
from (N - 1) * 100 for a hundred years.
"""
from datetime import datetime

from ._corpus import ad, nomatch, parse, span


def _century(n):
    start = (n - 1) * 100
    return ad(datetime(start, 1, 1)), ad(datetime(start + 100, 1, 1))


def test_v_20_storoci_is_the_twentieth_century():
    r = parse("v 20. storočí")
    assert r is not None
    assert r[1] == ""
    assert (r[0].start, r[0].end) == _century(20)


def test_v_15_storoci_is_the_fifteenth_century():
    r = parse("v 15. storočí")
    assert r is not None
    assert r[1] == ""
    assert (r[0].start, r[0].end) == _century(15)


def test_locative_agrees_with_the_nominative():
    assert span("v 20. storočí") == span("20. storočie")


def test_a_counted_number_of_centuries_is_not_an_ordinal():
    # "storočí" is also the genitive plural, the form Slovak counts with from
    # five up ("päť storočí" = five centuries).  Without the ordinal dot there
    # is no ordinal here at all, and a duration is not a span the engine can
    # place, so it must refuse rather than answer with the Nth century.
    for text in ("päť storočí", "20 storočí", "desať storočí", "sedem storočí"):
        nomatch(text)


def test_the_preposition_does_not_make_a_count_an_ordinal():
    # the same count, behind the preposition the century order takes.  The
    # number fold collapses the digit "20", the spelled "päť" and the dotted
    # ordinal "20." to one numeric token, so an order that accepted any
    # cardinal here would answer "v 20 storočí" (twenty centuries) with the
    # twentieth century, "v päť storočí" with the fifth, and "v 100 storočí"
    # with a century that runs past the year 9900.
    for text in ("v 20 storočí", "vo 4 storočí", "v 100 storočí",
                 "v päť storočí", "v desať storočí"):
        nomatch(text)


def test_a_counted_bc_span_is_not_the_ad_century():
    # the worst of the family: read as an ordinal this answers the 20th
    # century AD and strands the era marker, missing by four millennia
    nomatch("20 storočí pred naším letopočtom")
