# -*- coding: utf-8 -*-
"""Portuguese ordinals that read as a date when nothing marks them.

"segunda", "terça", "quarta", "quinta" and "sexta" are weekday names and
also feminine ordinals (Priberam s.v. "segunda", "terça"), so "a terça
parte", "quinta vez" and "a segunda maior cidade" name no day.  A
punctuation mark between the weekday and the next word keeps the weekday,
as a calendar note writes it.  "Último" also means final (Priberam s.v.
"último", 1), so "o último dia de escola" is the final day of school, not
yesterday.

Gold values are hand arithmetic from the anchor, Tuesday 2017-06-27 13:04:
the coming Wednesday is 2017-06-28 and the coming Thursday 2017-06-29; a
Tuesday said on that Tuesday is the anchor day (ruling 6); the last day of
June is 2017-06-30; the month before the anchor's is May 2017 (class 2b:
a named period is the calendar unit).
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ad, nomatch, start_end

#: Saturday 2026-10-17 12:00, the anchor of the ovos-date-parser pt grid.
SATURDAY = datetime(2026, 10, 17, 12, 0)


@pytest.mark.parametrize("anchor", [datetime(2017, 6, 27, 13, 4), SATURDAY])
@pytest.mark.parametrize("text", [
    "a terça parte",
    "a terca parte",
    "a terça parte do bolo",
    "quinta vez",
    "segunda vez",
    "sexta tentativa",
    "a segunda maior cidade",
    "a quinta melhor equipa",
    "a quarta pior nota",
    "o último dia de escola foi triste",
    "o último dia de aulas",
    "a última semana de férias",
    "o último mês de gravidez",
])
def test_ordinal_names_no_day(text, anchor):
    nomatch(text, anchor)


@pytest.mark.parametrize("text,day", [
    ("na quinta", datetime(2017, 6, 29)),
    ("na terça", datetime(2017, 6, 27)),
    ("terça-feira", datetime(2017, 6, 27)),
    ("quarta, aula de piano", datetime(2017, 6, 28)),
    ("quinta, segunda prestação do carro", datetime(2017, 6, 29)),
    ("o último dia do mês", datetime(2017, 6, 30)),
    ("o último dia de junho", datetime(2017, 6, 30)),
])
def test_day_reading_survives(text, day):
    assert start_end(text) == (ad(day), ad(day + timedelta(days=1)))


def test_last_period_without_of_is_the_previous_one():
    assert start_end("o último mês") == (ad(datetime(2017, 5, 1)),
                                         ad(datetime(2017, 6, 1)))
