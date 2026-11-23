"""extract_event reads "every holiday in <country>" as the next holiday of that country."""
from datetime import datetime

import pytest

from chronologia.astrodate import AstroDate
from chronologia.civil_holidays import registry
from chronologia.events import extract_event
from chronologia.recurrence import JurisdictionHolidays

_ANCHOR = datetime(2026, 11, 19, 10, 0)

_CASES = [
    ("every holiday in Portugal", "en", "PT"),
    ("every public holiday in Portugal", "en", "PT"),
    ("all holidays in Portugal", "en", "PT"),
    ("every holiday in Spain", "en", "ES"),
    ("every holiday in France", "en", "FR"),
    ("every holiday in Germany", "en", "DE"),
    ("every holiday in Brazil", "en", "BR"),
    ("every holiday in the United States", "en", "US"),
    ("every holiday in the United Kingdom", "en", "GB"),
    ("todos os feriados em Portugal", "pt", "PT"),
    ("cada feriado de Portugal", "pt", "PT"),
    ("todos os feriados em Espanha", "pt", "ES"),
    ("cada feriado da França", "pt", "FR"),
    ("todos os feriados na Alemanha", "pt", "DE"),
    ("cada feriado do Brasil", "pt", "BR"),
]


def _next_holiday_start(code):
    anchor = AstroDate(2026, 11, 19, 10, 0)
    for year in (2026, 2027):
        starts = sorted(h.span.start
                        for h in registry.holidays_for(code, year, None, ("public",))
                        if h.span.start >= anchor)
        if starts:
            return starts[0]
    raise AssertionError(code)


@pytest.mark.parametrize("text,lang,code", _CASES)
def test_every_holiday_in_country_gives_next_holiday(text, lang, code):
    got = extract_event(text, lang, _ANCHOR)
    assert got is not None
    assert got.recurrence == JurisdictionHolidays(code)
    assert got.span.start == _next_holiday_start(code)
