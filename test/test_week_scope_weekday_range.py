"""A week scope after a weekday range ("from wednesday to thursday next week") scopes both ends (#1442)."""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_timespan

_ANCHORS = (datetime(2017, 6, 27, 13, 4), datetime(2026, 11, 26, 9, 30))


def _day(anchor, week, weekday):
    """Midnight of ``weekday`` (0 = Monday) in the week ``week`` weeks from the anchor's."""
    monday = anchor.date() - timedelta(days=anchor.weekday())
    d = monday + timedelta(weeks=week, days=weekday)
    return datetime(d.year, d.month, d.day)


# text, lang, (week, weekday) of the start, (week, weekday) of the last day
_ROWS = [
    ("from wednesday to thursday next week", "en", (1, 2), (1, 3)),
    ("from monday to friday next week", "en", (1, 0), (1, 4)),
    ("from tuesday to wednesday next week", "en", (1, 1), (1, 2)),
    ("from wednesday to thursday last week", "en", (-1, 2), (-1, 3)),
    ("from friday to monday next week", "en", (1, 4), (2, 0)),
    ("from wednesday this week to thursday next week", "en", (0, 2), (1, 3)),
    ("von Mittwoch bis Donnerstag nächste Woche", "de", (1, 2), (1, 3)),
    ("de miércoles a jueves la próxima semana", "es", (1, 2), (1, 3)),
    ("de quarta a quinta da próxima semana", "pt", (1, 2), (1, 3)),
    ("de segunda-feira a quinta-feira da próxima semana", "pt", (1, 0), (1, 3)),
    ("du mercredi au jeudi la semaine prochaine", "fr", (1, 2), (1, 3)),
    ("da mercoledì a giovedì la prossima settimana", "it", (1, 2), (1, 3)),
    ("van woensdag tot donderdag volgende week", "nl", (1, 2), (1, 3)),
]


@pytest.mark.parametrize("anchor", _ANCHORS)
@pytest.mark.parametrize("text,lang,first,last", _ROWS)
def test_week_scope_reaches_both_ends(text, lang, first, last, anchor):
    got = extract_timespan(text, lang, anchor)
    assert got is not None
    assert (got.span.start, got.span.end) == (
        _day(anchor, *first), _day(anchor, *last) + timedelta(days=1))


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="https://github.com/TigreGotico/chronologia/issues/1452")
def test_leading_week_scope_reaches_both_ends():
    anchor = _ANCHORS[0]
    got = extract_timespan("next week from wednesday to thursday", "en", anchor)
    assert (got.span.start, got.span.end) == (_day(anchor, 1, 2), _day(anchor, 1, 4))
