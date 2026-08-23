"""The Esperanto numeral fold (:mod:`chronologia.extract.numfold_esperanto`),
exercised through the "antaŭ N tagoj" (N days ago) relative-offset frame so
every value is checked against real date arithmetic, never the fold's own
output.

Cardinals 0..10 (nul, unu, du, tri, kvar, kvin, ses, sep, ok, naŭ, dek), the
fused tens (dudek=20 .. naŭdek=90), cent (100) and mil (1000) compose by
writing words left to right, most-significant first: "dek du" = 12 (ten +
two), "dudek du" = 22, "cent tri" = 103, "mil dudek kvin" = 1025. Source:
en.wikipedia.org, "Esperanto grammar".
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, start


@pytest.mark.parametrize("text,n", [
    ("antaŭ unu tago", 1),
    ("antaŭ du tagoj", 2),
    ("antaŭ naŭ tagoj", 9),
    ("antaŭ dek tagoj", 10),
    ("antaŭ dek unu tagoj", 11),
    ("antaŭ dek du tagoj", 12),
    ("antaŭ dek naŭ tagoj", 19),
    ("antaŭ dudek tagoj", 20),
    ("antaŭ dudek unu tagoj", 21),
    ("antaŭ tridek tagoj", 30),
    ("antaŭ kvardek tagoj", 40),
    ("antaŭ kvindek tagoj", 50),
    ("antaŭ sesdek tagoj", 60),
    ("antaŭ sepdek tagoj", 70),
    ("antaŭ okdek tagoj", 80),
    ("antaŭ naŭdek naŭ tagoj", 99),
    ("antaŭ cent tagoj", 100),
    ("antaŭ cent unu tagoj", 101),
    ("antaŭ cent dudek kvin tagoj", 125),
    ("antaŭ mil tagoj", 1000),
    ("antaŭ mil dudek kvin tagoj", 1025),
])
def test_cardinal_run_folds_to_the_right_value(text, n):
    assert start(text).date() == (ANCHOR - timedelta(days=n)).date()


@pytest.mark.parametrize("text,n", [
    ("post unu tago", 1), ("post dek du tagoj", 12),
    ("post naŭdek naŭ tagoj", 99),
])
def test_future_direction_uses_the_same_number_table(text, n):
    assert start(text).date() == (ANCHOR + timedelta(days=n)).date()


@pytest.mark.parametrize("text,y,m,d", [
    # the day-of-month ordinal: cardinal + regular "-a" suffix ("tri" ->
    # "tria"), compound tens staying the bare cardinal ("dudek tria" = 23rd).
    ("la unua de januaro", 2018, 1, 1),
    ("la deka de junio", 2018, 6, 10),
    ("dek tria de julio", 2017, 7, 13),
    ("dudek tria de decembro", 2017, 12, 23),
    ("tridek unua de decembro", 2017, 12, 31),
])
def test_ordinal_day_of_month(text, y, m, d):
    d0 = start(text)
    assert (d0.year, d0.month, d0.day) == (y, m, d)


@pytest.mark.parametrize("text,y,m,d", [
    ("dudek tria de decembro", 2017, 12, 23),
])
def test_compound_day_keeps_its_tens(text, y, m, d):
    """The tens element must survive: reading the third when the speaker
    said the twenty-third is the silent-wrong this test exists to prevent."""
    d0 = start(text)
    assert (d0.year, d0.month, d0.day) == (y, m, d)
    assert d0.day != 3
