"""Meteorological season pinned to an explicit year: "summer 2019",
"the winter of 2020", "in the summer of 1969".

Season windows (Northern-hemisphere meteorological convention, first day of
the season's first month to the first day of the month after its last):

    spring  Mar 1 - Jun 1   (same year)
    summer  Jun 1 - Sep 1   (same year)
    fall    Sep 1 - Dec 1   (same year)
    winter  Dec 1 (year) - Mar 1 (year + 1)

Winter is the only one that crosses the year boundary: "winter 2020" is the
December-2020 winter, ending in March 2021.  Edges are hand-derived from the
named year -- the anchor plays no role once a year is stated.
"""
import pytest

from chronologia.astrodate import AstroDate
from ._corpus import start_end


# season -> (start_month, end_month, end_year_offset)
_SEASON = {
    "spring": (3, 6, 0),
    "summer": (6, 9, 0),
    "fall": (9, 12, 0),
    "autumn": (9, 12, 0),
    "winter": (12, 3, 1),
}


def _cases():
    out = []
    for year in (1969, 2000, 2015, 2019, 2020):
        for name, (sm, em, eoff) in _SEASON.items():
            for surf in (f"{name} {year}", f"{name} of {year}",
                         f"the {name} of {year}"):
                out.append((surf, name, year))
    return out


@pytest.mark.parametrize("text,name,year", _cases())
def test_season_year(text, name, year):
    sm, em, eoff = _SEASON[name]
    s = AstroDate(year, sm, 1)
    e = AstroDate(year + eoff, em, 1)
    assert start_end(text) == (s, e)


# framing preposition does not disturb the resolved span
@pytest.mark.parametrize("text,name,year", [
    ("in the summer of 1969", "summer", 1969),
    ("in the winter of 1999", "winter", 1999),
    ("back in the spring of 2000", "spring", 2000),
])
def test_season_year_framed(text, name, year):
    sm, em, eoff = _SEASON[name]
    assert start_end(text) == (AstroDate(year, sm, 1),
                               AstroDate(year + eoff, em, 1))
