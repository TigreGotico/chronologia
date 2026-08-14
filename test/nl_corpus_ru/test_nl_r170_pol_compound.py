# -*- coding: utf-8 -*-
"""R170 (ru): compound duration words with the "пол" ("half") and "полтора"/
"полторы" ("one and a half") prefixes silently refused to parse.

"полчаса" (half an hour) is the standard fused spelling of the already-working
space-separated "пол часа" -- the tokenizer read it as one unknown word and
the whole phrase stranded. "полтора часа"/"полтора дня" (1.5 hours/days) and
"полторы минуты" (1.5 minutes, feminine agreement) had no quantifier surface
at all, unlike the already-working Polish sibling "półtorej godziny" (#264).
"""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "ru"


def test_fused_pol_chasa_hour_idiom():
    got = extract_duration("полчаса", LANG)
    assert got is not None
    assert got.duration == timedelta(minutes=30)
    assert got.remainder.strip() == ""


def test_fused_pol_minuty_idiom():
    got = extract_duration("полминуты", LANG)
    assert got is not None
    assert got.duration == timedelta(seconds=30)
    assert got.remainder.strip() == ""


def test_fused_pol_dnya_idiom():
    got = extract_duration("полдня", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=12)
    assert got.remainder.strip() == ""


def test_fused_pol_nedeli_idiom():
    got = extract_duration("полнедели", LANG)
    assert got is not None
    assert got.duration == timedelta(days=3, hours=12)
    assert got.remainder.strip() == ""


def test_space_separated_pol_chasa_control_unaffected():
    got = extract_duration("пол часа", LANG)
    assert got is not None
    assert got.duration == timedelta(minutes=30)
    assert got.remainder.strip() == ""


def test_poltora_chasa_one_and_a_half_hours():
    got = extract_duration("полтора часа", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=1, minutes=30)
    assert got.remainder.strip() == ""


def test_poltora_dnya_one_and_a_half_days():
    got = extract_duration("полтора дня", LANG)
    assert got is not None
    assert got.duration == timedelta(days=1, hours=12)
    assert got.remainder.strip() == ""


def test_poltory_minuty_feminine_agreement():
    got = extract_duration("полторы минуты", LANG)
    assert got is not None
    assert got.duration == timedelta(minutes=1, seconds=30)
    assert got.remainder.strip() == ""


def test_idiom_embedded_in_sentence():
    got = extract_duration("встреча длится полтора часа сегодня", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=1, minutes=30)
    assert "встреча" in got.remainder
    assert "сегодня" in got.remainder


def test_control_3_chasa_unaffected():
    got = extract_duration("3 часа", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=3)
    assert got.remainder.strip() == ""


def test_control_30_minut_unaffected():
    got = extract_duration("30 минут", LANG)
    assert got is not None
    assert got.duration == timedelta(minutes=30)
    assert got.remainder.strip() == ""


def test_control_compound_2_chasa_30_minut_unaffected():
    got = extract_duration("2 часа 30 минут", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=2, minutes=30)
    assert got.remainder.strip() == ""


def test_bare_chas_not_supported():
    # "час" carries no article the way English "an hour" does, and the same
    # bare noun heads the clock idiom "в час" (at one o'clock); supporting a
    # bare implicit-one duration was left unimplemented rather than risk that
    # collision -- see PR body / commit message for the decision record.
    assert extract_duration("час", LANG) is None


@pytest.mark.parametrize("text", ["2 июня", "тут нет времени"])
def test_not_a_duration_control(text):
    assert extract_duration(text, LANG) is None
