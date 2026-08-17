"""Croatian bare-unit relative offsets -- the implied-quantity-one reading.

"za tjedan" ("in a week") and "tjedan prije" ("a week ago") carry no
numeral; Croatian has no article to fold to 1 the way English "a" does,
so the bare unit itself must read as quantity one. The USG slot (schema
"singular_units", from unit1_<unit>.voc, already shipped for hr) supplies
only the noun's singular case surfaces, so the fold applies exactly when
the surface is grammatically singular -- a bare PLURAL unit ("za
tjedne") is not an offset at all and stays a hard non-match. unit1_year
shipped with "godine", the genitive singular of "godina" -- but "godine"
is also the nominative plural, so it let "za godine" ("in years") match
as one year; that shipped syncretic form is removed here, alongside the
grammar-order fix, since it is the same silently-wrong class of bug.
Values mirror the numeral-form golds in test_nl_relative.py (n=1)
against the same Tuesday 2017-06-27 13:04 anchor; a bare offset spans
one unit wide from its own directional endpoint, same as "za 1
<unit>"/"1 <unit> prije".
"""
from datetime import timedelta

from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start, span, nomatch


def test_day_future():
    assert start("za dan") == ad(ANCHOR + timedelta(days=1))


def test_day_past():
    assert start("dan prije") == ad(ANCHOR - timedelta(days=1))


def test_week_future():
    assert start("za tjedan") == ad(ANCHOR + timedelta(weeks=1))


def test_week_past():
    assert start("tjedan prije") == ad(ANCHOR - timedelta(weeks=1))


def test_month_future():
    assert start("za mjesec") == ad(ANCHOR + relativedelta(months=1))


def test_month_past():
    assert start("mjesec prije") == ad(ANCHOR - relativedelta(months=1))


def test_year_future():
    assert start("za godinu") == ad(ANCHOR + relativedelta(years=1))


def test_year_past():
    assert start("godinu prije") == ad(ANCHOR - relativedelta(years=1))


def test_hour_future():
    assert start("za sat") == ad(ANCHOR + timedelta(hours=1))


def test_hour_past():
    assert start("sat prije") == ad(ANCHOR - timedelta(hours=1))


def test_bare_offset_is_unit_wide():
    assert span("za tjedan").width == timedelta(weeks=1)
    assert span("dan prije").width == timedelta(days=1)


# numeral-form control: the pre-existing NUM UNIT MARKER / MARKER NUM UNIT
# orders must keep working unchanged.
def test_numeral_form_unaffected():
    assert start("za 3 dana") == ad(ANCHOR + timedelta(days=3))
    assert start("3 dana prije") == ad(ANCHOR - timedelta(days=3))


# a bare PLURAL unit is not an implied one -- USG only ever supplies
# singular surfaces, so these stay hard non-matches. "za godine" pins the
# genitive/nominative-plural "godine" syncretism fix in unit1_year.voc.
def test_bare_plural_is_not_an_offset():
    nomatch("za dane")
    nomatch("za tjedne")
    nomatch("za godine")
