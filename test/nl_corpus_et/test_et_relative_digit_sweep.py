"""Estonian digit-numeral relative offsets, both directions.

``N UNIT pärast`` (in / future) and ``N UNIT tagasi`` (ago / past) with a
leading Arabic numeral sweep across days, weeks, months, years, hours and
minutes.  The span carries the width of a single unit.  Gold is independent
``relativedelta`` arithmetic against the mission anchor.
"""
import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start_end

# unit surface (partitive, the form that follows a numeral) -> delta
UNITS = {
    "päeva": relativedelta(days=1),
    "nädalat": relativedelta(weeks=1),
    "kuud": relativedelta(months=1),
    "aastat": relativedelta(years=1),
    "tundi": relativedelta(hours=1),
    "minutit": relativedelta(minutes=1),
}
NS = [2, 5, 8]


def _future_cases():
    for unit in UNITS:
        for n in NS:
            yield (f"{n} {unit} pärast", n, unit)


def _past_cases():
    for unit in UNITS:
        for n in NS:
            yield (f"{n} {unit} tagasi", n, unit)


@pytest.mark.parametrize("text,n,unit", list(_future_cases()))
def test_future(text, n, unit):
    d = UNITS[unit]
    s, e = start_end(text)
    assert s == ad(ANCHOR + n * d)
    assert e == ad(ANCHOR + (n + 1) * d)


@pytest.mark.parametrize("text,n,unit", list(_past_cases()))
def test_past(text, n, unit):
    d = UNITS[unit]
    s, e = start_end(text)
    assert s == ad(ANCHOR - n * d)
    assert e == ad(ANCHOR - (n - 1) * d)
