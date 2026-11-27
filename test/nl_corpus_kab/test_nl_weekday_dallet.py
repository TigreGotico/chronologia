# -*- coding: utf-8 -*-
"""Kabyle weekday names and the "ass n" frame from Dallet 1982, the market
homograph, the night words and the annexed "yiḍelli".

Sources: Dallet, Dictionnaire kabyle-français (SELAF 1982): lḥedd / ass
el_lḥedd p. 305, letnayen / ass l_letnayen p. 826, ṯṯlata / ass n eṯṯlata
p. 824, laṛebɛa p. 703, lexmis p. 902, ljemɛa and ljamuɛa p. 371, ssebt
p. 756, "ssuq el_lḥedd, le marché du dimanche" p. 305, "ssuq l_letnayen,
marché du lundi" p. 826, iḍ, pl. uḍan / aḍan p. 170; Dallet,
Dictionnaire français-kabyle (SELAF 1985) p. 168, llil.

Gold is calendar arithmetic from the anchor, Tuesday 2017-06-27: Wednesday
06-28, Thursday 06-29, Friday 06-30, Saturday 07-01, Sunday 07-02, Monday
07-03; yesterday 06-26; last Friday 06-23, last Sunday 06-25; the Friday of
next week 07-07.
"""
import pytest

from ._corpus import parse, nomatch, span

FRAME = [
    ("lḥedd", "2017-07-02"),
    ("ass n lḥedd", "2017-07-02"),
    ("ass el_lḥedd", "2017-07-02"),
    ("ass el lḥedd", "2017-07-02"),
    ("ass l_letnayen", "2017-07-03"),
    ("ass l letnayen", "2017-07-03"),
    ("ass n letnayen", "2017-07-03"),
    ("ass n eṯṯlata", "2017-06-27"),
    ("ass n ttlata", "2017-06-27"),
    ("ṯṯlata", "2017-06-27"),
    ("laṛebɛa", "2017-06-28"),
    ("ass n Larebɛa", "2017-06-28"),
    ("lexmis", "2017-06-29"),
    ("ass n lexmis", "2017-06-29"),
    ("ljemɛa", "2017-06-30"),
    ("Ljemɛa", "2017-06-30"),
    ("ljemεa", "2017-06-30"),
    ("ljamuɛa", "2017-06-30"),
    ("ass n ljemɛa", "2017-06-30"),
    ("ssebt", "2017-07-01"),
    ("ass n ssebt", "2017-07-01"),
]


def _day(r):
    s = r.span.start
    return f"{s.year:04d}-{s.month:02d}-{s.day:02d}"


@pytest.mark.parametrize("text,day", FRAME)
def test_weekday_frame_consumed(text, day):
    r = parse(text)
    assert r is not None
    assert _day(r) == day
    assert r.remainder.strip() == ""


def test_weekday_wins_over_season():
    r = parse("ass n Larebɛa tafsut")
    assert _day(r) == "2017-06-28"
    assert r.remainder.strip() == "tafsut"


@pytest.mark.parametrize("text", [
    "ssuq l_letnayen",
    "ssuq l letnayen",
    "ssuq n letnayen",
    "ssuq el_lḥedd",
    "ssuq el lḥedd",
    "ssuq n ssebt",
])
def test_market_gives_no_date(text):
    nomatch(text)


def test_market_place_keeps_weekday():
    # "to the market this coming Saturday": no link word, so "ssuq" is a place.
    r = parse("Ad nṛuḥ ɣer ssuq ssebt-agi i d-iteddun akken ad d-naɣ lexḍer.")
    assert _day(r) == "2017-07-01"


NATIVE = [
    ("Ass n lḥedd yezrin, nruḥ ɣer tala n taddart, nessew aman isemmaḍen.",
     "2017-06-25", "nruḥ ɣer tala n taddart, nessew aman isemmaḍen"),
    ("Ass n Ljemɛa yezrin, nruḥ ɣer lebḥer nekk d yemma.",
     "2017-06-23", "nruḥ ɣer lebḥer nekk d yemma"),
    ("Ad nruḥ ad nẓer jida deg taddart ass n lǧemεa n ddurt i d-iteddun.",
     "2017-07-07", "Ad nruḥ ad nẓer jida deg taddart"),
    ("Iḍelli, ass n letnayen, nruḥ ɣer yiri n lebḥer nekk d yemma.",
     "2017-06-26", "nruḥ ɣer yiri n lebḥer nekk d yemma"),
    ("Tameɣra n yiḍelli tella tecbeḥ aṭas.",
     "2017-06-26", "Tameɣra n tella tecbeḥ aṭas"),
]


@pytest.mark.parametrize("text,day,rem", NATIVE)
def test_native_rows(text, day, rem):
    r = parse(text)
    assert _day(r) == day
    assert " ".join(r.remainder.replace(",", " ").split()) == " ".join(
        rem.replace(",", " ").split())


@pytest.mark.parametrize("text", ["llil", "uḍan", "aḍan"])
def test_night_words_read_as_iḍ(text):
    assert span(text) == span("iḍ")
