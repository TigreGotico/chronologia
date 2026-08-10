"""Russian ranges and seasons.

Ranges: "с A до B" (from A to B) and "между A и B" (between A and B); framing
words are the Russian connectors с/до/между/и.  Between-ranges take
instrumental month forms ("между июнем и сентябрём").  Seasons are
meteorological, northern hemisphere.  Decades are single spoken words
("девяностые" = the 1990s).
"""
import pytest

from ._corpus import AstroDate, start_end, start, parse


def _d(s):
    y, m, dd = (int(x) for x in s.split("-"))
    return AstroDate(y, m, dd)


@pytest.mark.parametrize("text,s,e", [
    ("с июня до августа", "2017-6-1", "2017-9-1"),
    ("с января до марта", "2017-1-1", "2017-4-1"),
    ("с октября до декабря", "2017-10-1", "2018-1-1"),
    ("с июня 2020 до августа 2021", "2020-6-1", "2021-9-1"),
])
def test_from_to_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


@pytest.mark.parametrize("text,s,e", [
    ("между июнем и сентябрём", "2017-6-1", "2017-10-1"),
    ("между апрелем и июнем", "2017-4-1", "2017-7-1"),
])
def test_between_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


@pytest.mark.parametrize("text,s,e", [
    ("следующая зима", "2017-12-1", "2018-3-1"),
    ("лето 2020", "2020-6-1", "2020-9-1"),
    ("зима 2019", "2019-12-1", "2020-3-1"),
    ("следующей зимой", "2017-12-1", "2018-3-1"),
])
def test_season(text, s, e):
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


@pytest.mark.parametrize("text,s,e", [
    # Genitive singular is the case an oblique-governing word forces onto
    # the season noun ("начало весны" = "beginning OF spring", genitive is
    # obligatory after "начало").  Full paradigm per Грамота.ру / Зализняк,
    # "Грамматический словарь русского языка": весна (2*a), лето (1a/1c-ish
    # neuter "о"-stem, gen. лета), осень (8*a, gen./dat./loc. all осени),
    # зима (1a/1'a, gen. зимы).  "лета" is genitive singular of "лето"
    # (summer) here, not to be confused with "лет" (genitive plural of
    # "год", years) -- that word is deliberately absent from unit_year.voc
    # for the same reason (see its docstring); no overlap was introduced.
    ("весны 2027", "2027-3-1", "2027-6-1"),
    ("лета 2027", "2027-6-1", "2027-9-1"),
    ("осени 2027", "2027-9-1", "2027-12-1"),
    ("зимы 2027", "2027-12-1", "2028-3-1"),
    # controls: nominative and instrumental keep working unchanged
    ("весна 2027", "2027-3-1", "2027-6-1"),
    ("весной 2027", "2027-3-1", "2027-6-1"),
])
def test_season_genitive_case(text, s, e):
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


def test_season_genitive_after_nachalo_narrows_to_first_third():
    # "начало весны 2027" ("the beginning of spring 2027") -- genitive is
    # obligatory after "начало".  With the oblique case forms in the vocab
    # AND the season_fuzzy thirds construction both present, the natural
    # genitive phrase narrows to the first third of the season and consumes
    # the part word entirely.
    r = parse("начало весны 2027")
    assert r is not None
    assert r[0].start == AstroDate(2027, 3, 1, 0, 0)
    assert r[0].end == AstroDate(2027, 3, 31, 16, 0)
    assert r.remainder.strip() == ""


# -- fuzzy season thirds (начало/середина/конец <season> [year]) ----------

# Regression: "начало весна 2027" used to match the bare season, stranding
# "начало" ("early") in the remainder.  Independent thirds arithmetic
# mirrors the English ``test_season_fuzzy_bare``/``test_season_fuzzy_year``
# (same :func:`chronologia.subdivide` algorithm, anchor year 2017).
@pytest.mark.parametrize("text,s,e", [
    ("начало весна", AstroDate(2017, 3, 1, 0, 0), AstroDate(2017, 3, 31, 16, 0)),
    ("середина весна", AstroDate(2017, 3, 31, 16, 0), AstroDate(2017, 5, 1, 8, 0)),
    ("конец весна", AstroDate(2017, 5, 1, 8, 0), AstroDate(2017, 6, 1, 0, 0)),
    ("начало зима", AstroDate(2017, 12, 1, 0, 0), AstroDate(2017, 12, 31, 0, 0)),
    ("середина зима", AstroDate(2017, 12, 31, 0, 0), AstroDate(2018, 1, 30, 0, 0)),
    ("конец зима", AstroDate(2018, 1, 30, 0, 0), AstroDate(2018, 3, 1, 0, 0)),
    ("начало лето", AstroDate(2017, 6, 1, 0, 0), AstroDate(2017, 7, 1, 16, 0)),
    ("начало осень", AstroDate(2017, 9, 1, 0, 0), AstroDate(2017, 10, 1, 8, 0)),
])
def test_season_fuzzy_bare(text, s, e):
    assert start_end(text) == (s, e)


@pytest.mark.parametrize("text,s,e", [
    ("начало весна 2027", AstroDate(2027, 3, 1, 0, 0), AstroDate(2027, 3, 31, 16, 0)),
    ("конец весна 2027", AstroDate(2027, 5, 1, 8, 0), AstroDate(2027, 6, 1, 0, 0)),
])
def test_season_fuzzy_year(text, s, e):
    assert start_end(text) == (s, e)


# control: the bare season, unqualified, must stay unchanged.
def test_season_fuzzy_control():
    assert start_end("весна 2027") == (AstroDate(2027, 3, 1), AstroDate(2027, 6, 1))


@pytest.mark.parametrize("word,decade_start", [
    ("девяностые", 1990), ("восьмидесятые", 1980), ("семидесятые", 1970),
    ("шестидесятые", 1960), ("двадцатые", 1920),
])
def test_spoken_decade(word, decade_start):
    ss, ee = start_end(word)
    assert ss == AstroDate(decade_start, 1, 1)
    assert ee == AstroDate(decade_start + 10, 1, 1)
