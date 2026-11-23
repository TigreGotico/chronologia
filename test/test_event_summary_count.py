# -*- coding: utf-8 -*-
"""A count word that opens a longer number stays in the event summary.

The summary drops a stranded article or preposition at its edges, and "un",
"um" and "one" are on that list as the indefinite article. In "un millón de
euros" the word is the count of the scale noun: numtag reads "un millón" as
one number, 1000000, so the summary keeps it. Anchor Tuesday 2017-06-27 13:04;
"mañana", "amanhã", "domani" and "tomorrow" are 28 June, and "dentro de 2
semanas" is 11 July, read off the calendar by hand.
"""
from datetime import datetime

import pytest

from chronologia.events import extract_event

ANCHOR = datetime(2017, 6, 27, 13, 4)


@pytest.mark.parametrize("lang,text,summary,day", [
    ("es", "un millón de euros mañana", "un millón de euros", datetime(2017, 6, 28)),
    ("es", "un millón de razones dentro de 2 semanas", "un millón de razones", datetime(2017, 7, 11)),
    ("ca", "un milió de raons dintre de 2 setmanes", "un milió de raons", datetime(2017, 7, 11)),
    ("gl", "un millón de razóns dentro de 2 semanas", "un millón de razóns", datetime(2017, 7, 11)),
    ("es", "pagar un millón de pesos mañana", "pagar un millón de pesos", datetime(2017, 6, 28)),
    ("es", "un mil euros mañana", "un mil euros", datetime(2017, 6, 28)),
    ("pt", "um milhão de euros amanhã", "um milhão de euros", datetime(2017, 6, 28)),
    ("it", "un milione di euro domani", "un milione di euro", datetime(2017, 6, 28)),
    ("en", "one million euros tomorrow", "one million euros", datetime(2017, 6, 28)),
    ("en", "a million euros tomorrow", "a million euros", datetime(2017, 6, 28)),
])
def test_the_count_of_a_scale_word_stays(lang, text, summary, day):
    event = extract_event(text, lang, anchor=ANCHOR)
    assert event.summary == summary
    assert event.span.start.datetime().date() == day.date()


@pytest.mark.parametrize("lang,text,summary", [
    # an article that opens no number still leaves the edge
    ("en", "the meeting tomorrow", "meeting"),
    ("es", "la reunión mañana", "reunión"),
    ("pt", "a reunião amanhã", "reunião"),
])
def test_an_article_alone_still_leaves(lang, text, summary):
    assert extract_event(text, lang, anchor=ANCHOR).summary == summary
