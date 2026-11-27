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


@pytest.mark.parametrize("text", [
    # a relative word between the day and the idiom: no reading, never today
    "jeudi prochain en huit",
    "jeudi dernier en huit",
    "lundi prochain en huit",
    "le lundi suivant en huit",
    # two idioms joined: one day each, no single span
    "vendredi en huit ou en quinze",
    # a word after "en huit" that may be the noun it counts ("en huit
    # manches", eight rounds): the phrase refuses
    "le match de jeudi en huit manches",
])
def test_idiom_refuses_what_it_cannot_read(text):
    nomatch(text, THU)


def test_jusqu_a_the_idiom_ends_after_that_day():
    # as "jusqu'à vendredi" ends at the end of that Friday
    r = parse("jusqu'à jeudi en huit", THU)
    assert r is not None
    assert (r[0].start, r[0].end) == (ad(THU), ad(datetime(2026, 12, 4)))
    assert r.remainder == ""


def test_a_preposition_after_the_idiom_keeps_it():
    r = parse("jeudi en huit chez Paul", THU)
    assert r is not None
    assert r[0].start == ad(datetime(2026, 12, 3))
    assert r.remainder == "chez Paul"


@pytest.mark.parametrize("text,day", [
    ("depuis vendredi en huit", datetime(2026, 12, 4)),
    ("depuis samedi en quinze", datetime(2026, 12, 12)),
    ("depuis jeudi en quinze", datetime(2026, 12, 10)),
])
def test_depuis_never_opens_on_the_idiom(text, day):
    # The idiom names a day after the anchor, so no "since" span opens on it
    # (on dev "depuis vendredi en huit" ran from Friday 20 November to the
    # anchor).  As "depuis demain" reads, the day stands and "depuis" is left
    # over.
    r = parse(text, THU)
    assert r is not None
    assert (r[0].start, r[0].end) == (ad(day), ad(day + timedelta(days=1)))
    assert r.remainder == "depuis"


def test_digit_numeral_is_no_idiom_and_refuses():
    # The dictionaries give the locution with the spelled numeral only; "en 8"
    # after a day is unattested, and reading the bare day would be wrong.
    nomatch("jeudi en 8", THU)
    nomatch("jeudi en 15", THU)


@pytest.mark.parametrize("text", ["jeudi en 8 heures", "jeudi en huit heures"])
def test_a_digit_numeral_before_a_unit_counts_like_the_spelled_one(text):
    # "en 8 heures" counts hours, as "en huit heures" does: no week idiom, but
    # the clock eight o'clock on a Thursday, one minute wide, with no word left
    # over.  Said on Thursday 26 November 2026 at 10:00, 08:00 has passed, and
    # a bare weekday with a clock that has passed is the next one (rulings.md:
    # "tuesday at 10am" said on a Tuesday at 13:04): Thursday 3 December 2026.
    r = parse(text, THU)
    assert r is not None and r.remainder == ""
    assert (r.span.start, r.span.end) == (ad(datetime(2026, 12, 3, 8, 0)),
                                          ad(datetime(2026, 12, 3, 8, 1)))


@pytest.mark.parametrize("text", [
    "jeudi. En huit manches, Alice gagne.",
    "Jeudi. En huit, nous partons",
])
def test_no_idiom_across_a_sentence_break(text):
    # "jeudi" said on Thursday is today (ruling 6); the next sentence is not
    # part of it
    r = parse(text, THU)
    assert r is not None
    assert r[0].start == ad(datetime(2026, 11, 26))


def test_coordinated_idioms_after_a_comma_refuse():
    nomatch("vendredi en huit, ou en quinze", THU)


def test_candidates_drop_the_clock_of_a_refused_idiom():
    from chronologia import extract_candidates
    assert extract_candidates("lundi en huit à 10h", "fr", THU) == []


def test_a_unit_after_a_joined_numeral_is_no_second_idiom():
    # "et en quinze minutes" counts minutes: Friday 4 December at 10:00 stands
    r = parse("vendredi en huit à 10h et en quinze minutes", THU)
    assert r is not None
    assert (r[0].start, r[0].end) == (ad(datetime(2026, 12, 4, 10, 0)),
                                      ad(datetime(2026, 12, 4, 10, 1)))


@pytest.mark.parametrize("text", [
    "lundi en huit entre 10h et 11h",
    "lundi en huit de 10h à 11h",
])
def test_a_clock_range_after_a_refused_idiom_refuses(text):
    # the idiom names no day, so the clock range does not time the anchor's day
    from chronologia import extract_candidates
    nomatch(text, THU)
    assert extract_candidates(text, "fr", THU) == []
