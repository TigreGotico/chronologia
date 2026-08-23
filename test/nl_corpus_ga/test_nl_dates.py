"""Irish calendar dates, in both constructions the month name takes.

The written date runs day-month-year with no connector: "25 Nollaig 2020".
The month itself appears three ways -- bare ("Bealtaine"), after the noun
"mí" in the genitive ("mí Aibreáin"), and after the bare preposition "i"
eclipsed ("i mBealtaine") -- and all three name the same month.

Expected values are plain calendar facts about the corpus anchor, never the
parser's own output.
"""
import pytest

from chronologia.astrodate import AstroDate

from ._corpus import nomatch, remainder, span, start


@pytest.mark.parametrize("text,y,m,d", [
    ("1 Márta 1990", 1990, 3, 1),
    ("25 Nollaig 2020", 2020, 12, 25),
    ("16 Feabhra 1918", 1918, 2, 16),
    ("1 Bealtaine 2004", 2004, 5, 1),
    ("17 Meitheamh 1944", 1944, 6, 17),
    ("8 Lúnasa 1971", 1971, 8, 8),
    ("30 Meán Fómhair 1995", 1995, 9, 30),
    ("31 Deireadh Fómhair 2001", 2001, 10, 31),
])
def test_full_written_date(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


@pytest.mark.parametrize("text", ["1 Márta 1990", "25 Nollaig 2020"])
def test_full_written_date_consumes_everything(text):
    assert remainder(text) == ""


@pytest.mark.parametrize("text,y,m,d", [
    ("5 Iúil", 2017, 7, 5),
    ("24 Nollaig", 2017, 12, 24),
    ("1 Márta", 2018, 3, 1),
    ("5 Meitheamh", 2018, 6, 5),
    ("11 Samhain", 2017, 11, 11),
])
def test_day_month_without_year(text, y, m, d):
    """With no year stated the date resolves forward from the anchor."""
    assert start(text) == AstroDate(y, m, d)


@pytest.mark.parametrize("text,m", [
    ("Eanáir", 1), ("Feabhra", 2), ("Márta", 3), ("Aibreán", 4),
    ("Bealtaine", 5), ("Meitheamh", 6), ("Iúil", 7), ("Lúnasa", 8),
    ("Meán Fómhair", 9), ("Deireadh Fómhair", 10), ("Samhain", 11),
    ("Nollaig", 12),
])
def test_bare_month_is_the_whole_month(text, m):
    s = span(text)
    assert s.start.month == m and s.start.day == 1
    assert (s.end - s.start).days >= 28


@pytest.mark.parametrize("text,m", [
    ("mí Eanáir", 1), ("mí Feabhra", 2), ("mí Aibreáin", 4),
    ("mí Bealtaine", 5), ("mí Meithimh", 6), ("mí Iúil", 7),
    ("mí Lúnasa", 8), ("mí Samhna", 11), ("mí Nollag", 12),
])
def test_month_after_mi_takes_the_genitive(text, m):
    """"mí" governs the genitive of the month name, so "mí Aibreáin" and
    bare "Aibreán" must name the same month."""
    assert span(text).start.month == m


@pytest.mark.parametrize("text,m", [
    ("i mBealtaine", 5), ("i nEanáir", 1), ("i bhFeabhra", 2),
    ("i nAibreán", 4), ("i nIúil", 7), ("i nDeireadh Fómhair", 10),
])
def test_month_after_bare_i_is_eclipsed(text, m):
    """The bare preposition "i" eclipses the month name that follows it; the
    eclipsed surface names the same month the radical does."""
    assert span(text).start.month == m


@pytest.mark.parametrize("radical,eclipsed", [
    ("Bealtaine", "i mBealtaine"), ("Eanáir", "i nEanáir"),
    ("Feabhra", "i bhFeabhra"),
])
def test_eclipsed_and_radical_month_agree(radical, eclipsed):
    assert span(radical).start.month == span(eclipsed).start.month


@pytest.mark.parametrize("text,m", [
    ("Ean", 1), ("Feabh", 2), ("Aib", 4), ("Beal", 5), ("Meith", 6),
    ("Lún", 8), ("Samh", 11), ("Noll", 12),
])
def test_abbreviated_month(text, m):
    assert span(text).start.month == m


@pytest.mark.parametrize("text", [
    "5", "an cúigiú", "asdf qwerty", "",
])
def test_no_date_without_a_month(text):
    """A day with nothing to attach to, and outright garbage, must fail
    honestly rather than inventing a date."""
    nomatch(text)


@pytest.mark.parametrize("text,y", [("2019", 2019), ("1918", 1918)])
def test_year_reference(text, y):
    s = span(text)
    assert s.start == AstroDate(y, 1, 1) and s.end == AstroDate(y + 1, 1, 1)


def test_iso_literal_date():
    assert start("2017-06-30") == AstroDate(2017, 6, 30)
