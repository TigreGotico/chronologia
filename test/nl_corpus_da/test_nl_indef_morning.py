# -*- coding: utf-8 -*-
"""Danish "morgen" is the morning, and "en morgen" names no date.

Bare "morgen" is the noun "morning" (en.wiktionary "morgen", Danish noun);
"tomorrow" is the adverb "i morgen" (en.wiktionary "i morgen").  Den Danske
Ordbog "morgen" gives "mandag/søndag morgen".  The article en ("a", "one")
before a daypart makes it indefinite; the sources are in
marker_indef_daypart.voc.  Anchor Tue 2017-06-27 13:04: the next Monday is
2017-07-03 and the next Sunday 2017-07-02; the morgen band is [05:00, 10:00).
"""
from datetime import datetime

import pytest

from ._corpus import ad, nomatch, parse, start_end

NO_DATE = [
    "En kold morgen i februar stod hun pludselig ved min dør med en kuffert.",
    "En kold morgen i november stod min bedstefar i døren med en kurv æbler.",
    "En morgen vågnede jeg ved, at fuglene sang uden for vinduet.",
    "Det var en grå morgen, og vi gik en lang tur langs stranden.",
    "En sen aften i maj sad vi i haven og hørte nattergalen.",
]


@pytest.mark.parametrize("text", NO_DATE)
def test_indefinite_daypart_names_no_date(text):
    nomatch(text)


BANDS = [
    ("Vi ses på mandag morgen ved stationen.",
     datetime(2017, 7, 3, 5), datetime(2017, 7, 3, 10)),
    ("Hun kommer søndag morgen med toget.",
     datetime(2017, 7, 2, 5), datetime(2017, 7, 2, 10)),
    ("Vi mødes i morgen aften hos min søster.",
     datetime(2017, 6, 28, 18), datetime(2017, 6, 29)),
]


@pytest.mark.parametrize("text,s,e", BANDS)
def test_morgen_after_a_day_is_its_morning(text, s, e):
    assert start_end(text) == (ad(s), ad(e))


def test_i_morgen_is_still_tomorrow():
    assert start_end("Jeg ringer til dig i morgen.") == (
        ad(datetime(2017, 6, 28)), ad(datetime(2017, 6, 29)))


def test_spoken_one_oclock_is_not_an_article():
    r = parse("Toget kører klokken et om natten.")
    assert r is not None and r[0].start == ad(datetime(2017, 6, 28, 1, 0))
