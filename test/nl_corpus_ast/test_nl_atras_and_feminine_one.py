"""The postposed past marker "atrás" and the feminine hour "la una".

Asturian marks a past offset two ways: preposed "hai"/"fai" ("hai 2 meses")
and postposed "atrás" closing the counted length ("meses atrás"), the pair
Portuguese also lists.  One o'clock is feminine because "hora" is, so it
takes the feminine article and the feminine numeral: "a la una de la
madrugada".  Both are attested in running prose on ast.wikipedia.

Anchor 2017-06-27 13:04, a Tuesday; expected values computed by hand.
"""
from datetime import datetime

import pytest

from ._corpus import AstroDate, parse, start


@pytest.mark.parametrize("text,expected", [
    # 27 June minus 2 months
    ("2 meses atrás", datetime(2017, 4, 27, 13, 4)),
    ("2 meses atras", datetime(2017, 4, 27, 13, 4)),
    # 27 June minus 3 days
    ("3 díes atrás", datetime(2017, 6, 24, 13, 4)),
    # the preposed marker keeps its reading
    ("hai 2 meses", datetime(2017, 4, 27, 13, 4)),
])
def test_past_offset(text, expected):
    assert start(text) == AstroDate(expected.year, expected.month,
                                    expected.day, expected.hour,
                                    expected.minute)
    assert parse(text).remainder == ""


@pytest.mark.parametrize("text,expected", [
    # 13:04 is past one o'clock, so the next 01:00 is tomorrow's
    ("a la una", datetime(2017, 6, 28, 1, 0)),
    ("a la una y media", datetime(2017, 6, 28, 1, 30)),
    ("a la una de la nueche", datetime(2017, 6, 28, 1, 0)),
    # the masculine plural hour already worked and must keep working
    ("a les dos", datetime(2017, 6, 28, 2, 0)),
])
def test_feminine_hour(text, expected):
    assert start(text) == AstroDate(expected.year, expected.month,
                                    expected.day, expected.hour,
                                    expected.minute)
    assert parse(text).remainder == ""


def test_article_one_still_heads_a_scale_frame():
    """"un" before a scale word stays the article, not a separate count."""
    assert start("hai un añu") == AstroDate(2016, 6, 27, 13, 4)
    assert start("hai una selmana") == AstroDate(2017, 6, 20, 13, 4)
