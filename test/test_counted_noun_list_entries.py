"""Entries of the counted-noun lists: en "person", ast "meses", pt "quartos".

A bare hour behind a clock preposition and directly before a noun that counts
people or things is a count, not a time ("at 5 persons").  The singular "person"
counts too ("at 1 person").  The ast word "meses" is a unit of time, not a
counted noun, so the list does not hold it, and "a les 3 meses" still gives no
clock.  The pt "quartos" are rooms, and "às 3 quartos" gives no clock.
Every anchor is Friday 2026-09-25 12:00.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2026, 9, 25, 12, 0)


@pytest.mark.parametrize("text,lang", [
    ("at 1 person", "en"),
    ("at 5 persons", "en"),
    ("a la 1 persona", "es"),
    ("às 3 quartos", "pt"),
])
def test_a_count_before_a_counted_noun_is_no_clock(text, lang):
    assert extract_timespan(text, lang, ANCHOR) is None


def test_the_ast_unit_meses_is_not_a_counted_noun():
    from chronologia.extract.loader import load_lang_spec
    assert "meses" not in load_lang_spec("ast").connectors.get(
        "counted_noun", frozenset())


def test_a_clock_before_a_person_word_in_another_sense_still_reads():
    found = extract_timespan("at 5 pm with the person", "en", ANCHOR)
    assert found.span.start.datetime() == datetime(2026, 9, 25, 17, 0)
