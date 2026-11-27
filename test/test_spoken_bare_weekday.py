"""A weekday alone gives the bare weekday name.

Gold: Unicode CLDR 47, cldr-json ca-gregorian pt.json, days > format >
wide (Papers: Reference/Calendars/cldr47_ca_gregorian/pt.json), listed here
Monday first. pt-PT and pt-BR use the same wide names.
"""
import pytest

from chronologia.spoken import spoken_date

CLDR_PT_WIDE = ["segunda-feira", "terça-feira", "quarta-feira",
                "quinta-feira", "sexta-feira", "sábado", "domingo"]


@pytest.mark.parametrize("tag", ["pt-PT", "pt-BR"])
@pytest.mark.parametrize("weekday", range(7))
def test_bare_weekday(tag, weekday):
    assert spoken_date(tag, weekday=weekday) == CLDR_PT_WIDE[weekday]


@pytest.mark.parametrize("tag", ["pt-PT", "pt-BR"])
def test_empty_call_raises(tag):
    with pytest.raises(ValueError, match="a date needs"):
        spoken_date(tag)


@pytest.mark.parametrize("weekday", [7, -1])
def test_bare_weekday_out_of_range(weekday):
    with pytest.raises(ValueError):
        spoken_date("pt-PT", weekday=weekday)
