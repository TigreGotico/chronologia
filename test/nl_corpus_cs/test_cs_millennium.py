# -*- coding: utf-8 -*-
"""The millennium, alongside the century it is built like.

``století`` and ``tisíciletí`` are both neuter -í nouns whose nominative
singular and plural are spelled alike, and a scoped ordinal is grammatically
singular: a scope noun that cannot be told apart from its own plural reads as
a bare count ("two millennia") and refuses.  The locale settles that by
listing the singular, which is why ``druhé tisíciletí`` names the second
millennium rather than counting two of them.

Both the spelled ordinal ("druhé") and the dotted digit ordinal ("2.") are
Czech's ordinary ways of writing it, and both are exercised.

Gold is arithmetic: the Nth millennium opens in year (N-1)*1000 and is 1000
years wide, the Nth century in (N-1)*100 and 100 wide, both half-open.  The
first period is the exception every calendar has -- there is no year zero, so
it opens in year 1 and closes a whole period later, the same shape English
"1st century"/"1st millennium" already resolve to.
"""
import pytest

from ._corpus import nomatch, parse, span


@pytest.mark.parametrize("text,n", [
    ("druhé tisíciletí", 2),
    ("2. tisíciletí", 2),
    ("třetí tisíciletí", 3),
])
def test_the_millennium_is_a_thousand_years_wide(text, n):
    s = span(text)
    assert (s.start.year, s.end.year) == ((n - 1) * 1000, n * 1000)
    assert parse(text)[1] == ""


def test_the_first_millennium_opens_in_year_one():
    s = span("první tisíciletí")
    assert (s.start.year, s.end.year) == (1, 1001)
    assert parse("první tisíciletí")[1] == ""


@pytest.mark.parametrize("text,n", [
    ("20. století", 20),
    ("druhé století", 2),
])
def test_the_century_sibling_is_a_hundred(text, n):
    s = span(text)
    assert (s.start.year, s.end.year) == ((n - 1) * 100, n * 100)
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text", ["tisíciletí", "století"])
def test_a_bare_scope_noun_names_no_period(text):
    """No number, no period -- the noun alone says only what kind of span was
    meant, never which one."""
    nomatch(text)
