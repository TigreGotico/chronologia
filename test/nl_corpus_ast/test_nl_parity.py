"""Shared semantic-parity block: an Asturian phrase must resolve to the *same*
span as its English staple.
"""
import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR


# (asturian, english) translation pairs that must land on the identical span
PAIRS = [
    ("güei", "today"),
    ("mañana", "tomorrow"),
    ("ayeri", "yesterday"),
    ("trasmañana", "overmorrow"),
    ("antayeri", "ereyesterday"),
    ("en 3 díes", "in 3 days"),
    ("en 5 díes", "in 5 days"),
    ("en 2 selmanes", "in 2 weeks"),
    ("en 1 día", "in 1 day"),
    ("en 2 meses", "in 2 months"),
    ("en 5 años", "in 5 years"),
    ("en 3 hores", "in 3 hours"),
    ("en 15 minutos", "in 15 minutes"),
    ("vienres que vien", "next friday"),
    ("llunes que vien", "next monday"),
    ("15:30", "15:30"),
    ("09:30", "09:30"),
    ("00:00", "00:00"),
    ("a mediudía", "noon"),
    ("a medianueche", "midnight"),
    ("2019", "2019"),
    ("1989", "1989"),
    ("2017-06-30", "2017-06-30"),
    ("de xunu a agostu", "from june to august"),
    ("de xineru a marzu", "from january to march"),
    ("ente xunu y setiembre", "between june and september"),
    ("branu 2020", "summer 2020"),
    ("44 enantes de cristu", "44 bc"),
    ('la selmana que vien', 'next week'),
    ("l'añu pasáu", 'last year'),
    ('esti fin de selmana', 'this weekend'),
]


@pytest.mark.parametrize("ast_text,en_text", PAIRS)
def test_span_parity(ast_text, en_text):
    ast = extract_timespan(ast_text, "ast", ANCHOR)
    en = extract_timespan(en_text, "en", ANCHOR)
    assert ast is not None, f"ast {ast_text!r} did not parse"
    assert en is not None, f"en {en_text!r} did not parse"
    assert ast[0].start == en[0].start, (ast_text, en_text)
    assert ast[0].end == en[0].end, (ast_text, en_text)
