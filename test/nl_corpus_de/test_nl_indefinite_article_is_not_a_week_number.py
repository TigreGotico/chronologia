"""An indefinite article before the week noun names a length, not week 1.

A German calendar week carries a definite article, an ordinal and the noun
("die 2. Woche", "der 20. Woche"), or the KW abbreviation, or the noun before
its number ("in Woche 2"). The indefinite article names a LENGTH instead:
"eine Woche" is one week long and "innerhalb einer Woche" is within one week.

The value probe reads every indefinite form as the number 1, which is right in
"in einer Stunde" and wrong before the week noun: the week-number order took
that 1 as its ordinal and answered calendar week 1, a date six months before
the anchor. Requiring the article on that order separates the two, because
every spoken week-number form carries an article or a prefix word.

de.wikipedia insource counts, length sense against week-number sense:
"eine Woche" 13302 and "einer Woche" 4371, against "die N. Woche" 24, "der N.
Woche" 297, "KW N" 1295 and "in Woche N" 415.
"""
import pytest

from ._corpus import nomatch, start

#: the length sense, which names no calendar week at all.
LENGTHS = ["einer woche", "eine woche", "innerhalb einer woche"]

#: the week-number forms a speaker actually uses, each kept.
WEEK_NUMBERS = [
    ("die 2. woche", "2017-01-09"),
    ("der 2. woche", "2017-01-09"),
    ("in der 20. woche", "2017-05-15"),
    ("die zweite woche", "2017-01-09"),
    ("kw 2", "2017-01-09"),
    ("kalenderwoche 2", "2017-01-09"),
    ("in woche 2", "2017-01-09"),
]

#: the counted offsets, which need the article read as its count.
OFFSETS = [
    ("vor einer woche", "2017-06-20"),
    ("in einer woche", "2017-07-04"),
]


@pytest.mark.parametrize("text", LENGTHS)
def test_an_indefinite_week_is_not_a_calendar_week(text):
    nomatch(text)


@pytest.mark.parametrize("text,expected", WEEK_NUMBERS)
def test_the_spoken_week_number_forms_are_kept(text, expected):
    assert str(start(text)).startswith(expected)


@pytest.mark.parametrize("text,expected", OFFSETS)
def test_the_counted_offsets_are_kept(text, expected):
    assert str(start(text)).startswith(expected)
