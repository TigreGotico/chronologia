"""pt: the first number of a spelled range of time units is no year.

"durou entre dois mil e três mil horas ontem" is a stay of 2000 to 3000 hours
that ends or starts at the day word, so the event starts on "ontem".  A row
with no day word has no start.  Anchor: Friday 2026-01-30 10:00, so yesterday
is Thursday 29 January, "amanhã" is Saturday 31 January, "na segunda" is
Monday 2 February and "na sexta" is Friday 30 January.
"""
from datetime import date, datetime

import pytest

from chronologia import extract_event

ISSUE = "https://github.com/TigreGotico/chronologia/issues/1053"
ANCHOR = datetime(2026, 1, 30, 10, 0)

DAY_WORD = [
    ("pt", "durou entre dois mil e três mil horas ontem", date(2026, 1, 29)),
    ("pt", "a viagem durou entre dois mil e três mil minutos na segunda",
     date(2026, 2, 2)),
    ("pt", "entre dois mil e três mil segundos na sexta", date(2026, 1, 30)),
    ("pt", "durou entre dois mil e três mil dias ontem", date(2026, 1, 29)),
    ("pt", "entre dois mil e três mil dias a partir de amanhã",
     date(2026, 1, 31)),
    ("pt-BR", "durou entre dois mil e três mil horas ontem",
     date(2026, 1, 29)),
    ("pt", "durou desde dois mil até três mil horas ontem",
     date(2026, 1, 29)),
]

NO_DAY_WORD = [
    ("pt", "de dois mil a três mil dias"),
    ("pt", "desde dois mil até três mil dias"),
    ("pt-BR", "de dois mil a três mil horas"),
]


@pytest.mark.xfail(strict=True, reason=ISSUE)
@pytest.mark.parametrize("lang,text,day", DAY_WORD)
def test_the_event_starts_at_the_day_word(lang, text, day):
    event = extract_event(text, lang, anchor=ANCHOR)
    assert event.span.start.datetime().date() == day


@pytest.mark.xfail(strict=True, reason=ISSUE)
@pytest.mark.parametrize("lang,text", NO_DAY_WORD)
def test_a_range_of_lengths_with_no_day_word_has_no_start(lang, text):
    event = extract_event(text, lang, anchor=ANCHOR)
    assert event is None or event.span is None
