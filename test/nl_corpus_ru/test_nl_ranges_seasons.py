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


def test_season_genitive_after_nachalo_does_not_strand_the_season():
    # "начало весны 2027" ("the beginning of spring 2027") -- genitive is
    # obligatory after "начало".  This base branch has no season_fuzzy /
    # thirds construction for "начало <season>", so "начало" itself is not
    # consumed; what matters for this fix is that the season resolves
    # correctly (year 2027 -> spring span) instead of falling back to the
    # whole-year genitive-year misparse ("весны" stranded, span = full
    # year) that motivated this fix.
    r = parse("начало весны 2027")
    assert r is not None
    assert r[0].start == _d("2027-3-1") and r[0].end == _d("2027-6-1")
    assert r.remainder.strip() == "начало"


@pytest.mark.parametrize("word,decade_start", [
    ("девяностые", 1990), ("восьмидесятые", 1980), ("семидесятые", 1970),
    ("шестидесятые", 1960), ("двадцатые", 1920),
])
def test_spoken_decade(word, decade_start):
    ss, ee = start_end(word)
    assert ss == AstroDate(decade_start, 1, 1)
    assert ee == AstroDate(decade_start + 10, 1, 1)
