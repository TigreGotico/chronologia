# -*- coding: utf-8 -*-
"""The article in front of a weekday written as a label on a date opens the
whole date, in every locale that has the article.

"el lunes 3 de julio" names one day, Monday 3 July 2017, and the article
belongs to that date: nothing of it is left over.  An article in front of a
noun that is not the date ("nos vemos el lunes ...": "nos vemos") is not
touched.  Anchor Tuesday 2017-06-27 13:04; 3 July 2017 is a Monday, by hand.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

ANCHOR = datetime(2017, 6, 27, 13, 4)


@pytest.mark.parametrize("lang,text,rest", [
    ("es", "el lunes 3 de julio", ""),
    ("es", "nos vemos el lunes 3 de julio", "nos vemos"),
    ("de", "der Montag, 3. Juli", ""),
    ("en", "the monday, july 3", ""),
    ("it", "il lunedì 3 luglio", ""),
    ("ca", "el dilluns 3 de juliol", ""),
    ("nl", "de maandag 3 juli", ""),
])
def test_the_article_goes_with_the_labelled_date(lang, text, rest):
    span, remainder = extract_timespan(text, lang, ANCHOR)
    assert (span.start, span.end) == (AstroDate(2017, 7, 3),
                                      AstroDate(2017, 7, 4))
    assert remainder == rest
