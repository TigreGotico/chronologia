# -*- coding: utf-8 -*-
"""R148: a sentence-final period must break mention clustering/range binding.

See ``test/nl_corpus_de/test_nl_r148_sentence_boundary.py`` for the full
mechanism -- Russian, like German, is an ``ordinal_dot`` locale, so the same
tokenizer-shape defect applies: a sentence-final period after a word is
never part of any token and used to leave an empty adjacency gap that fused
two mentions from two different sentences into one.
"""
from datetime import datetime

from chronologia.extract import extract_timespans
from chronologia.astrodate import AstroDate

ANCHOR = datetime(2026, 8, 10, 9, 0)


def mentions(text):
    return extract_timespans(text, "ru", ANCHOR)


# --------------------------------------------------------------------------
# The reported repro shape (meeting-with-clock + a "until <deadline>" clause
# in a separate sentence).
# --------------------------------------------------------------------------

def test_r148_ru_meeting_and_deadline_stay_two_mentions():
    ms = mentions(
        "Встреча состоится в следующую пятницу в 14:00. "
        "Пожалуйста, сдайте отчёты до конца месяца."
    )
    assert len(ms) == 2
    friday, deadline = ms
    assert friday.span.start == AstroDate(2026, 8, 14, 14, 0)
    assert friday.span.end == AstroDate(2026, 8, 14, 14, 1)
    assert deadline.span.start == AstroDate(2026, 8, 21, 16, 0)
    assert deadline.span.end == AstroDate(2026, 9, 1, 0, 0)


def test_r148_ru_monday_and_friday_stay_two_mentions_not_a_range():
    ms = mentions(
        "Мы встретимся в понедельник. Отчёт должен быть готов до пятницы."
    )
    assert len(ms) == 2
    monday, friday = ms
    assert monday.span.start == AstroDate(2026, 8, 17)
    assert monday.span.end == AstroDate(2026, 8, 18)
    assert friday.span.start == AstroDate(2026, 8, 14)
    assert friday.span.end == AstroDate(2026, 8, 15)


# --------------------------------------------------------------------------
# Other ru pairs: the reported failure mode DROPPED the second clause
# instead of fusing it -- both clauses must survive as independent mentions.
# --------------------------------------------------------------------------

def test_r148_ru_second_clause_survives_as_its_own_mention():
    ms = mentions("Мы встретимся в среду. Крайний срок в пятницу.")
    assert len(ms) == 2
    wed, fri = ms
    assert wed.span.start == AstroDate(2026, 8, 12)
    assert fri.span.start == AstroDate(2026, 8, 14)


def test_r148_ru_three_sentences_four_mentions():
    """'Сегодня' (today) itself names a mention alongside the three weekday
    references -- none of the four may be absorbed across a period."""
    ms = mentions(
        "Сегодня понедельник. Встреча состоится в среду. "
        "Крайний срок в пятницу."
    )
    assert len(ms) == 4
    assert [m.span.start.day for m in ms] == [10, 17, 12, 14]


# --------------------------------------------------------------------------
# Ordinal-dot controls -- must NOT be treated as a sentence boundary.
# --------------------------------------------------------------------------

def test_r148_ru_ordinal_dot_bare_date_unaffected():
    ms = mentions("Встреча назначена на 15. июня.")
    assert len(ms) == 1
    assert ms[0].span.start == AstroDate(2027, 6, 15)


def test_r148_ru_ordinal_dot_composition_unaffected():
    ms = mentions("Мы встретимся 3. марта в 9 часов.")
    assert len(ms) == 1
    assert ms[0].span.start == AstroDate(2027, 3, 3, 9, 0)


def test_r148_ru_sentence_ending_on_an_ordinal_date_still_splits():
    """Sentence 1 itself ends with an ordinal date ('15. июня.'); the period
    after that whole mention is a genuine sentence break and must still
    split off sentence 2's own mention."""
    ms = mentions(
        "Встреча назначена на 15. июня. "
        "После этого будет праздник в понедельник."
    )
    assert len(ms) == 2
    assert ms[0].span.start == AstroDate(2027, 6, 15)
    assert ms[1].span.start == AstroDate(2026, 8, 17)


def test_r148_ru_dotted_civil_date_unaffected():
    ms = mentions("Встреча состоится 15.06.2020.")
    assert len(ms) == 1
    assert ms[0].span.start == AstroDate(2020, 6, 15)
