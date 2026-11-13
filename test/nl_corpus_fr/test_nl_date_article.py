# -*- coding: utf-8 -*-
"""The article that opens a dated weekday belongs to the date, fr.

"le 15 juin" reads whole through ``marker_defart.voc``; with the weekday
written as a label in front of the day ("le lundi 3 juillet") the article
opens the whole date and was left stranded.  Anchor 2017-06-27, a mardi,
13:04; 2017-07-03 is a Monday and 2017-07-02 a Sunday, by hand.
"""
import pytest

from ._corpus import parse, start_end, AstroDate


@pytest.mark.parametrize("text,ymd,rest", [
    ("le lundi 3 juillet", (2017, 7, 3), ""),
    ("le dimanche 2 juillet 2017", (2017, 7, 2), ""),
    ("rendez-vous le lundi 3 juillet", (2017, 7, 3), "rendez-vous"),
    ("le 15 juin", (2018, 6, 15), ""),
    # alone, "le jeudi" is also the habit; a habitual phrase reads as the
    # next such day, Thursday 29 June
    ("le jeudi", (2017, 6, 29), ""),
    ("le jeudi je travaille", (2017, 6, 29), "je travaille"),
])
def test_article_is_part_of_the_date(text, ymd, rest):
    s, e = start_end(text)
    assert s == AstroDate(*ymd)
    assert (e - s).days == 1
    assert parse(text)[1] == rest
