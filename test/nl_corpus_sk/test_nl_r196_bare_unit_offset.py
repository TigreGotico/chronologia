"""Slovak bare-unit relative offsets -- the implied-quantity-one reading.

"za deň" ("in a day") and "pred dňom" ("a day ago") carry no numeral;
Slovak has no article to fold to 1 the way English "a" does, so the bare
unit itself must read as quantity one. The USG slot (schema
"singular_units", from unit1_<unit>.voc, already shipped for sk) supplies
only the noun's singular case surfaces, so the fold applies exactly when
the surface is grammatically singular -- a bare PLURAL unit ("za
týždne") is not an offset at all and stays a hard non-match. Values
mirror the numeral-form golds in test_nl_relative.py (n=1) against the
same Tuesday 2017-06-27 13:04 anchor; a bare offset spans one unit wide
from its own directional endpoint, same as "za 1 <unit>"/"pred 1
<unit>-om".

The instrumental singular that "pred" governs is missing from the week
and month unit vocabulary ("týždňom", "mesiacom" are absent from
unit_week.voc / unit_month.voc, unlike "dňom"/"rokom"/"hodinou"), so
"pred týždňom" and "pred mesiacom" stay unmatched -- a vocabulary gap,
not a grammar-order gap, and out of scope here pending a native check.
"""
from datetime import timedelta

from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start, span, parse, nomatch


def test_day_future():
    assert start("za deň") == ad(ANCHOR + timedelta(days=1))


def test_day_past():
    assert start("pred dňom") == ad(ANCHOR - timedelta(days=1))


def test_week_future():
    assert start("o týždeň") == ad(ANCHOR + timedelta(weeks=1))


def test_month_future():
    assert start("za mesiac") == ad(ANCHOR + relativedelta(months=1))


def test_year_future():
    assert start("za rok") == ad(ANCHOR + relativedelta(years=1))


def test_year_past():
    assert start("pred rokom") == ad(ANCHOR - relativedelta(years=1))


def test_hour_future():
    assert start("za hodinu") == ad(ANCHOR + timedelta(hours=1))


def test_hour_past():
    assert start("pred hodinou") == ad(ANCHOR - timedelta(hours=1))


def test_bare_offset_is_unit_wide():
    assert span("o týždeň").width == timedelta(weeks=1)
    assert span("pred dňom").width == timedelta(days=1)


# vocabulary gap, not a grammar-order gap: "pred týždňom"/"pred mesiacom"
# need the instrumental singular noun form, absent from the unit vocab.
def test_week_month_past_instrumental_is_a_vocab_gap():
    assert parse("pred týždňom") is None
    assert parse("pred mesiacom") is None


# numeral-form control: the pre-existing NUM UNIT MARKER / MARKER NUM UNIT
# orders must keep working unchanged.
def test_numeral_form_unaffected():
    assert start("o 3 dni") == ad(ANCHOR + timedelta(days=3))
    assert start("pred 3 dňami") == ad(ANCHOR - timedelta(days=3))


# clock-collision control: "o 9 hodine" ("at 9 o'clock") uses the same
# "o" marker for an unrelated clock-time construction; the new bare-unit
# orders must not steal it.
def test_o_clock_collision_unaffected():
    r = parse("o 9 hodine")
    assert r is not None
    assert r[0].start.hour == 9


# a bare PLURAL unit is not an implied one -- USG only ever supplies
# singular surfaces, so these stay hard non-matches.
def test_bare_plural_is_not_an_offset():
    nomatch("za dni")
    nomatch("za týždne")
    nomatch("za roky")
