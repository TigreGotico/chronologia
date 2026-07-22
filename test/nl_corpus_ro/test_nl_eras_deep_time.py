"""Romanian eras and deep time: BC/AD (î.Hr./d.Hr.), "anul" year reference,
and "acum N milioane/miliarde de ani" deep-time offsets."""
import pytest

from ._corpus import span, start, nomatch

_BP_EPOCH = 1950


@pytest.mark.parametrize("text,year", [
    ("44 î.hr.", -43),
    ("44 înainte de hristos", -43),
    ("753 î.hr.", -752),
    ("2020 după hristos", 2020),
    ("2020 d.hr.", 2020),
])
def test_era_year(text, year):
    assert start(text).year == year


def test_bc_is_year_wide():
    s = span("44 î.hr.")
    assert s.end.year - s.start.year == 1


@pytest.mark.parametrize("text,year", [
    ("în anul 2000", 2000),
    ("anul 1789", 1789),
])
def test_year_reference(text, year):
    assert start(text).year == year


@pytest.mark.parametrize("text,years_ago", [
    ("acum 66 de milioane de ani", 66_000_000),
    ("acum 4 miliarde de ani", 4_000_000_000),
    ("acum 250 de milioane de ani", 250_000_000),
])
def test_deep_time(text, years_ago):
    assert start(text).year == _BP_EPOCH - years_ago
