# -*- coding: utf-8 -*-
"""Finnish case forms of a clock hour and of a weekday.

"puoli seitsemältä" is the half hour toward seven, 6:30, with the hour in the
ablative (Kotus, Kielitoimiston ohjepankki, "Ajanilmaukset: kellonajat
(merkintä ja taivutus)": the clock numerals inflect like any numeral).  The
translative "-ksi" of a weekday names the day it is for ("maanantaiksi" is for
Monday; Wiktionary, fi "maanantai", inflection table).  Expected values are
date arithmetic on the anchor, Tuesday 2017-06-27 13:04.
"""
from datetime import timedelta

import pytest

from ruling17 import next_twelve

from ._corpus import ANCHOR, ad, parse, start


@pytest.mark.parametrize("text", [
    "puoli seitsemältä",
    "herätä minut puoli seitsemältä",
])
def test_half_hour_with_an_ablative_hour(text):
    # said at 13:04, the next 6:30 is 18:30
    assert start(text) == ad(next_twelve(ANCHOR, 6, 30))
    assert parse(text).remainder == text.removesuffix("puoli seitsemältä").strip()


@pytest.mark.parametrize("form,index", [
    ("maanantaiksi", 0), ("tiistaiksi", 1), ("keskiviikoksi", 2),
    ("torstaiksi", 3), ("perjantaiksi", 4), ("lauantaiksi", 5),
    ("sunnuntaiksi", 6),
])
def test_translative_weekday(form, index):
    # a weekday said on that weekday is today (ruling 6)
    ahead = (index - ANCHOR.weekday()) % 7
    day = ANCHOR.replace(hour=0, minute=0, second=0, microsecond=0) \
        + timedelta(days=ahead)
    assert start(form) == ad(day)


def test_translative_weekday_with_a_clock():
    # the next Monday after Tuesday 2017-06-27 is 2017-07-03
    got = parse("aseta uusi herätys maanantaiksi kello seitsemän")
    assert got.span.start == ad(ANCHOR.replace(
        month=7, day=3, hour=7, minute=0))
    assert got.remainder == "aseta uusi herätys"
