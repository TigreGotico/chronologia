"""An event whose length is the second number of a range of counts starts at
its day word.  The length reads the second count, so the first count stays
over; it is no year."""
from datetime import datetime, timedelta

import pytest

from chronologia.events import extract_event

_FRIDAY = datetime(2026, 1, 30, 10, 0)
_THURSDAY_29 = datetime(2026, 1, 29)


@pytest.mark.parametrize("lang, text, length", [
    ("pt", "durou entre dois mil e três mil horas ontem",
     timedelta(hours=3000)),
    ("pt", "durou desde dois mil até três mil horas ontem",
     timedelta(hours=3000)),
    ("pt", "durou entre dois mil e três mil dias ontem",
     timedelta(days=3000)),
    ("en", "it lasted between two thousand and three thousand hours "
     "yesterday", timedelta(hours=3000)),
])
def test_the_event_starts_at_the_day_word(lang, text, length):
    event = extract_event(text, lang, anchor=_FRIDAY)
    assert event.span.start == _THURSDAY_29
    assert event.span.end == _THURSDAY_29 + length
    assert event.duration == length


def test_a_year_after_a_length_stays_the_date():
    event = extract_event("durou três horas em dois mil e dez", "pt",
                          anchor=_FRIDAY)
    assert event.span.start == datetime(2010, 1, 1)
    assert event.duration == timedelta(hours=3)
