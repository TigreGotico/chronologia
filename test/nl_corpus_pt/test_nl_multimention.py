# -*- coding: utf-8 -*-
"""Multi-mention in Portuguese: ``extract_timespans(text, "pt", anchor)``."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "pt"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ("sexta-feira às 3 ou segunda-feira ao meio-dia", 2),
    ("amanhã ou a próxima semana", 2),
    ("ontem, hoje e amanhã", 3),
    ("só amanhã", 1),
    ("nada temporal aqui", 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions("amanhã ou a próxima semana")
    assert [m.text for m in ms] == ["amanhã", "próxima semana"]


def test_three_named_days_in_order():
    ms = mentions("ontem, hoje e amanhã")
    assert [m.span.start.day for m in ms] == [26, 27, 28]
