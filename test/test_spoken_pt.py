"""The spoken form of a pt-PT date, clock time and year.

The gold rows are the pt-PT rows of ovos-date-parser test/test_spoken_pt.py,
copied by hand. Their sources are in chronologia/locale/pt/spoken.json.
"""
import pytest

from chronologia.spoken import (UnsupportedForm, revision, spoken_date,
                                spoken_time, spoken_year, writes)

DATES = [
    ("pt-PT", dict(day=12, month=3, year=2024),
     "doze de março de dois mil e vinte e quatro"),
    ("pt-PT", dict(day=1, month=3, year=2024),
     "primeiro de março de dois mil e vinte e quatro"),
    ("pt-PT", dict(day=19, month=12, year=2016),
     "dezanove de dezembro de dois mil e dezasseis"),
    ("pt", dict(day=16, month=7), "dezasseis de julho"),
    ("pt-PT", dict(day=1), "primeiro"),
    ("pt-PT", dict(day=3), "três"),
    ("pt-PT", dict(month=3), "março"),
    ("pt-PT", dict(year=1999), "mil novecentos e noventa e nove"),
    ("pt-PT", dict(month=3, year=2024), "março de dois mil e vinte e quatro"),
    ("pt-PT", dict(day=29, month=2), "vinte e nove de fevereiro"),
    ("pt-PT", dict(day=12, month=3, year=2024, weekday=1),
     "terça-feira doze de março de dois mil e vinte e quatro"),
    ("pt-PT-x-lisbon", dict(day=2, month=5), "dois de maio"),
]

TIMES = [
    ((14, 30), {}, "catorze e trinta"),
    ((21, 0), {}, "vinte e uma horas"),
    ((1, 0), {}, "uma hora"),
    ((0, 0), {}, "zero horas"),
    ((9, 5), {}, "nove e cinco"),
    ((14, 30), dict(style="units"), "catorze horas e trinta minutos"),
    ((19, 30), dict(style="units"), "dezanove horas e trinta minutos"),
    ((1, 1), dict(style="units"), "uma hora e um minuto"),
    ((21, 0), dict(style="units"), "vinte e uma horas"),
    ((20, 30, 24), dict(style="units"),
     "vinte horas trinta minutos e vinte e quatro segundos"),
    ((20, 0, 1), dict(style="units"), "vinte horas e um segundo"),
    ((14, 30), dict(clock="12h"), "duas e trinta"),
    ((14, 0), dict(clock="12h", period=True), "duas horas da tarde"),
    ((0, 30), dict(clock="12h"), "doze e trinta"),
    ((0, 30), dict(clock="12h", period=True), "doze e trinta da madrugada"),
    ((0, 0), dict(clock="12h", period=True), "meia-noite"),
    ((12, 0), dict(clock="12h", period=True), "meio-dia"),
    ((12, 0), dict(clock="12h"), "doze horas"),
    ((14, 30), dict(style="phrase", clock="12h", period=True),
     "duas e meia da tarde"),
    ((18, 45), dict(style="phrase", clock="12h", period=True),
     "sete menos um quarto da tarde"),
]


@pytest.mark.parametrize("tag,fields,expected", DATES)
def test_dates(tag, fields, expected):
    assert spoken_date(tag, **fields) == expected


@pytest.mark.parametrize("clock,options,expected", TIMES)
def test_times(clock, options, expected):
    assert spoken_time("pt-PT", *clock, **options) == expected


@pytest.mark.parametrize("year,expected", [
    (1, "um"), (2024, "dois mil e vinte e quatro"),
    (9999, "nove mil novecentos e noventa e nove")])
def test_years(year, expected):
    assert spoken_year("pt-PT", year) == expected


@pytest.mark.parametrize("fields", [
    dict(day=31, month=2), dict(day=29, month=2, year=2023), dict(day=32),
    dict(month=13), dict(day=12, year=2024),
    dict(day=12, month=3, year=2024, weekday=0),
    dict(month=3, year=2024, weekday=4), dict(day=12, weekday=7),
    dict(day=12, weekday=-1), {}])
def test_impossible_dates(fields):
    with pytest.raises(ValueError):
        spoken_date("pt-PT", **fields)


@pytest.mark.parametrize("clock,options", [
    ((24, 0), {}), ((12, 60), {}), ((12, 0, 60), dict(style="units")),
    ((12, 0), dict(style="spoken")), ((12, 0), dict(clock="13h")),
    ((14, 0), dict(period=True))])
def test_bad_times(clock, options):
    with pytest.raises(ValueError):
        spoken_time("pt-PT", *clock, **options)


@pytest.mark.parametrize("call", [
    lambda: spoken_time("pt-PT", 14, 30, 5),
    lambda: spoken_time("pt-PT", 14, 30, style="phrase"),
    lambda: spoken_time("pt-PT", 14, 30, 5, style="phrase", clock="12h"),
    lambda: spoken_time("pt-PT", 14, 30, case="genitive"),
    lambda: spoken_date("pt-PT", day=1, month=5, case="genitive"),
    lambda: spoken_year("pt-PT", 2024, ordinal=True),
    lambda: spoken_date("hi", day=1, month=5),
    lambda: spoken_date("pt-AO", day=1, month=5),
])
def test_unsupported(call):
    with pytest.raises(UnsupportedForm):
        call()


def test_unsupported_is_a_short_value_error():
    with pytest.raises(ValueError, match=r"^hi: no date reading for this language$"):
        spoken_date("hi", day=1)


@pytest.mark.parametrize("year", [0, -5, 10000])
def test_year_range(year):
    with pytest.raises(ValueError):
        spoken_year("pt-PT", year)


@pytest.mark.parametrize("tag,expected", [
    ("pt-PT", True), ("pt", True), ("pt_PT", True), ("pt-PT-x-lisbon", True),
    ("pt-BR", True), ("pt-AO", False), ("en-US", False), ("it", False)])
def test_writes(tag, expected):
    assert writes(tag) is expected


def test_revision_is_the_version():
    from chronologia.version import VERSION_STR
    assert revision() == VERSION_STR
