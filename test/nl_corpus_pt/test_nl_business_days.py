"""Dias úteis: "em N dias úteis", "o próximo dia útil", "N dias úteis depois
do natal".

Um dia útil é um dia de semana que não é fim de semana nem feriado da
``jurisdiction``.  Sem jurisdição a contagem ignora feriados (só fim de semana).

Âncora: quarta-feira 2026-12-23.  Feriados públicos PT no intervalo:
sex 2026-12-25 (Natal), sex 2027-01-01 (Ano Novo).

PT (salta Natal + Ano Novo), a partir de qua 12-23:
    qui24(1) seg28(2) ter29(3) qua30(4) qui31(5) seg Jan4(6)
Sem jurisdição (só dias de semana):
    qui24(1) sex25(2) seg28(3) qua30(5) qui31(6)
"""
from datetime import date, datetime, timedelta

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

import pytest

ANCHOR = datetime(2026, 12, 23, 9, 0)   # quarta-feira


def start(text, jurisdiction=None):
    r = extract_timespan(text, "pt", ANCHOR, jurisdiction=jurisdiction)
    assert r is not None, f"{text!r} não resolveu"
    return r[0].start


def nomatch(text, jurisdiction=None):
    r = extract_timespan(text, "pt", ANCHOR, jurisdiction=jurisdiction)
    assert r is None, f"{text!r} resolveu inesperadamente para {r!r}"


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    ("em 1 dia útil", date(2026, 12, 24)),
    ("em 2 dias úteis", date(2026, 12, 28)),   # salta sex Natal + fim de semana
    ("em 3 dias úteis", date(2026, 12, 29)),
    ("em 4 dias úteis", date(2026, 12, 30)),
    ("em 5 dias úteis", date(2026, 12, 31)),
    ("em 6 dias úteis", date(2027, 1, 4)),      # salta Ano Novo + fim de semana
    ("4 dias úteis", date(2026, 12, 30)),
])
def test_conta_pt(text, expected):
    assert start(text, "PT") == _ad(expected)


@pytest.mark.parametrize("text,expected", [
    ("em 1 dia útil", date(2026, 12, 24)),
    ("em 2 dias úteis", date(2026, 12, 25)),   # Natal conta (cego a feriados)
    ("em 3 dias úteis", date(2026, 12, 28)),
    ("em 5 dias úteis", date(2026, 12, 30)),
])
def test_conta_cego_feriados(text, expected):
    assert start(text) == _ad(expected)


def test_proximo_dia_util():
    assert start("o próximo dia útil", "PT") == _ad(date(2026, 12, 24))


@pytest.mark.parametrize("text,expected,juris", [
    ("3 dias úteis depois do natal", date(2026, 12, 30), "PT"),
    ("3 dias úteis depois do natal", date(2026, 12, 30), None),
    ("2 dias úteis antes do natal", date(2026, 12, 23), "PT"),
])
def test_composicao(text, expected, juris):
    assert start(text, juris) == _ad(expected)


def test_largura_de_um_dia():
    r = extract_timespan("em 3 dias úteis", "pt", ANCHOR, jurisdiction="PT")
    assert r[0].width == timedelta(days=1)


@pytest.mark.parametrize("text", ["como sempre", "tudo normal"])
def test_negativos(text):
    nomatch(text)
    nomatch(text, "PT")
