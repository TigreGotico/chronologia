"""Shared semantic-parity block: a Russian phrase must resolve to the *same*
span as its English staple, tying the Russian locale to the same hand-checked
reference spans rather than to the engine's own output.
"""
import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR


PAIRS = [
    ("сегодня", "today"),
    ("завтра", "tomorrow"),
    ("вчера", "yesterday"),
    ("послезавтра", "overmorrow"),
    ("позавчера", "ereyesterday"),
    ("через 3 дня", "in 3 days"),
    ("через 5 дней", "in 5 days"),
    ("через 2 недели", "in 2 weeks"),
    ("через 1 день", "in 1 day"),
    ("через 2 месяца", "in 2 months"),
    ("через 5 лет", "in 5 years"),
    ("через 3 часа", "in 3 hours"),
    ("через 15 минут", "in 15 minutes"),
    ("следующая пятница", "next friday"),
    ("следующий понедельник", "next monday"),
    ("прошлый вторник", "last tuesday"),
    ("этот четверг", "this thursday"),
    ("15:30", "15:30"),
    ("09:30", "09:30"),
    ("00:00", "00:00"),
    ("полдень", "noon"),
    ("полночь", "midnight"),
    ("2019", "2019"),
    ("1945", "1945"),
    ("2017-06-30", "2017-06-30"),
    ("с июня до августа", "from june to august"),
    ("с января до марта", "from january to march"),
    ("между июнем и сентябрём", "between june and september"),
    ("лето 2020", "summer 2020"),
    ("следующая зима", "next winter"),
]


@pytest.mark.parametrize("ru_text,en_text", PAIRS)
def test_span_parity(ru_text, en_text):
    ru = extract_timespan(ru_text, "ru", ANCHOR)
    en = extract_timespan(en_text, "en", ANCHOR)
    assert ru is not None, f"ru {ru_text!r} did not parse"
    assert en is not None, f"en {en_text!r} did not parse"
    assert ru[0].start == en[0].start, (ru_text, en_text)
    assert ru[0].end == en[0].end, (ru_text, en_text)
