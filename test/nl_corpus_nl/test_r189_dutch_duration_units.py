"""nl duration-vocabulary defects: diminutive time units, the generalized
"anderhalf"/"anderhalve" (1.5) quantifier, and "kwartier" (a quarter-hour
NOUN, distinct from the English fraction word "quarter").

Every expected timedelta is hand-derived seconds/day arithmetic, never read
back from the parser.

1. Diminutives ("-tje"/"-je") on a time-unit noun are everyday register and
   mean the plain unit: "een uurtje" == "een uur" (an hour). Dutch has no
   diminutive-only reading that changes the length -- the smallness is
   affective, not quantitative.
2. "anderhalf" (neuter agreement: uur/jaar) and "anderhalve" (common-gender
   agreement: week/dag/maand/minuut) both mean 1.5 and compose with ANY unit,
   not one fixed surface.
3. "kwartier" names a fixed quarter-hour length on its own -- unlike the
   clock fraction "kwart" ("kwart over negen") or the calendar-quarter noun
   "kwartaal", neither of which this touches.
"""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

from ._corpus import parse

LANG = "nl"


# -- 1. diminutive time units -----------------------------------------------
_DIMINUTIVE_CASES = [
    ("een uurtje", timedelta(hours=1)),
    ("twee uurtjes", timedelta(hours=2)),
    ("een minuutje", timedelta(minutes=1)),
    ("drie minuutjes", timedelta(minutes=3)),
    ("een dagje", timedelta(days=1)),
    ("een weekje", timedelta(weeks=1)),
    ("een kwartiertje", timedelta(minutes=15)),
]


@pytest.mark.parametrize("text,expected", _DIMINUTIVE_CASES)
def test_diminutive_time_unit(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse (expected a duration)"
    assert got.duration == expected
    assert got.remainder == ""


def test_diminutive_control_plain_unit_still_works():
    # the plain (non-diminutive) surface must keep working unchanged.
    got = extract_duration("een uur", LANG)
    assert got.duration == timedelta(hours=1)


def test_diminutive_negative_control_non_temporal_tje_word():
    # a "-tje" word with no time-unit stem must never fire ("biertje" is not
    # "bier" + a time unit -- it names no length at all).
    assert extract_duration("een biertje", LANG) is None


def test_diminutive_timespan_over_een_uurtje():
    # "over een uurtje" ("in an hour", diminutive) reads as the same
    # 1-hour-ahead point/span as "over een uur" -- independently derived:
    # anchor 10:00 -> [11:00, 12:00).
    from datetime import datetime

    from chronologia.astrodate import AstroDate

    anchor = datetime(2026, 8, 14, 10, 0)
    r = parse("over een uurtje", anchor)
    assert r is not None
    s = r[0]
    assert s.start == AstroDate(2026, 8, 14, 11, 0)
    assert s.end == AstroDate(2026, 8, 14, 12, 0)


# -- 2. generalized anderhalf/anderhalve (1.5) -------------------------------
_ANDERHALF_CASES = [
    ("anderhalf uur", timedelta(hours=1, minutes=30)),
    ("anderhalve dag", timedelta(days=1, hours=12)),
    # 1.5 weeks = 10.5 days = 10 days 12 hours.
    ("anderhalve week", timedelta(days=10, hours=12)),
]


@pytest.mark.parametrize("text,expected", _ANDERHALF_CASES)
def test_anderhalf_generalized(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse (expected a duration)"
    assert got.duration == expected
    assert got.remainder == ""


def test_anderhalf_calendar_unit_is_a_timespan_not_a_fixed_duration():
    # "jaar"/"maand" are calendar-ambiguous (not a fixed-width duration, same
    # as the plain "een jaar"/"een maand" control), so "anderhalf jaar" and
    # "anderhalve maand" stay outside extract_duration's fixed-width table --
    # they resolve only as an anchored timespan ("over anderhalf jaar").
    assert extract_duration("anderhalf jaar", LANG) is None
    assert extract_duration("anderhalve maand", LANG) is None
    from datetime import datetime

    anchor = datetime(2026, 8, 14, 10, 0)
    assert parse("over anderhalf jaar", anchor) is not None
    assert parse("over anderhalve maand", anchor) is not None


# -- 3. kwartier: a quarter-hour NOUN ----------------------------------------
_KWARTIER_CASES = [
    ("een kwartier", timedelta(minutes=15)),
    ("drie kwartier", timedelta(minutes=45)),
    ("een uur en een kwartier", timedelta(hours=1, minutes=15)),
]


@pytest.mark.parametrize("text,expected", _KWARTIER_CASES)
def test_kwartier_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse (expected a duration)"
    assert got.duration == expected
    assert got.remainder == ""


def test_kwartier_does_not_strand_the_hour():
    # regression pin for the compound stranding "en een kwartier": the whole
    # phrase must be consumed, not just the leading "een uur".
    got = extract_duration("een uur en een kwartier", LANG)
    assert got.remainder == ""


def test_kwartier_does_not_collide_with_clock_kwart():
    # "kwartier" (the 15-minute noun) is a different surface from the clock
    # fraction "kwart" ("kwart over/voor <hour>") -- the clock idiom must
    # keep reading as a TIME, unaffected by kwartier's new unit registration.
    from datetime import datetime

    from chronologia.astrodate import AstroDate

    anchor = datetime(2026, 8, 14, 10, 0)
    r = parse("kwart over negen", anchor)
    assert r is not None
    assert r[0].start == AstroDate(2026, 8, 15, 9, 15)

    r = parse("kwart voor negen", anchor)
    assert r is not None
    assert r[0].start == AstroDate(2026, 8, 15, 8, 45)
