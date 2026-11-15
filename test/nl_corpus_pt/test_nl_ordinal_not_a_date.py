# -*- coding: utf-8 -*-
"""Portuguese ordinals that read as a date when nothing marks them.

"segunda", "quarta", "quinta" and "sexta" are weekday names and also
feminine ordinals (Priberam s.v. "segunda"), so "quinta vez" and "a segunda
maior cidade" name no day.  "terça" is a fraction only before "parte"
(Priberam s.v. "terça", 2): "a terça parte" names no day, while "na terça
aula de piano" is Tuesday.  A punctuation mark between the weekday and the
next word keeps the weekday, as a calendar note writes it; a spaced or
doubled hyphen is such a mark.  "Último" also means final (Priberam s.v.
"último", 1), so "o último dia de escola" is the final day of school, not
yesterday.

Gold values are hand arithmetic from the anchor, Tuesday 2017-06-27 13:04:
the coming Wednesday is 2017-06-28, the coming Thursday 2017-06-29, the
coming Friday 2017-06-30 and the coming Monday 2017-07-03; a
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
    "a segunda menor cidade",
    "as duas terças partes",
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
    ("na terça aula de piano", datetime(2017, 6, 27)),
    ("terça sessão de fisioterapia", datetime(2017, 6, 27)),
    ("segunda - aula de piano", datetime(2017, 7, 3)),
    ("segunda -aula de piano", datetime(2017, 7, 3)),
    ("quinta -- aula de natação", datetime(2017, 6, 29)),
    ("sexta—visita ao médico", datetime(2017, 6, 30)),
])
def test_day_reading_survives(text, day):
    assert start_end(text) == (ad(day), ad(day + timedelta(days=1)))


def test_last_period_without_of_is_the_previous_one():
    assert start_end("o último mês") == (ad(datetime(2017, 5, 1)),
                                         ad(datetime(2017, 6, 1)))
