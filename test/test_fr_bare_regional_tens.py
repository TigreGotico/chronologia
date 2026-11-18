# -*- coding: utf-8 -*-
"""Bare "fr" reads "septante", "nonante" and "huitante".

The Académie française lists them: "Ils sont officiels en Belgique et en
Suisse" (Questions de langue, "Septante, octante (ou huitante), nonante",
https://www.dictionnaire-academie.fr/article/QDL078).  They mean 70, 90 and 80,
and no word of the French of France has those values, so reading them under
the bare tag loses no reading.  "quatre-vingts" keeps its value 80.

Anchor: Friday 2026-01-30 10:00.  Expected values come from ``relativedelta``
and ``timedelta`` on the anchor.
"""
from datetime import datetime, timedelta

import pytest
from dateutil.relativedelta import relativedelta

from chronologia import extract_duration, extract_timespan

ANCHOR = datetime(2026, 1, 30, 10)

CASES = [
    ("il y a septante ans", ANCHOR - relativedelta(years=70)),
    ("il y a huitante ans", ANCHOR - relativedelta(years=80)),
    ("il y a quatre-vingts ans", ANCHOR - relativedelta(years=80)),
    ("dans nonante jours", ANCHOR + timedelta(days=90)),
    ("en mille neuf cent septante-cinq", datetime(1975, 1, 1)),
]


@pytest.mark.parametrize("lang", ["fr", "fr-FR", "fr-CA", "fr-LU"])
@pytest.mark.parametrize("text,expected", CASES)
def test_bare_fr_reads_regional_tens(lang, text, expected):
    found = extract_timespan(text, lang, ANCHOR)
    assert found is not None
    assert found.span.start.datetime() == expected
    assert found.remainder == ""


@pytest.mark.parametrize("text", ["dans septante-et-un jours",
                                  "dans septante et un jours"])
def test_compound_is_one_count(text):
    found = extract_duration(text, "fr", anchor=ANCHOR)
    assert found.duration == timedelta(days=71)
    assert found.remainder == "dans"
