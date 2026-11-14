# -*- coding: utf-8 -*-
"""The "last <unit> of" refusal acts only in a locale that opts in.

pt "o último dia de escola" and en "the last day of school" name the final
day of school, so they refuse.  In de, da, fr and pl the "last" word also
means "previous" and the preposition after it also means "in", so the phrase
after the period is a place or an activity and the previous period stands
(DWDS s.v. "letzt", 3: "eben erst vergangen, vorig", example "letztes Jahr,
im letzten Sommer waren wir an der See", https://www.dwds.de/wb/letzt).
Those locales ship no ``marker_ordlast_of.voc``.

Inside the two locales that opt in, the "of" word must be the complement of
the adjective.  en bare "last week" is the determiner "previous"
(Wiktionary s.v. "last", determiner 1: "The (one) immediately before the
present. We went there last year.", https://en.wiktionary.org/wiki/last),
so "I told you last week of the change" is the previous week; only "the
last" is "final".  pt "de forma", "de maneira", "de modo" and "de manhã"
open an adverbial locution (Priberam s.v. "forma", "maneira", "modo" and
"manhã"), so "no último ano de forma notável" is the previous year.  So do
"de qualquer forma", "da mesma forma" and the locutions "de novo", "de
repente", "de vez em quando", "de facto", "de resto", "de propósito" and
"de todo", each listed in its Priberam entry.

Gold values are hand arithmetic from the anchor, Tuesday 2017-06-27 13:04:
the previous Monday-to-Sunday week is 2017-06-19 to 2017-06-26 (exclusive
end), the previous month is May 2017, the previous year is 2016.  Three
phrases name a stretch inside the previous period that the parser does not
narrow yet: Monday to Friday of that week (2017-06-19 to 2017-06-24),
January to March 2016, and summer 2016 (June to August).  For those the
answer must hold the stretch and stay inside the previous period.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

ANCHOR = datetime(2017, 6, 27, 13, 4)


def ad(y, m, d):
    return AstroDate(y, m, d, 0, 0, 0, 0)


def span(text, lang):
    r = extract_timespan(text, lang, ANCHOR)
    assert r is not None, f"{text!r} ({lang}) did not parse"
    return r.span


@pytest.mark.parametrize("lang,text", [
    ("pt", "o último dia de escola foi triste"),
    ("en", "the last day of school"),
    ("en", "the last week of school"),
])
def test_opted_in_locale_refuses(lang, text):
    assert extract_timespan(text, lang, ANCHOR) is None


@pytest.mark.parametrize("lang,text,start,end", [
    ("de", "letzte Woche im Büro", ad(2017, 6, 19), ad(2017, 6, 26)),
    ("de", "letzten Monat im Krankenhaus", ad(2017, 5, 1), ad(2017, 6, 1)),
    ("da", "sidste måned i Paris", ad(2017, 5, 1), ad(2017, 6, 1)),
    ("pl", "w ostatnim tygodniu w pracy", ad(2017, 6, 19), ad(2017, 6, 26)),
    ("en", "the last day of the month", ad(2017, 6, 30), ad(2017, 7, 1)),
    ("en", "I told you last week of the change",
     ad(2017, 6, 19), ad(2017, 6, 26)),
    ("en", "I heard last week of his death", ad(2017, 6, 19), ad(2017, 6, 26)),
    ("en", "I was reminded last week of my appointment",
     ad(2017, 6, 19), ad(2017, 6, 26)),
    ("en", "we talked last week of going to Lisbon",
     ad(2017, 6, 19), ad(2017, 6, 26)),
    ("en", "last week of course I was busy", ad(2017, 6, 19), ad(2017, 6, 26)),
    ("en", "we spoke last month of the merger", ad(2017, 5, 1), ad(2017, 6, 1)),
    ("en", "he wrote to me last month of his plans",
     ad(2017, 5, 1), ad(2017, 6, 1)),
    ("en", "she spoke last year of retiring", ad(2016, 1, 1), ad(2017, 1, 1)),
    ("pt", "o número de transplantes aumentou no último ano de forma notável",
     ad(2016, 1, 1), ad(2017, 1, 1)),
    ("pt", "as vendas cresceram no último mês de forma consistente",
     ad(2017, 5, 1), ad(2017, 6, 1)),
    ("pt", "choveu na última semana de forma intensa",
     ad(2017, 6, 19), ad(2017, 6, 26)),
    ("pt", "os preços subiram no último ano de maneira geral",
     ad(2016, 1, 1), ad(2017, 1, 1)),
    ("pt", "a inflação desceu no último ano de modo consistente",
     ad(2016, 1, 1), ad(2017, 1, 1)),
    ("pt", "na última semana de manhã", ad(2017, 6, 19), ad(2017, 6, 26)),
    ("pt", "no último mês de tarde", ad(2017, 5, 1), ad(2017, 6, 1)),
    ("pt", "na última semana de noite", ad(2017, 6, 19), ad(2017, 6, 26)),
    ("pt", "no último mês de madrugada", ad(2017, 5, 1), ad(2017, 6, 1)),
    ("pt", "na última semana, de Lisboa ao Porto, choveu sempre",
     ad(2017, 6, 19), ad(2017, 6, 26)),
    ("pt", "no último mês, de casa em casa, vendi tudo",
     ad(2017, 5, 1), ad(2017, 6, 1)),
    ("pt", "na última semana de qualquer forma",
     ad(2017, 6, 19), ad(2017, 6, 26)),
    ("pt", "no último mês de qualquer maneira fui trabalhar",
     ad(2017, 5, 1), ad(2017, 6, 1)),
    ("pt", "no último ano de qualquer modo",
     ad(2016, 1, 1), ad(2017, 1, 1)),
    ("pt", "as vendas subiram no último ano de uma forma geral",
     ad(2016, 1, 1), ad(2017, 1, 1)),
    ("pt", "as vendas subiram no último ano de um modo geral",
     ad(2016, 1, 1), ad(2017, 1, 1)),
    ("pt", "no último mês de uma maneira geral",
     ad(2017, 5, 1), ad(2017, 6, 1)),
    ("pt", "no último ano de certa forma tudo mudou",
     ad(2016, 1, 1), ad(2017, 1, 1)),
    ("pt", "no último mês de alguma forma tudo correu bem",
     ad(2017, 5, 1), ad(2017, 6, 1)),
    ("pt", "choveu na última semana de outra forma",
     ad(2017, 6, 19), ad(2017, 6, 26)),
    ("pt", "os preços subiram no último mês de igual modo",
     ad(2017, 5, 1), ad(2017, 6, 1)),
    ("pt", "as vendas subiram no último ano da mesma forma",
     ad(2016, 1, 1), ad(2017, 1, 1)),
    ("pt", "choveu na última semana de novo",
     ad(2017, 6, 19), ad(2017, 6, 26)),
    ("pt", "na última semana de repente começou a chover",
     ad(2017, 6, 19), ad(2017, 6, 26)),
    ("pt", "no último mês de vez em quando chovia",
     ad(2017, 5, 1), ad(2017, 6, 1)),
    ("pt", "no último ano de facto as vendas subiram",
     ad(2016, 1, 1), ad(2017, 1, 1)),
    ("pt", "no último ano de fato as vendas subiram",
     ad(2016, 1, 1), ad(2017, 1, 1)),
    ("pt", "no último mês de resto nada mudou",
     ad(2017, 5, 1), ad(2017, 6, 1)),
    ("pt", "na última semana de propósito não saí",
     ad(2017, 6, 19), ad(2017, 6, 26)),
    ("pt", "no último ano de todo não saí",
     ad(2016, 1, 1), ad(2017, 1, 1)),
    ("pt", "na última semana de manha",
     ad(2017, 6, 19), ad(2017, 6, 26)),
])
def test_previous_period_stands(lang, text, start, end):
    s = span(text, lang)
    assert (s.start, s.end) == (start, end)


@pytest.mark.parametrize("lang,text,inner,outer", [
    ("fr", "la semaine dernière de lundi à vendredi",
     (ad(2017, 6, 19), ad(2017, 6, 24)), (ad(2017, 6, 19), ad(2017, 6, 26))),
    ("fr", "l'année dernière de janvier à mars",
     (ad(2016, 1, 1), ad(2016, 4, 1)), (ad(2016, 1, 1), ad(2017, 1, 1))),
    ("de", "letztes Jahr im Sommer",
     (ad(2016, 6, 1), ad(2016, 9, 1)), (ad(2016, 1, 1), ad(2017, 1, 1))),
])
def test_previous_period_holds_the_stretch(lang, text, inner, outer):
    s = span(text, lang)
    assert outer[0] <= s.start <= inner[0]
    assert inner[1] <= s.end <= outer[1]
