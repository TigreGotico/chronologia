"""French "<day> en huit" and "<day> en quinze": the same day one or two
weeks on.

Sources:

* TLFi (CNRTL) s.v. "huit", I.A: "[Avec ell. de jours] En huit. Le même jour
  de la semaine suivante. À lundi en huit! De lundi, de mardi en huit (Ac.)",
  with Hugo, Corresp., 1859, written on "Samedi 7 août": "Victor devant
  revenir samedi prochain (d'aujourd'hui en huit), c'est encore sept jours à
  attendre".
* TLFi s.v. "quinze": "[Avec ell. de jours] En quinze. Le même jour, dans deux
  semaines. Demain en quinze."
* Académie française, 9th edition, s.v. "huit": "En huit, au huitième jour à
  partir du jour où l'on parle ou qui sert de référence. D'aujourd'hui en
  huit, de demain en huit"; s.v. "quinze": "En quinze, le quinzième jour à
  partir du jour où l'on parle ou qui sert de référence. D'aujourd'hui en
  quinze. Nous nous verrons jeudi en quinze."
* Larousse s.v. "huit": "Lundi, mardi en huit, lundi, mardi de la semaine
  prochaine."
* Wiktionnaire s.v. "en huit": "pour désigner ce jour dans la semaine à venir
  à partir du 8e jour, aujourd'hui étant le 1er jour".

The day word is counted as day one, so "en huit" adds seven days and
"en quinze" fourteen.  For a weekday the sources agree only when the weekday
falls on or after the anchor's weekday in the locale's week (Monday first).
Said on a Thursday, Larousse makes "lundi en huit" the Monday of next week
(30 November), while counting from the coming Monday (the Académie's "jour
qui sert de référence", Wiktionnaire's "à partir du 8e jour") gives
7 December.  Where they disagree the phrase refuses.

Expected values are hand-computed from the calendar of November and December
2026, never read back from the parser.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ad, nomatch, parse

THU = datetime(2026, 11, 26, 10, 0)   # a Thursday
MON = datetime(2026, 11, 30, 10, 0)   # a Monday
SUN = datetime(2026, 11, 29, 10, 0)   # a Sunday


def _day(text, anchor):
    r = parse(text, anchor)
    assert r is not None, f"{text!r} did not parse"
    return r[0].start, r[0].end, r.remainder


@pytest.mark.parametrize("text,anchor,day", [
    # said on Thursday 26 November
    ("jeudi en huit", THU, datetime(2026, 12, 3)),
    ("vendredi en huit", THU, datetime(2026, 12, 4)),
    ("samedi en huit", THU, datetime(2026, 12, 5)),
    ("dimanche en huit", THU, datetime(2026, 12, 6)),
    ("jeudi en 8", THU, datetime(2026, 12, 3)),
    ("jeudi en quinze", THU, datetime(2026, 12, 10)),
    ("dimanche en quinze", THU, datetime(2026, 12, 13)),
    ("aujourd'hui en huit", THU, datetime(2026, 12, 3)),
    ("d'aujourd'hui en huit", THU, datetime(2026, 12, 3)),
    ("demain en huit", THU, datetime(2026, 12, 4)),
    ("aujourd'hui en quinze", THU, datetime(2026, 12, 10)),
    ("demain en quinze", THU, datetime(2026, 12, 11)),
    # said on Monday 30 November: every weekday is on or after Monday
    ("lundi en huit", MON, datetime(2026, 12, 7)),
    ("mardi en huit", MON, datetime(2026, 12, 8)),
    ("dimanche en huit", MON, datetime(2026, 12, 13)),
    ("mardi en quinze", MON, datetime(2026, 12, 15)),
    # said on Sunday 29 November
    ("dimanche en huit", SUN, datetime(2026, 12, 6)),
])
def test_en_huit_reads_one_or_two_weeks_on(text, anchor, day):
    start, end, remainder = _day(text, anchor)
    assert (start, end) == (ad(day), ad(day + timedelta(days=1)))
    assert remainder == ""


@pytest.mark.parametrize("text,anchor", [
    # the weekday lies before the anchor's weekday in the week: Larousse and
    # the Académie/Wiktionnaire count disagree, so no reading
    ("lundi en huit", THU),
    ("mardi en huit", THU),
    ("mercredi en huit", THU),
    ("lundi en quinze", THU),
    ("lundi en huit", SUN),
    ("samedi en huit", SUN),
    # no source gives a day word other than "aujourd'hui" and "demain"
    ("hier en huit", THU),
])
def test_en_huit_refuses_where_sources_disagree(text, anchor):
    nomatch(text, anchor)


def test_en_huit_heures_is_not_the_idiom():
    # "en huit heures" counts hours: the week idiom does not fire
    r = parse("jeudi en huit heures", THU)
    assert r is None or r[0].start != ad(datetime(2026, 12, 3))
