"""The spoken form of a pt-BR date, clock time and year.

Gold rows follow the pt-BR sources in chronologia/locale/pt/spoken.json:
Cunha & Cintra 2017 pp. 385-388 and FLiP DID 1881.
"""
import glob
import json
import os

import pytest

from chronologia import spoken
from chronologia.spoken import (UnsupportedForm, spoken_date, spoken_time,
                                spoken_year, writes)

DATES = [
    (dict(day=1, month=3, year=2026),
     "primeiro de março de dois mil e vinte e seis"),
    (dict(day=1, month=5), "primeiro de maio"),
    (dict(day=28, month=7, year=1983),
     "vinte e oito de julho de mil novecentos e oitenta e três"),
    (dict(day=16, month=7), "dezesseis de julho"),
    (dict(day=17, month=1, year=2019),
     "dezessete de janeiro de dois mil e dezenove"),
    (dict(day=7, month=9, year=2026, weekday=0),
     "segunda-feira sete de setembro de dois mil e vinte e seis"),
]

TIMES = [
    ((13, 30), {}, "treze e trinta"),
    ((16, 0), {}, "dezesseis horas"),
    ((19, 0), dict(style="units"), "dezenove horas"),
    ((0, 0), dict(style="units"), "zero hora"),
    ((6, 0), dict(style="units"), "seis horas"),
    ((14, 0), dict(clock="12h", period=True), "duas horas da tarde"),
    ((13, 30), dict(clock="12h", style="phrase", period=True),
     "uma e meia da tarde"),
    ((12, 30), dict(clock="12h", style="phrase"), "meio-dia e meio"),
    ((12, 10), dict(clock="12h", style="phrase"), "meio-dia e dez"),
    ((0, 30), dict(clock="12h", style="phrase"), "meia-noite e meia"),
    ((12, 0), dict(clock="12h", period=True), "meio-dia"),
    ((0, 0), dict(clock="12h", period=True), "meia-noite"),
]


@pytest.mark.parametrize("fields,gold", DATES)
def test_date(fields, gold):
    assert spoken_date("pt-BR", **fields) == gold


@pytest.mark.parametrize("clock,kwargs,gold", TIMES)
def test_time(clock, kwargs, gold):
    assert spoken_time("pt-BR", *clock, **kwargs) == gold


def test_year():
    assert spoken_year("pt-BR", 2026) == "dois mil e vinte e seis"
    assert spoken_year("pt-BR-x-carioca", 2016) == "dois mil e dezesseis"


def test_pt_pt_keeps_its_forms():
    assert spoken_date("pt-PT", day=16, month=7) == "dezasseis de julho"
    assert spoken_time("pt-PT", 0, 0, style="units") == "zero horas"
    assert spoken_time("pt-PT", 12, 30, clock="12h",
                       style="phrase") == "meio-dia e meia"


def test_unsourced_phrase_hour_is_refused():
    with pytest.raises(UnsupportedForm):
        spoken_time("pt-BR", 3, 0, clock="12h", style="phrase")


def _shipped_tags():
    pattern = os.path.join(os.path.dirname(spoken.__file__), "locale", "*",
                           "spoken.json")
    for path in glob.glob(pattern):
        with open(path, encoding="utf-8") as fh:
            yield from json.load(fh)["tags"]


def _works(writer, *args, **kwargs):
    try:
        writer(*args, **kwargs)
    except UnsupportedForm:
        return False
    return True


@pytest.mark.parametrize("tag", sorted(_shipped_tags()) + ["pt-AO", "xx"])
def test_writes_matches_the_writers(tag):
    real = (_works(spoken_date, tag, day=1, month=3, year=2026)
            and _works(spoken_time, tag, 13, 30)
            and _works(spoken_year, tag, 2026))
    assert writes(tag) is real
    assert writes(tag) is (tag not in ("pt-AO", "xx"))
