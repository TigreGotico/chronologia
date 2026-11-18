# -*- coding: utf-8 -*-
"""fr "été" behind a form of "avoir" is the past participle of "être".

"il a été malade le 15 mai" says nothing about summer, so the season reading
must not take the place of the date beside it.  The season stays a season
after a determiner or a preposition.  Larousse, conjugaison du verbe "être":
passé composé "il a été", plus-que-parfait "il avait été".

Anchor: Saturday 2026-10-24 13:00.  The next 15 May after the anchor is
2027-05-15 (ruling 3 of the disagreement rulings); the summer of 2026 runs from
1 June to 1 September (the span the season reading gives for "cet été").
"""
from datetime import datetime

import pytest

from chronologia import extract_candidates, extract_timespan

ANCHOR = datetime(2026, 10, 24, 13)
MAY_15 = datetime(2027, 5, 15)

PARTICIPLE_WITH_DATE = [
    "quel jour de la semaine a été le 15 mai",
    "il a été malade le 15 mai",
    "le 15 mai a été un vendredi",
    "elle avait été absente le 15 mai",
    "ils ont été malades le 15 mai",
    "il aurait été malade le 15 mai",
    "j'ai été malade le 15 mai",
]

SEASON = [
    ("cet été", datetime(2026, 6, 1), datetime(2026, 9, 1)),
    ("en été", datetime(2026, 6, 1), datetime(2026, 9, 1)),
    ("l'été prochain", datetime(2027, 6, 1), datetime(2027, 9, 1)),
    ("il a plu cet été", datetime(2026, 6, 1), datetime(2026, 9, 1)),
    ("il a été malade en été", datetime(2026, 6, 1), datetime(2026, 9, 1)),
]


@pytest.mark.parametrize("text", PARTICIPLE_WITH_DATE)
def test_participle_keeps_the_date(text):
    found = extract_timespan(text, "fr-FR", ANCHOR)
    assert found is not None
    assert found.span.start.datetime() == MAY_15
    assert found.span.end.datetime() == datetime(2027, 5, 16)


@pytest.mark.parametrize("text", PARTICIPLE_WITH_DATE)
def test_participle_is_no_season_candidate(text):
    seasons = [c for c in extract_candidates(text, "fr-FR", ANCHOR)
               if c.construction == "season_ref"]
    assert seasons == []


def test_participle_alone_names_no_time():
    assert extract_timespan("il avait été", "fr-FR", ANCHOR) is None


@pytest.mark.parametrize("text,start,end", SEASON)
def test_season_stays_a_season(text, start, end):
    found = extract_timespan(text, "fr-FR", ANCHOR)
    assert found is not None
    assert found.span.start.datetime() == start
    assert found.span.end.datetime() == end
