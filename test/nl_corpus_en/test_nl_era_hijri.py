"""English surfaces for the Islamic (lunar) Hijri and Iranian Solar Hijri eras.

The era math already existed in the registry (``resolve_era("hijri", ...)`` /
``resolve_era("solar_hijri", ...)``) but English carried NO surface for it, so
"1447 AH" was read literally as the Gregorian year 1447 and the era name
stranded.  These wire the surfaces (``AH`` / ``Anno Hegirae`` / ``hijri`` /
``hijra``; ``Solar Hijri`` / ``S.H.`` / ``hijri shamsi`` / ``persian calendar
year``) and assert the epoch-correct Gregorian year.

Reference values are INDEPENDENT of the extractor: they come straight from
``chronologia.resolve_era`` (the era registry), never from the parser's own
output.
"""
import pytest

from chronologia import resolve_era

from ._corpus import ANCHOR, AstroDate, parse, span, start_end


def _greg_year(era, n):
    d = resolve_era(era, n)
    return d.year


# -- Islamic (lunar) Hijri: AH 1 == 622-07-19 -----------------------------
@pytest.mark.parametrize("text", [
    "1447 AH",
    "AH 1447",
    "Anno Hegirae 1447",
    "1447 A.H.",
    "1447 hijri",
    "hijra 1447",
])
def test_hijri_1447_resolves_through_epoch(text):
    s = span(text)
    assert s.start.year == _greg_year("hijri", 1447)          # ~2025
    assert parse(text)[1] == ""                                # name consumed


# -- Iranian Solar Hijri (Jalali): SH 1 == 622-03-21 ----------------------
@pytest.mark.parametrize("text", [
    "1404 Solar Hijri",
    "1404 S.H.",
    "1404 hijri shamsi",
])
def test_solar_hijri_1404_is_2025(text):
    s = span(text)
    assert s.start.year == _greg_year("solar_hijri", 1404)    # 2025
    assert s.start.year == 2025
    assert parse(text)[1] == ""


# -- guard: the short abbreviations never fabricate a date standalone ------
@pytest.mark.parametrize("text", ["ah", "be", "sh"])
def test_bare_era_abbreviation_not_adjacent_to_year_is_no_date(text):
    # a lone era abbreviation with NO adjacent year must name nothing
    assert parse(text, ANCHOR) is None


def test_ah_does_not_misfire_inside_ordinary_text():
    # "ah" only fires adjacent to a year; an interjection-like "ah" alone or
    # with no year must not fabricate a Hijri date
    assert parse("ah well", ANCHOR) is None
