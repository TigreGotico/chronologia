"""Bulgarian bare-unit relative offsets -- the implied-quantity-one reading.

"след седмица" ("in a week") and "преди седмица" ("a week ago") carry no
numeral; Bulgarian has no article to fold to 1 the way English "a" does,
so the bare unit itself must read as quantity one. The USG slot (schema
"singular_units", from unit1_<unit>.voc) supplies only the noun's
singular surfaces -- indefinite and definite, since Bulgarian marks
number by ending rather than case -- so the fold applies exactly when
the surface is grammatically singular; a bare PLURAL unit ("след
седмици") is not an offset at all and stays a hard non-match. Values
mirror the numeral-form golds in test_nl_relative.py (n=1) against the
same Tuesday 2017-06-27 13:04 anchor; a bare offset spans one unit wide
from its own directional endpoint, same as "след 1 <unit>"/"преди 1
<unit>".
"""
from datetime import timedelta

from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start, span, nomatch


def test_day_future():
    assert start("след ден") == ad(ANCHOR + timedelta(days=1))


def test_day_past():
    assert start("преди ден") == ad(ANCHOR - timedelta(days=1))


def test_week_future():
    assert start("след седмица") == ad(ANCHOR + timedelta(weeks=1))


def test_week_past():
    assert start("преди седмица") == ad(ANCHOR - timedelta(weeks=1))


def test_month_future():
    assert start("след месец") == ad(ANCHOR + relativedelta(months=1))


def test_month_past():
    assert start("преди месец") == ad(ANCHOR - relativedelta(months=1))


def test_year_future():
    assert start("след година") == ad(ANCHOR + relativedelta(years=1))


def test_year_past():
    assert start("преди година") == ad(ANCHOR - relativedelta(years=1))


def test_hour_future():
    assert start("след час") == ad(ANCHOR + timedelta(hours=1))


def test_hour_past():
    assert start("преди час") == ad(ANCHOR - timedelta(hours=1))


def test_bare_offset_is_unit_wide():
    assert span("след седмица").width == timedelta(weeks=1)
    assert span("преди ден").width == timedelta(days=1)


# numeral-form control: the pre-existing NUM UNIT MARKER / MARKER NUM UNIT
# orders must keep working unchanged.
def test_numeral_form_unaffected():
    assert start("след 3 дни") == ad(ANCHOR + timedelta(days=3))
    assert start("преди 3 дни") == ad(ANCHOR - timedelta(days=3))


# a bare PLURAL unit is not an implied one -- USG only ever supplies
# singular surfaces, so these stay hard non-matches.
def test_bare_plural_is_not_an_offset():
    nomatch("след дни")
    nomatch("след седмици")
    nomatch("след години")
