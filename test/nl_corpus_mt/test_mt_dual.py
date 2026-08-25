"""The dual: a form meaning exactly two, and the units that do not have one.

Five Maltese time nouns inflect for a dual in ``-ejn`` -- jumejn, ġimagħtejn,
sagħtejn, xahrejn, sentejn -- and the count lives inside the noun, with no
numeral anywhere in the phrase.  A reader that knows only singular and plural
sees no number at all in "jumejn ilu" and answers with yesterday, or with
nothing.

Minute, second and century have no dual and none is invented for them: they
are Romance loans (minuta, sekonda, seklu) that never took Semitic dual
morphology, so "two minutes ago" is spelled with an ordinary numeral.  The
refusals below pin that as a fact of the language rather than a gap.

Gold is arithmetic on the anchor -- exactly two of the unit named -- and the
cross-checks assert the dual and the numeral spelling of the same count land
on the same span.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, parse, remainder, span, start_end


@pytest.mark.parametrize("text,delta,width", [
    ("jumejn ilu", timedelta(days=2), timedelta(days=1)),
    ("ġimagħtejn ilu", timedelta(weeks=2), timedelta(weeks=1)),
    ("sagħtejn ilu", timedelta(hours=2), timedelta(hours=1)),
])
def test_the_dual_carries_its_own_count(text, delta, width):
    back = ANCHOR - delta
    assert start_end(text) == (ad(back), ad(back + width))


@pytest.mark.parametrize("text,months", [
    ("xahrejn ilu", 2),
])
def test_the_month_dual(text, months):
    back = ANCHOR - relativedelta(months=months)
    assert start_end(text) == (ad(back), ad(back + relativedelta(months=1)))


@pytest.mark.parametrize("text,years", [
    ("sentejn ilu", 2),
])
def test_the_year_dual(text, years):
    back = ANCHOR - relativedelta(years=years)
    assert start_end(text) == (ad(back), ad(back + relativedelta(years=1)))


def test_the_dual_consumes_the_whole_phrase():
    for text in ("jumejn ilu", "sentejn ilu", "sagħtejn ilu"):
        assert remainder(text) == ""


# -- the dual and the numeral spelling name the same count ------------------
# Maltese tolerates both "jumejn" and "żewġ ġranet" for two days; neither is
# preferred here, and both must read as two.

@pytest.mark.parametrize("dual,counted", [
    ("jumejn ilu", "żewġ ġranet ilu"),
    ("sentejn ilu", "żewġ snin ilu"),
    ("xahrejn ilu", "żewġ xhur ilu"),
    ("ġimagħtejn ilu", "żewġ ġimgħat ilu"),
    ("sagħtejn ilu", "żewġ sigħat ilu"),
])
def test_dual_and_numeral_spellings_agree(dual, counted):
    assert span(dual).start == span(counted).start


def test_the_dual_reads_forward_as_well_as_back():
    forward = ANCHOR + timedelta(days=2)
    assert start_end("fi żmien jumejn oħra") == (
        ad(forward), ad(forward + timedelta(days=1)))


# -- the units with NO dual -------------------------------------------------

@pytest.mark.parametrize("invented", [
    "minutejn ilu", "sekondejn ilu", "seklejn ilu",
])
def test_minute_second_and_century_refuse_an_invented_dual(invented):
    # These forms do not exist in Maltese.  Nothing may parse them, and in
    # particular nothing may read them as "two <unit> ago".
    assert parse(invented) is None


@pytest.mark.parametrize("text,delta,width", [
    ("żewġ minuti ilu", timedelta(minutes=2), timedelta(minutes=1)),
    ("żewġ sekondi ilu", timedelta(seconds=2), timedelta(seconds=1)),
])
def test_the_dual_less_units_count_with_a_numeral(text, delta, width):
    back = ANCHOR - delta
    assert start_end(text) == (ad(back), ad(back + width))


def test_two_centuries_counts_with_a_numeral():
    back = ANCHOR - relativedelta(years=200)
    assert start_end("żewġ sekli ilu") == (
        ad(back), ad(back + relativedelta(years=100)))
