"""R120, German: "die woche nach/vor <Ereignis>" resolves as a WEEK span,
not a single day -- mirrors
``test_nl_corpus_en/test_nl_r120_week_after_event.py``.

The bare, DEFINITE "die woche" (no explicit count) names the calendar week
itself, same grain as "the week of X"; a counted "2 wochen" or the bare
indefinite "eine woche"/"1 woche" stays a plain arithmetic point offset,
unaffected.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, span, start_end


def ad(d):
    return AstroDate(d.year, d.month, d.day)

OSTERN = date(2018, 4, 1)          # Sonntag
WEIHNACHTEN = date(2017, 12, 25)   # Montag


def _week_of(d):
    back = (d.weekday() - 0) % 7
    s = d - timedelta(days=back)
    return s, s + timedelta(days=7)


@pytest.mark.parametrize("text,shifted", [
    ("die woche nach ostern", OSTERN + timedelta(days=7)),
    ("die woche vor weihnachten", WEIHNACHTEN - timedelta(days=7)),
])
def test_die_woche_nach_vor_is_week_wide(text, shifted):
    exp_start, exp_end = _week_of(shifted)
    s, e = start_end(text)
    assert (s, e) == (ad(exp_start), ad(exp_end))
    assert span(text).width == timedelta(days=7)


# -- CONTROL: counted/indefinite "woche" stays a single-day point ---------

@pytest.mark.parametrize("text,expected", [
    ("2 wochen nach ostern", OSTERN + timedelta(days=14)),
    ("1 woche nach ostern", OSTERN + timedelta(days=7)),
])
def test_counted_woche_stays_a_point(text, expected):
    s, e = start_end(text)
    assert s == ad(expected)
    assert e == ad(expected + timedelta(days=1))
    assert span(text).width == timedelta(days=1)


# -- CONTROL: "der tag nach/vor X" is unaffected ---------------------------

@pytest.mark.parametrize("text,expected", [
    ("der tag nach ostern", OSTERN + timedelta(days=1)),
    ("der tag vor weihnachten", WEIHNACHTEN - timedelta(days=1)),
])
def test_der_tag_nach_vor_stays_a_point(text, expected):
    s, e = start_end(text)
    assert s == ad(expected)
    assert span(text).width == timedelta(days=1)
