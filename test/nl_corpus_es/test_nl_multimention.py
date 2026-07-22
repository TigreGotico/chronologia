# -*- coding: utf-8 -*-
"""Multi-mention in Spanish: ``extract_timespans(text, "es", anchor)``."""
import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR

LANG = "es"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ("el viernes a las 3 o el lunes a mediodía", 2),
    ("mañana o la próxima semana", 2),
    ("ayer, hoy y mañana", 3),
    ("solo mañana", 1),
    ("nada temporal aquí", 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_mentions_in_order():
    ms = mentions("mañana o la próxima semana")
    assert [m.text for m in ms] == ["mañana", "próxima semana"]


def test_three_named_days_in_order():
    ms = mentions("ayer, hoy y mañana")
    assert [m.span.start.day for m in ms] == [26, 27, 28]
