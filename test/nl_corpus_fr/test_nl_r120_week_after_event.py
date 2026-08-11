"""R120, French: "la semaine après/avant <événement>" resolves as a WEEK
span, not a single day -- mirrors
``test_nl_corpus_en/test_nl_r120_week_after_event.py``.

The bare, DEFINITE "la semaine" (no explicit count) names the calendar week
itself, same grain as "the week of X"; a counted/indefinite "une semaine"
or "2 semaines" stays a plain arithmetic point offset, unaffected.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, span, start_end


def ad(d):
    return AstroDate(d.year, d.month, d.day)

PAQUES = date(2018, 4, 1)      # dimanche
NOEL = date(2017, 12, 25)      # lundi


def _week_of(d):
    back = (d.weekday() - 0) % 7
    s = d - timedelta(days=back)
    return s, s + timedelta(days=7)


@pytest.mark.parametrize("text,shifted", [
    ("la semaine après pâques", PAQUES + timedelta(days=7)),
    ("la semaine avant noël", NOEL - timedelta(days=7)),
])
def test_la_semaine_apres_avant_is_week_wide(text, shifted):
    exp_start, exp_end = _week_of(shifted)
    s, e = start_end(text)
    assert (s, e) == (ad(exp_start), ad(exp_end))
    assert span(text).width == timedelta(days=7)


# -- CONTROL: counted/indefinite "semaine" stays a single-day point -------

@pytest.mark.parametrize("text,expected", [
    ("deux semaines après pâques", PAQUES + timedelta(days=14)),
    ("une semaine après pâques", PAQUES + timedelta(days=7)),
    ("1 semaine après pâques", PAQUES + timedelta(days=7)),
])
def test_counted_or_indefinite_semaine_stays_a_point(text, expected):
    s, e = start_end(text)
    assert s == ad(expected)
    assert e == ad(expected + timedelta(days=1))
    assert span(text).width == timedelta(days=1)


# -- CONTROL: "le jour après/avant X" is unaffected ------------------------

@pytest.mark.parametrize("text,expected", [
    ("le jour après pâques", PAQUES + timedelta(days=1)),
    ("le jour avant noël", NOEL - timedelta(days=1)),
])
def test_le_jour_apres_avant_stays_a_point(text, expected):
    s, e = start_end(text)
    assert s == ad(expected)
    assert span(text).width == timedelta(days=1)
