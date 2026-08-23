"""Serbian shares Croatian's "mesec DANA" idiom: the trailing genitive-plural
"dana"/"дана" ("of days") that closes a month count is emphatic filler, not
a genuine extra day. "za mesec dana" ("in a month") landed one day past "za
mesec" ("in a month") through the same mixed-grain compound-offset fold
this fix guards in ``anchored.py`` (shared by every locale). "za tri dana"
is unaffected: "dana" there is the PRIMARY relative_offset match's own UNIT
with an explicit count, never reaching the trailing-chunk scan.

Expected values are independently hand-computed against the anchor.
"""
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start, parse


def test_month_future_dana_matches_bare_month_latin():
    assert start("za mesec dana") == ad(ANCHOR + relativedelta(months=1))
    assert start("za mesec dana") == start("za mesec")


def test_month_future_dana_matches_bare_month_cyrillic():
    assert start("за месец дана") == ad(ANCHOR + relativedelta(months=1))


def test_month_future_dana_fully_consumed():
    r = parse("za mesec dana")
    assert r is not None
    assert r[0].start == ad(ANCHOR + relativedelta(months=1))
    assert r.remainder == ""


def test_counted_days_control_unaffected():
    assert start("za tri dana") == ad(ANCHOR + timedelta(days=3))
    assert start("за три дана") == ad(ANCHOR + timedelta(days=3))


def test_weekday_dana_veto_unaffected():
    # the pre-existing "weekday immediately followed by a bare day-unit
    # word" veto (matcher.py) must keep refusing rather than surface a
    # lone-weekday sub-reading with "dana" silently dropped.
    assert parse("nedelju dana") is None
