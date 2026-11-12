# -*- coding: utf-8 -*-
"""The nth weekday of a period, pt.

"segunda", "quarta", "quinta" and "sexta" are both feminine ordinals and
weekday names.  Priberam s.v. "segundo": "adjetivo numeral ... 1. Que ou o
que está logo depois do primeiro."  Between an article and a feminine weekday
name the word is the ordinal, because a weekday name does not take a second
weekday name after it.  A list of weekdays keeps the weekday reading.

"do mês que vem" and "do ano que vem" are the period after this one, with the
marker after the noun as in "o mês que vem".

Anchor 2017-06-27 13:04.  Counted on the calendar by hand: Tuesdays of 2026
fall on 6 and 13 January; Mondays of July 2017 on 3 and 10; Fridays of July
2017 on 7, 14, 21 and 28; Fridays of August 2017 on 4, 11, 18 and 25;
1 January 2018 is a Monday; the last Monday of July 2017 is the 31st.
"""
import pytest

from ._corpus import parse, start_end, AstroDate


@pytest.mark.parametrize("text,ymd", [
    ("a segunda terça-feira de 2026", (2026, 1, 13)),
    ("a segunda segunda-feira de julho", (2017, 7, 10)),
    ("a quarta sexta-feira de agosto", (2017, 8, 25)),
    ("a segunda sexta-feira do mês que vem", (2017, 7, 14)),
    ("a terceira sexta-feira do mês que vem", (2017, 7, 21)),
    ("a última sexta-feira do mês que vem", (2017, 7, 28)),
    ("o primeiro dia do mês que vem", (2017, 7, 1)),
    ("a primeira segunda-feira do ano que vem", (2018, 1, 1)),
    ("a última semana do mês que vem", (2017, 7, 31)),
])
def test_nth_weekday_of_period(text, ymd):
    s, _ = start_end(text)
    assert s == AstroDate(*ymd)
    assert parse(text)[1] == ""


def test_a_list_of_weekdays_keeps_the_weekday():
    s, e = start_end("na segunda, terça e quarta")
    assert s == AstroDate(2017, 7, 3)
    assert (e - s).days == 1
