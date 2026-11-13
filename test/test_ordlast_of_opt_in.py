# -*- coding: utf-8 -*-
"""The "last <unit> of" refusal acts only in a locale that opts in.

pt "o último dia de escola" and en "the last day of school" name the final
day of school, so they refuse.  In de, da, fr and pl the "last" word also
means "previous" and the preposition after it also means "in", so the phrase
after the period is a place or an activity and the previous period stands
(DWDS s.v. "letzt", 3: "eben erst vergangen, vorig", example "letztes Jahr,
im letzten Sommer waren wir an der See", https://www.dwds.de/wb/letzt).
Those locales ship no ``marker_ordlast_of.voc``.

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
