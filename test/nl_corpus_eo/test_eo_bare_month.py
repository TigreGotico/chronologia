"""A bare Esperanto month name, with or without a trailing year.

"junio" ("June") names the month with no day attached at all -- unlike the
"la ORD de MONTH" shape in test_nl_dates.py, there is no ordinal here for
"de" to link. Esperanto's month nouns are invariant (the same word names the
month whether it is the subject, object, or a bare adverbial-of-time), so
"junio" alone is exactly as legitimate a calendar_date reading as "januaro"
paired with a day is -- the same reading every other Romance-order locale
already gives its own bare month (see chronologia/extract/compiler.py's
BASE_GRAMMAR comment on calendar_date staying per-locale). A trailing bare
YEAR composes onto the same reading ("junio 2020" = June 2020) rather than
being swallowed whole by year_ref and stranding the month, since MONTH YEAR?
out-spans a bare year_ref on the same tokens.

The regular temporal accusative -n ("junion") names the same month with the
same reading; unlike WEEKDAY (test_eo_weekday_case.py), MONTH carries no
nominative/accusative recurrence split to preserve, so both cases are wired
to the identical calendar_date match.
"""
import pytest

from ._corpus import remainder, start


@pytest.mark.parametrize("text", ["junio", "junion"])
def test_bare_month_resolves_forward_from_the_anchor(text):
    """The anchor (2017-06-27) sits INSIDE June: unlike a day-of-month
    reference, a bare month is not yet past just because part of it has
    elapsed, so it resolves to the anchor's own June, not next year's."""
    got = start(text)
    assert (got.year, got.month, got.day) == (2017, 6, 1)


@pytest.mark.parametrize("text", ["junio", "junion"])
def test_bare_month_consumes_everything(text):
    assert remainder(text) == ""


@pytest.mark.parametrize("text,m", [
    ("januaro", 1), ("marto", 3), ("decembro", 12),
])
def test_every_bare_month_resolves(text, m):
    got = start(text)
    assert got.month == m


@pytest.mark.parametrize("text", ["junio 2020", "junion 2020"])
def test_month_plus_year_resolves_that_year_not_the_whole_year(text):
    got = start(text)
    assert (got.year, got.month, got.day) == (2020, 6, 1)


@pytest.mark.parametrize("text", ["junio 2020", "junion 2020"])
def test_month_plus_year_consumes_everything(text):
    assert remainder(text) == ""


def test_month_plus_year_span_is_the_whole_month_not_the_whole_year():
    from ._corpus import span
    got = span("junio 2020")
    assert (got.end - got.start).days == 30
