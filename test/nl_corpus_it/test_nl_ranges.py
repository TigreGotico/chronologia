"""Italian ranges: "da A a B" / "dal A al B" / "tra A e B", plus the scoped
century 100-year span."""
from datetime import timedelta

import pytest

from ._corpus import start_end, AstroDate


@pytest.mark.parametrize("text,s,e", [
    ("da giugno ad agosto", AstroDate(2017, 6, 1), AstroDate(2017, 9, 1)),
    ("dal 5 luglio al 10 agosto", AstroDate(2017, 7, 5), AstroDate(2017, 8, 11)),
    ("tra luglio e settembre", AstroDate(2017, 7, 1), AstroDate(2017, 10, 1)),
    ("dal 2018 al 2020", AstroDate(2018, 1, 1), AstroDate(2021, 1, 1)),
    ("dal 1 luglio al 5 luglio", AstroDate(2017, 7, 1), AstroDate(2017, 7, 6)),
])
def test_range(text, s, e):
    assert start_end(text) == (s, e)


def test_weekday_range():
    s, e = start_end("da lunedì a venerdì")
    assert e - s == timedelta(days=5)


def test_century_span():
    s, e = start_end("il 20 secolo")
    assert (s, e) == (AstroDate(1900, 1, 1), AstroDate(2000, 1, 1))


# -- the shared-month range: the month named ONCE for the pair ---------------
# Naming the month once is the default written form of a date range in the
# Romance languages (RAE, Ortografia de la lengua espanola 5.2.5.1, and its
# counterparts), and the endpoint carrying only the bare day used to be thrown
# away -- the span collapsed onto the dated endpoint alone.  The bare day is
# read through its partner's own words, so both forms now agree.

@pytest.mark.parametrize("text", [
    "dal 5 al 12 giugno",
    "dal 5 giugno al 12 giugno",
    "da 5 a 12 giugno",
])
def test_shared_month_range_reads_both_days(text):
    ss, ee = start_end(text)
    assert ss == AstroDate(2018, 6, 5) and ee == AstroDate(2018, 6, 13)


def test_shared_month_range_crosses_the_year():
    ss, ee = start_end("dal 28 dicembre al 3 gennaio")
    assert ss == AstroDate(2017, 12, 28) and ee == AstroDate(2018, 1, 4)


def test_alle_without_a_from_lead_is_not_a_range():
    ss, ee = start_end("il concerto è alle tre")
    assert ss == AstroDate(2017, 6, 28, 3, 0)
    assert ee == AstroDate(2017, 6, 28, 3, 1)


@pytest.mark.parametrize("text", ["dal al", "dal 5 al", "dal pane al vino"])
def test_dal_al_garbage_never_raises(text):
    from ._corpus import parse
    parse(text)


def test_shared_month_range_after_a_subject():
    # "dal" is nobody's date particle, so the lead is trusted mid-utterance
    # and the subject goes to the remainder where it belongs
    ss, ee = start_end("il congresso si tiene dal 5 al 12 giugno")
    assert ss == AstroDate(2018, 6, 5) and ee == AstroDate(2018, 6, 13)
