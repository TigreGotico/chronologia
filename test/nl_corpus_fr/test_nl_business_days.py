"""Jours ouvrés / ouvrables : « dans N jours ouvrés », « le prochain jour
ouvrable », « N jours ouvrés après noël ».

Un jour ouvrable est un jour de semaine qui n'est ni un week-end ni un jour
férié de la ``jurisdiction``.  Sans juridiction, le compte ignore les fériés.

La distinction juridique française jours *ouvrables* (tous sauf le repos
hebdomadaire et les fériés) / jours *ouvrés* (effectivement travaillés) n'est
pas modélisée : les deux surfaces valent le même jour ouvrable
lundi-vendredi-moins-fériés, au sens courant de « jour travaillé ».

Ancre : mercredi 2026-12-23.  Jours fériés FR dans l'intervalle :
ven 2026-12-25 (Noël), ven 2027-01-01 (Jour de l'an).

FR (saute Noël + Jour de l'an), depuis mer 12-23 :
    jeu24(1) lun28(2) mar29(3) mer30(4) jeu31(5) lun Jan4(6)
Sans juridiction (jours de semaine seulement) :
    jeu24(1) ven25(2) lun28(3)
"""
from datetime import date, datetime, timedelta

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

import pytest

ANCHOR = datetime(2026, 12, 23, 9, 0)   # mercredi


def start(text, jurisdiction=None):
    r = extract_timespan(text, "fr", ANCHOR, jurisdiction=jurisdiction)
    assert r is not None, f"{text!r} n'a pas résolu"
    return r[0].start


def nomatch(text, jurisdiction=None):
    r = extract_timespan(text, "fr", ANCHOR, jurisdiction=jurisdiction)
    assert r is None, f"{text!r} a résolu de façon inattendue en {r!r}"


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    ("dans 1 jour ouvré", date(2026, 12, 24)),
    ("dans 2 jours ouvrés", date(2026, 12, 28)),
    ("dans 4 jours ouvrés", date(2026, 12, 30)),
    ("dans 5 jours ouvrés", date(2026, 12, 31)),
    ("dans 6 jours ouvrés", date(2027, 1, 4)),
    ("4 jours ouvrables", date(2026, 12, 30)),
])
def test_compte_fr(text, expected):
    assert start(text, "FR") == _ad(expected)


@pytest.mark.parametrize("text,expected", [
    ("dans 1 jour ouvré", date(2026, 12, 24)),
    ("dans 2 jours ouvrés", date(2026, 12, 25)),   # aveugle aux fériés
    ("dans 3 jours ouvrés", date(2026, 12, 28)),
])
def test_compte_aveugle(text, expected):
    assert start(text) == _ad(expected)


def test_prochain_jour_ouvrable():
    assert start("le prochain jour ouvrable", "FR") == _ad(date(2026, 12, 24))


@pytest.mark.parametrize("text,expected,juris", [
    ("3 jours ouvrés après noël", date(2026, 12, 30), "FR"),
    ("3 jours ouvrés après noël", date(2026, 12, 30), None),
    ("2 jours ouvrables avant noël", date(2026, 12, 23), "FR"),
])
def test_composition(text, expected, juris):
    assert start(text, juris) == _ad(expected)


def test_largeur_un_jour():
    r = extract_timespan("dans 3 jours ouvrés", "fr", ANCHOR, jurisdiction="FR")
    assert r[0].width == timedelta(days=1)


@pytest.mark.parametrize("text", ["comme d habitude", "tout est normal"])
def test_negatifs(text):
    nomatch(text)
    nomatch(text, "FR")
