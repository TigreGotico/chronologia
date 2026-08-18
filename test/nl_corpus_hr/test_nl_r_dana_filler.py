"""Croatian "godinu/mjesec/tjedan DANA" idiom -- the trailing genitive-plural
"dana" ("of days") that closes a year/month/week count is emphatic filler,
not a genuine extra day. "za godinu dana" ("in a year") landed one day past
"za godinu" ("in a year") because the mixed-grain compound-offset fold
(``apply_compound_offset``/``_compound_unit_at``) read the bare, uncounted
"dana" as an implied "+1 day" chunk and summed it onto the year. A real
counted-days offset ("za tri dana") is unaffected: "dana" there is the
PRIMARY relative_offset match's own UNIT, carrying the explicit "tri", and
never reaches the trailing-chunk scan this fix guards.

Expected values are independently hand-computed against the anchor
(dateutil.relativedelta for calendar-grain steps, timedelta for fixed-width
ones) -- never read back from the parser.
"""
from datetime import timedelta

from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start, parse


def test_year_future_dana_matches_bare_year():
    assert start("za godinu dana") == ad(ANCHOR + relativedelta(years=1))
    assert start("za godinu dana") == start("za godinu")


def test_year_past_dana_matches_bare_year():
    assert start("prije godinu dana") == ad(ANCHOR - relativedelta(years=1))
    assert start("prije godinu dana") == start("prije godinu")


def test_month_future_dana_matches_bare_month():
    assert start("za mjesec dana") == ad(ANCHOR + relativedelta(months=1))
    assert start("za mjesec dana") == start("za mjesec")


def test_week_future_dana_matches_bare_week():
    assert start("za tjedan dana") == ad(ANCHOR + timedelta(weeks=1))
    assert start("za tjedan dana") == start("za tjedan")


def test_year_future_dana_fully_consumed():
    r = parse("za godinu dana")
    assert r is not None
    assert r[0].start == ad(ANCHOR + relativedelta(years=1))
    assert r.remainder == ""


def test_counted_days_control_unaffected():
    # "dana" here is the primary match's own UNIT, carrying an explicit
    # count -- three genuine days, not the filler idiom.
    assert start("za tri dana") == ad(ANCHOR + timedelta(days=3))


def test_bare_day_offset_control_unaffected():
    # A genuine bare "+1 day" offset uses the nominative "dan", never the
    # genitive-plural "dana" this fix treats as filler.
    assert start("za dan") == ad(ANCHOR + timedelta(days=1))
