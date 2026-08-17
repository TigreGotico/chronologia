"""Polish bare-unit relative offsets -- the implied-quantity-one reading.

"za tydzień" ("in a week") and "tydzień temu" ("a week ago") carry no
numeral at all; Polish has no article to fold to 1 the way English "a"
does, so the bare unit itself must read as quantity one. The USG slot
(schema "singular_units", from unit1_<unit>.voc) supplies only the
noun's singular case surfaces, so the fold applies exactly when the
surface is grammatically singular -- a bare PLURAL unit ("za tygodnie",
"za lata") is not an offset at all and stays a hard non-match; that is
"za tygodnie" in test_nl_adversarial_parity.py and test_nl_relative.py.
Values mirror the numeral-form golds in test_nl_relative.py (n=1)
against the same Tuesday 2017-06-27 13:04 anchor; a bare offset spans
one unit wide from its own directional endpoint, same as "za 1
<unit>"/"1 <unit> temu".
"""
from datetime import timedelta

from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start, span, parse, nomatch


def test_day_future():
    assert start("za dzień") == ad(ANCHOR + timedelta(days=1))


def test_day_past():
    assert start("dzień temu") == ad(ANCHOR - timedelta(days=1))


def test_week_future():
    assert start("za tydzień") == ad(ANCHOR + timedelta(weeks=1))


def test_week_past():
    assert start("tydzień temu") == ad(ANCHOR - timedelta(weeks=1))


def test_month_future():
    assert start("za miesiąc") == ad(ANCHOR + relativedelta(months=1))


def test_month_past():
    assert start("miesiąc temu") == ad(ANCHOR - relativedelta(months=1))


def test_year_future():
    assert start("za rok") == ad(ANCHOR + relativedelta(years=1))


def test_year_past():
    assert start("rok temu") == ad(ANCHOR - relativedelta(years=1))


def test_hour_future():
    assert start("za godzinę") == ad(ANCHOR + timedelta(hours=1))


def test_hour_past():
    assert start("godzinę temu") == ad(ANCHOR - timedelta(hours=1))


def test_bare_offset_is_unit_wide():
    assert span("za tydzień").width == timedelta(weeks=1)
    assert span("dzień temu").width == timedelta(days=1)


# numeral-form control: the pre-existing NUM UNIT MARKER / MARKER NUM UNIT
# orders must keep working unchanged.
def test_numeral_form_unaffected():
    assert start("za 3 dni") == ad(ANCHOR + timedelta(days=3))
    assert start("3 dni temu") == ad(ANCHOR - timedelta(days=3))


# clock-collision control: "za kwadrans dziesiąta" ("a quarter to ten") uses
# the same "za" marker for an unrelated toward-hour clock construction; the
# new bare-unit orders must not steal it.
def test_za_clock_collision_unaffected():
    r = parse("za kwadrans dziesiąta")
    assert r is not None
    assert r[0].start.hour == 9 and r[0].start.minute == 45


# a bare PLURAL unit is not an implied one -- USG only ever supplies
# singular surfaces, so these stay hard non-matches.
def test_bare_plural_is_not_an_offset():
    nomatch("za tygodnie")
    nomatch("za lata")
    nomatch("za dni")
    nomatch("za miesiące")
