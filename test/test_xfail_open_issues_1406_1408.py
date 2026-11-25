"""Strict xfails for open issues 1406 to 1408, the clock orders.

Each row asserts the value the issue expects. Strict mode turns the run red
when a fix lands, so the fix removes the mark from its rows. The controls at
the end must keep their reading.
"""
from datetime import datetime

import pytest

from chronologia import extract_candidates, extract_timespan

ANCHOR = datetime(2026, 11, 25, 10, 0)
URL = "https://github.com/TigreGotico/chronologia/issues/"


def xfail(issue):
    return pytest.mark.xfail(strict=True, reason=URL + str(issue))


def rows(issue, entries):
    return [pytest.param(*entry, marks=xfail(issue)) for entry in entries]


def clocks(text, lang):
    return [(c.span.start.datetime().strftime("%H:%M"), c.remainder)
            for c in extract_candidates(text, lang, ANCHOR)]


@pytest.mark.parametrize("lang,text,clock,wrong", rows(1406, [
    ("es", "tres y diez", "15:10", "10:03"),
    ("es", "las tres y diez", "15:10", "10:03"),
    ("it", "tre e dieci", "15:10", "10:03"),
    ("ro", "trei și zece", "15:10", "10:03"),
    ("ast", "tres y diez", "15:10", "10:03"),
    ("ast", "les tres y diez", "15:10", "10:03"),
]) + rows(1407, [
    ("pt-PT", "dez menos três", "21:57", "14:50"),
    ("pt-PT", "cinco menos dez", "16:50", "21:55"),
    ("pt-PT", "dez menos cinco", "21:55", "16:50"),
    ("es", "diez menos cinco", "21:55", "16:50"),
    ("es", "tres menos diez", "14:50", "21:57"),
    ("it", "dieci meno cinque", "21:55", "16:50"),
    ("ro", "zece fără cinci", "21:55", "16:50"),
    ("fr", "dix moins cinq", "21:55", "16:50"),
    ("ast", "diez menos cinco", "21:55", "16:50"),
]))
def test_the_hour_comes_before_the_past_or_minus_word(lang, text, clock, wrong):
    found = clocks(text, lang)
    assert found[0] == (clock, "")
    assert wrong not in [start for start, _ in found]


@pytest.mark.parametrize("lang,text,wrong", rows(1407, [
    ("pt-PT", "meia e três", "15:30"),
    ("pt-PT", "um quarto e as três", "15:15"),
]))
def test_a_fraction_before_e_names_no_clock(lang, text, wrong):
    assert wrong not in [start for start, _ in clocks(text, lang)]


@pytest.mark.parametrize("lang,text,start", rows(1408, [
    ("pt-PT", "dez para a meia-noite", datetime(2026, 11, 25, 23, 50)),
    ("pt-PT", "um quarto para a meia-noite", datetime(2026, 11, 25, 23, 45)),
    ("pt-PT", "dez para o meio-dia", datetime(2026, 11, 25, 11, 50)),
    ("pt-PT", "meio-dia menos dez", datetime(2026, 11, 25, 11, 50)),
    ("pt-PT", "dez para as três horas", datetime(2026, 11, 25, 14, 50)),
    ("pt-PT", "vinte para as oito horas da noite", datetime(2026, 11, 25, 19, 40)),
    ("pt-BR", "dez pras três", datetime(2026, 11, 25, 14, 50)),
    ("pt-BR", "cinco pra uma", datetime(2026, 11, 25, 12, 55)),
]))
def test_a_to_the_hour_clock_before_a_landmark_or_horas(lang, text, start):
    result = extract_timespan(text, lang, ANCHOR)
    assert result is not None
    assert result.span.start.datetime() == start
    assert result.remainder == ""


@pytest.mark.parametrize("lang,text,clock", [
    ("pt-PT", "três e dez", "15:10"),
    ("pt-PT", "dez para as três", "14:50"),
    ("pt-PT", "três menos dez", "14:50"),
    ("es", "las tres menos diez", "14:50"),
    ("it", "le tre e dieci", "15:10"),
    ("fr", "trois heures moins dix", "14:50"),
])
def test_control_clock_keeps_its_reading(lang, text, clock):
    assert clocks(text, lang)[0] == (clock, "")
