"""explain() reports the parse extract_timespan makes, including its
pre-selection veto.

Danish, Swedish and Norwegian name Christmas "jul" and the month "juli".
Bokmålsordboka, "jul": "minnehøytid for Jesu fødsel 25. desember".
Swedish Wiktionary, "jul": "(huvudsakligen kristen) högtid man firar den
25 december", and separately "förkortning för juli" -- the written
abbreviation, which binds a day or a year in a date ("15. jul. 2026",
"jul 2026").  Danish Wiktionary, "jul" (https://da.wiktionary.org/wiki/jul):
"En serie af kristne helligdage, begyndede den 24. december hvert år
(lille juleaften)."  ovos-date-parser reads holidays through explain(), so
a trace that let the month win made "jul" answer nothing there while
extract_timespan answered Christmas.

The veto is the whole pre-selection veto of extract_timespan, so explain()
also drops the readings it vetoes outside "jul".  "the new year" is one:
extract_timespan reads it as the coming year as a period, not as 1 January,
and answers nothing for it.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan
from chronologia.extract import explain, load_lang_spec

ANCHOR = datetime(2026, 9, 27)


def _winner(text, lang):
    trace = explain(text, load_lang_spec(lang), ANCHOR)
    assert len(trace.winners) == 1, trace.report()
    return trace, trace.winners[0]


@pytest.mark.parametrize("lang", ["da", "sv", "nb", "nn"])
def test_bare_jul_wins_as_christmas(lang):
    trace, won = _winner("jul", lang)
    assert won.match.construction == "holiday_ref", trace.report()
    start = won.resolution.value.start
    assert (start.year, start.month, start.day) == (2026, 12, 25)


@pytest.mark.parametrize("text,lang", [
    ("hvor mange dage til jul", "da"),
    ("til jul", "da"),
    ("till jul", "sv"),
])
def test_jul_after_a_preposition_is_christmas(text, lang):
    trace, won = _winner(text, lang)
    assert won.match.construction == "holiday_ref", trace.report()
    start = won.resolution.value.start
    assert (start.year, start.month, start.day) == (2026, 12, 25)


@pytest.mark.parametrize("lang", ["da", "sv", "nb", "nn"])
def test_vetoed_month_is_reported_as_vetoed(lang):
    trace, _ = _winner("jul", lang)
    lost = [l for l in trace.losers if l.match.construction == "calendar_date"]
    assert lost and lost[0].reason.startswith("vetoed"), trace.report()


@pytest.mark.parametrize("text,lang", [
    ("juli", "da"), ("juli", "sv"), ("juli", "nb"),
    ("jul 2026", "da"), ("jul 2026", "sv"), ("jul 2026", "nb"),
])
def test_month_readings_unchanged(text, lang):
    trace, won = _winner(text, lang)
    assert won.match.construction == "calendar_date", trace.report()
    start = won.resolution.value.start
    assert start.month == 7


@pytest.mark.parametrize("lang", ["da", "nb"])
def test_written_day_month_year_stays_july(lang):
    trace, won = _winner("15. jul. 2026", lang)
    assert won.match.construction == "calendar_date", trace.report()
    start = won.resolution.value.start
    assert (start.year, start.month, start.day) == (2026, 7, 15)


@pytest.mark.parametrize("text", ["the new year", "in the new year"])
def test_the_new_year_has_no_winner_as_in_extract_timespan(text):
    trace = explain(text, load_lang_spec("en"), ANCHOR)
    assert trace.winners == (), trace.report()
    lost = [l for l in trace.losers
            if l.match.construction == "new_year_ref"]
    assert lost and lost[0].reason.startswith("vetoed"), trace.report()
    assert extract_timespan(text, "en", ANCHOR) is None


def test_bare_new_year_is_still_the_first_of_january():
    trace, won = _winner("new year", "en")
    assert won.match.construction == "new_year_ref", trace.report()
    start = won.resolution.value.start
    assert (start.year, start.month, start.day) == (2027, 1, 1)
