# -*- coding: utf-8 -*-
"""The century named by an ordinal.

Russian writes the ordinal spelled out ("второй век", "второе
столетие") or as a bare digit run -- Russian does not mark ordinals with
a dot.  Both the native "век" and the calque "столетие" name the
century.  The noun stays in the nominative singular; a count puts it in
the genitive ("пять веков", "два века"), so a count names a quantity,
never a period, and must refuse.

Gold is arithmetic, not the parser: the Nth century opens in year
(N-1)*100 and is 100 years wide, half-open.
"""
import pytest

from ._corpus import nomatch, parse, span


@pytest.mark.parametrize("text,n", [
    ("20 век", 20),
    ("второй век", 2),
    ("второе столетие", 2),
])
def test_the_nth_century_is_a_hundred_years(text, n):
    s = span(text)
    assert (s.start.year, s.end.year) == ((n - 1) * 100, n * 100)
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text", ["пять веков", "два века", "пять столетий", "два столетия"])
def test_a_count_of_centuries_names_none_of_them(text):
    nomatch(text)


@pytest.mark.parametrize("text,n", [
    ("в 20 веке", 20),
    ("в 20 столетии", 20),
    ("во 2 веке", 2),
])
def test_in_the_nth_century_takes_the_prepositional(text, n):
    """The ordinary way to place an event in a century.

    "в"/"во" govern the prepositional case, so the noun is
    "веке"/"столетии".  Both forms were on record as unit
    surfaces but not as singular ones, so each counted as a plural -- a bare
    count -- and the reading was thrown away, leaving "в 20" to be read as
    eight o'clock with the century noun stranded.
    """
    s = span(text)
    assert (s.start.year, s.end.year) == ((n - 1) * 100, n * 100)
    assert parse(text)[1] == ""
