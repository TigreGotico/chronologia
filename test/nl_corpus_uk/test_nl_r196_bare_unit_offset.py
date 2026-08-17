"""Ukrainian bare-unit relative offsets -- the implied-quantity-one reading.

"через тиждень" ("in a week") and "тиждень тому" ("a week ago") carry no
numeral; Ukrainian has no article to fold to 1 the way English "a" does,
so the bare unit itself must read as quantity one. The USG slot (schema
"singular_units", from unit1_<unit>.voc) supplies only the noun's
singular case surfaces, so the fold applies exactly when the surface is
grammatically singular -- a bare PLURAL unit ("через тижні") is not an
offset at all and stays a hard non-match. Values mirror the
numeral-form golds in test_nl_relative.py (n=1) against the same
Tuesday 2017-06-27 13:04 anchor; a bare offset spans one unit wide from
its own directional endpoint, same as "через 1 <unit>"/"1 <unit> тому".
"""
from datetime import timedelta

from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start, span, nomatch


def test_day_future():
    assert start("через день") == ad(ANCHOR + timedelta(days=1))


def test_day_past():
    assert start("день тому") == ad(ANCHOR - timedelta(days=1))


def test_week_future():
    assert start("через тиждень") == ad(ANCHOR + timedelta(weeks=1))


def test_week_past():
    assert start("тиждень тому") == ad(ANCHOR - timedelta(weeks=1))


def test_month_future():
    assert start("через місяць") == ad(ANCHOR + relativedelta(months=1))


def test_month_past():
    assert start("місяць тому") == ad(ANCHOR - relativedelta(months=1))


def test_year_future():
    assert start("через рік") == ad(ANCHOR + relativedelta(years=1))


def test_year_past():
    assert start("рік тому") == ad(ANCHOR - relativedelta(years=1))


def test_hour_future():
    assert start("через годину") == ad(ANCHOR + timedelta(hours=1))


def test_hour_past():
    assert start("годину тому") == ad(ANCHOR - timedelta(hours=1))


def test_bare_offset_is_unit_wide():
    assert span("через тиждень").width == timedelta(weeks=1)
    assert span("день тому").width == timedelta(days=1)


# numeral-form control: the pre-existing NUM UNIT MARKER / MARKER NUM UNIT
# orders must keep working unchanged.
def test_numeral_form_unaffected():
    assert start("через 3 дні") == ad(ANCHOR + timedelta(days=3))
    assert start("3 дні тому") == ad(ANCHOR - timedelta(days=3))


# a bare PLURAL unit is not an implied one -- USG only ever supplies
# singular surfaces, so these stay hard non-matches.
def test_bare_plural_is_not_an_offset():
    nomatch("через тижні")
    nomatch("через роки")
    nomatch("через дні")
